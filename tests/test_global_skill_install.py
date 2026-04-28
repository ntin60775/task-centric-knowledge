from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "install_global_skill.py"


def load_module(module_name: str, script_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


install_global = load_module("task_centric_knowledge_install_global_skill", SCRIPT)


class GlobalSkillInstallTests(unittest.TestCase):
    def test_manifest_includes_required_resources_and_excludes_repo_only_artifacts(self) -> None:
        manifest_relatives = {
            path.relative_to(ROOT).as_posix()
            for path in install_global.iter_manifest_files(ROOT)
        }

        for relative in install_global.REQUIRED_RELATIVE_PATHS:
            with self.subTest(relative=relative):
                self.assertIn(relative, manifest_relatives)
        self.assertIn("assets/knowledge/tasks/_templates/task.md", manifest_relatives)
        self.assertIn("assets/knowledge/modules/_templates/module.md", manifest_relatives)
        self.assertNotIn("AGENTS.md", manifest_relatives)
        self.assertNotIn(".gitignore", manifest_relatives)
        self.assertNotIn("knowledge/README.md", manifest_relatives)
        self.assertNotIn("output/share/task-centric-knowledge-zip-context-2026-04-27.zip", manifest_relatives)
        self.assertNotIn("zip_context_ignore.md", manifest_relatives)

    def test_apply_creates_complete_live_bundle_without_transient_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            target_root = Path(tmp_dir) / "live-skill"
            plan = install_global.build_plan(ROOT, target_root)

            install_global.apply_plan(plan)
            issues, extra_target_files = install_global.verify_target(ROOT, target_root)

            self.assertEqual(issues, [])
            self.assertEqual(extra_target_files, [])
            self.assertTrue((target_root / "assets/knowledge/README.md").exists())
            self.assertTrue((target_root / "assets/knowledge/tasks/_templates/task.md").exists())
            self.assertFalse((target_root / "AGENTS.md").exists())
            self.assertFalse((target_root / ".gitignore").exists())
            self.assertFalse((target_root / "knowledge").exists())
            self.assertFalse((target_root / "output").exists())
            self.assertFalse((target_root / "zip_context_ignore.md").exists())

    def test_apply_refuses_manifest_target_symlink_before_any_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            target_root = root / "live-skill"
            target_root.mkdir()
            victim_path = root / "victim.txt"
            victim_path.write_text("DO NOT OVERWRITE\n", encoding="utf-8")
            (target_root / "SKILL.md").symlink_to(victim_path)

            plan = install_global.build_plan(ROOT, target_root)
            applied = install_global.apply_plan(plan)
            issues, _extra_target_files = install_global.verify_target(ROOT, target_root)

            skill_item = next(item for item in plan if item.relative == "SKILL.md")
            self.assertEqual(skill_item.status, "blocked-target-symlink")
            self.assertEqual(applied, [])
            self.assertEqual(victim_path.read_text(encoding="utf-8"), "DO NOT OVERWRITE\n")
            self.assertFalse((target_root / "README.md").exists())
            self.assertIn("blocked-target-symlink", "\n".join(issue.detail for issue in issues))

    def test_verify_reports_target_only_repo_artifacts_as_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            target_root = Path(tmp_dir) / "live-skill"
            install_global.apply_plan(install_global.build_plan(ROOT, target_root))
            (target_root / "zip_context_ignore.md").write_text("local artifact\n", encoding="utf-8")
            (target_root / "AGENTS.md").write_text("repo-local instructions\n", encoding="utf-8")
            (target_root / "knowledge").mkdir()
            (target_root / "knowledge/task.md").write_text("target project data\n", encoding="utf-8")

            issues, extra_target_files = install_global.verify_target(ROOT, target_root)

            self.assertEqual(issues, [])
            self.assertIn("zip_context_ignore.md", extra_target_files)
            self.assertIn("AGENTS.md", extra_target_files)
            self.assertIn("knowledge/", extra_target_files)

    def test_apply_preserves_target_only_files_for_separate_delete_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            target_root = Path(tmp_dir) / "live-skill"
            target_root.mkdir()
            target_only = target_root / "target-only-note.md"
            target_only.write_text("локальный файл live-copy\n", encoding="utf-8")

            install_global.apply_plan(install_global.build_plan(ROOT, target_root))
            issues, extra_target_files = install_global.verify_target(ROOT, target_root)

            self.assertTrue(target_only.exists())
            self.assertEqual(issues, [])
            self.assertIn("target-only-note.md", extra_target_files)

    def test_verify_detects_missing_assets_knowledge_in_live_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            target_root = Path(tmp_dir) / "live-skill"
            install_global.apply_plan(install_global.build_plan(ROOT, target_root))
            missing_asset = target_root / "assets/knowledge/README.md"
            missing_asset.unlink()

            issues, _extra_target_files = install_global.verify_target(ROOT, target_root)

            issue_relatives = {issue.relative for issue in issues}
            self.assertIn("assets/knowledge/README.md", issue_relatives)

    def test_verify_detects_user_cli_layer_not_pointing_to_live_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            target_root = tmp_root / "live-skill"
            user_bin = tmp_root / "bin"
            python_site = tmp_root / "site-packages"
            user_bin.mkdir()
            python_site.mkdir()
            install_global.apply_plan(install_global.build_plan(ROOT, target_root))
            (user_bin / "task-knowledge").write_text(
                f'#!/usr/bin/env bash\nexec "{sys.executable}" "{ROOT / "scripts/task_knowledge_cli.py"}" "$@"\n',
                encoding="utf-8",
            )
            (python_site / "task_knowledge_local.pth").write_text(str(ROOT / "scripts"), encoding="utf-8")

            issues = install_global.verify_cli_layer(target_root, user_bin=user_bin, python_site=python_site)

            details = "\n".join(issue.detail for issue in issues)
            self.assertIn("task-knowledge wrapper does not point to live skill copy", details)
            self.assertIn("task_knowledge_local.pth does not point to live skill copy", details)

    def test_verify_cli_layer_rejects_symlinked_wrapper_and_pth(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            target_root = tmp_root / "live-skill"
            user_bin = tmp_root / "bin"
            python_site = tmp_root / "site-packages"
            target_root.mkdir()
            user_bin.mkdir()
            python_site.mkdir()
            wrapper_target = tmp_root / "external-wrapper"
            pth_target = tmp_root / "external.pth"
            wrapper_target.write_text("external wrapper\n", encoding="utf-8")
            pth_target.write_text("external pth\n", encoding="utf-8")
            (user_bin / "task-knowledge").symlink_to(wrapper_target)
            (python_site / "task_knowledge_local.pth").symlink_to(pth_target)

            issues = install_global.verify_cli_layer(target_root, user_bin=user_bin, python_site=python_site)

            details = "\n".join(issue.detail for issue in issues)
            self.assertIn("wrapper is a symlink", details)
            self.assertIn("pth is a symlink", details)

    def test_user_cli_smoke_rejects_runtime_root_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            target_root = Path(tmp_dir) / "live-skill"
            source_runtime_root = str(ROOT / "scripts")
            smoke = install_global.SmokeResult(
                name="task-knowledge",
                command=["task-knowledge", "--json", "doctor"],
                returncode=0,
                ok=True,
                stdout_excerpt=json.dumps(
                    {
                        "ok": True,
                        "runtime_root": source_runtime_root,
                        "source_root": str(target_root),
                    }
                ),
                stderr_excerpt="",
            )

            validated = install_global.validate_user_cli_smoke(smoke, target_root)

            self.assertFalse(validated.ok)
            self.assertIn("expected_runtime_root", validated.stderr_excerpt)

    def test_apply_mode_can_install_user_cli_layer_from_live_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            target_root = tmp_root / "live-skill"
            user_bin = tmp_root / "bin"
            python_site = tmp_root / "site-packages"

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--mode",
                    "apply",
                    "--source-root",
                    str(ROOT),
                    "--target-root",
                    str(target_root),
                    "--project-root",
                    str(ROOT),
                    "--user-bin",
                    str(user_bin),
                    "--python-site",
                    str(python_site),
                    "--skip-smoke",
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
            self.assertTrue(payload["ok"])
            wrapper_path = user_bin / "task-knowledge"
            self.assertTrue(wrapper_path.exists())
            self.assertIn(str(target_root / "scripts/task_knowledge_cli.py"), wrapper_path.read_text(encoding="utf-8"))
            pth_path = python_site / "task_knowledge_local.pth"
            self.assertEqual(pth_path.read_text(encoding="utf-8").strip(), str(target_root / "scripts"))


if __name__ == "__main__":
    unittest.main()
