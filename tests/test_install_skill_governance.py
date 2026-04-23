from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import os
import textwrap
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
INSTALL_SCRIPT = SCRIPTS_DIR / "install_skill.py"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def load_module(module_name: str, script_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


install_module = load_module("task_centric_knowledge_install_skill_governance", INSTALL_SCRIPT)
doctor_runtime = importlib.import_module("install_skill_runtime.doctor")


SUBPROCESS_TIMEOUT_SECONDS = 30


def git(project_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(project_root), *args],
        capture_output=True,
        text=True,
        check=True,
        timeout=SUBPROCESS_TIMEOUT_SECONDS,
    )
    return completed.stdout.strip()


class InstallSkillGovernanceTests(unittest.TestCase):
    def _init_repo(self, root: Path) -> Path:
        project_root = root / "project"
        project_root.mkdir()
        git(project_root, "init")
        git(project_root, "branch", "-M", "main")
        git(project_root, "config", "user.name", "Test User")
        git(project_root, "config", "user.email", "test@example.com")
        (project_root / "README.md").write_text("repo\n", encoding="utf-8")
        git(project_root, "add", "README.md")
        git(project_root, "commit", "-m", "init")
        return project_root

    def _write_managed_agents(self, project_root: Path) -> None:
        (project_root / "AGENTS.md").write_text(
            textwrap.dedent(
                f"""\
                # AGENTS

                {install_module.BEGIN_MARKER}
                managed block
                {install_module.END_MARKER}
                """
            ),
            encoding="utf-8",
        )

    def _write_registry(self, project_root: Path) -> None:
        registry_path = project_root / "knowledge/tasks/registry.md"
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text(
            textwrap.dedent(
                """\
                # Реестр задач

                | ID | Parent ID | Статус | Приоритет | Ветка | Каталог | Краткое описание |
                |----|-----------|--------|-----------|-------|---------|------------------|
                """
            ),
            encoding="utf-8",
        )

    def _write_task_dir(self, project_root: Path) -> Path:
        task_dir = project_root / "knowledge/tasks/TASK-2026-0099-demo"
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "task.md").write_text("# task\n", encoding="utf-8")
        return task_dir

    def test_doctor_deps_keeps_publish_tooling_out_of_core_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = self._init_repo(Path(tmp_dir))
            git(project_root, "remote", "add", "origin", "git@github.com:test/example.git")
            which_map = {
                "python3": shutil.which("python3"),
                "git": shutil.which("git"),
                "gh": None,
                "glab": None,
            }
            with mock.patch.object(
                doctor_runtime,
                "_command_exists",
                side_effect=lambda command: which_map.get(command),
            ):
                payload = install_module.doctor_deps(project_root, ROOT, "generic")

            self.assertTrue(payload["ok"])
            dependencies = {item["name"]: item for item in payload["dependencies"]}
            self.assertEqual(dependencies["gh"]["status"], "missing")
            self.assertEqual(dependencies["gh"]["blocking_layer"], "publish/integration")
            self.assertEqual(dependencies["git_repository"]["status"], "ok")

    def test_doctor_deps_requires_python3_cli_in_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = self._init_repo(Path(tmp_dir))
            which_map = {
                "python3": None,
                "git": shutil.which("git"),
                "gh": None,
                "glab": None,
            }
            with mock.patch.object(
                doctor_runtime,
                "_command_exists",
                side_effect=lambda command: which_map.get(command),
            ):
                payload = install_module.doctor_deps(project_root, ROOT, "generic")

            self.assertFalse(payload["ok"])
            dependencies = {item["name"]: item for item in payload["dependencies"]}
            self.assertEqual(dependencies["python3"]["status"], "missing")
            self.assertEqual(dependencies["python3"]["blocking_layer"], "core/local mode")

    def test_doctor_deps_rejects_non_directory_knowledge_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = self._init_repo(Path(tmp_dir))
            (project_root / "knowledge").write_text("conflict\n", encoding="utf-8")

            payload = install_module.doctor_deps(project_root, ROOT, "generic")

            self.assertFalse(payload["ok"])
            knowledge_results = [item for item in payload["results"] if item["key"] == "knowledge"]
            self.assertEqual(knowledge_results[0]["status"], "error")
            dependencies = {item["name"]: item for item in payload["dependencies"]}
            self.assertEqual(dependencies["knowledge_contour"]["status"], "misconfigured")

    def test_doctor_deps_surfaces_git_timeout_without_false_non_repo_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = self._init_repo(Path(tmp_dir))
            which_map = {
                "python3": shutil.which("python3"),
                "git": shutil.which("git"),
                "gh": None,
                "glab": None,
            }
            with mock.patch.object(
                doctor_runtime,
                "_command_exists",
                side_effect=lambda command: which_map.get(command),
            ):
                with mock.patch.object(
                    doctor_runtime,
                    "_git_output",
                    return_value=(False, "git command timed out after 120s: git -C /tmp/demo rev-parse --git-dir", "timeout"),
                ):
                    payload = install_module.doctor_deps(project_root, ROOT, "generic")

            self.assertFalse(payload["ok"])
            dependencies = {item["name"]: item for item in payload["dependencies"]}
            git_repository = dependencies["git_repository"]
            self.assertEqual(git_repository["status"], "misconfigured")
            self.assertIn("git command timed out after 120s", git_repository["detail"])
            self.assertNotIn("не выглядит git-репозиторием", git_repository["detail"])
            self.assertEqual(dependencies["publish_remote"]["status"], "not-applicable")

    def test_doctor_deps_keeps_non_repo_diagnosis_for_directory_without_git(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            which_map = {
                "python3": shutil.which("python3"),
                "git": shutil.which("git"),
                "gh": None,
                "glab": None,
            }
            with mock.patch.object(
                doctor_runtime,
                "_command_exists",
                side_effect=lambda command: which_map.get(command),
            ):
                payload = install_module.doctor_deps(project_root, ROOT, "generic")

            self.assertFalse(payload["ok"])
            dependencies = {item["name"]: item for item in payload["dependencies"]}
            git_repository = dependencies["git_repository"]
            self.assertEqual(git_repository["status"], "misconfigured")
            self.assertIn("не выглядит git-репозиторием", git_repository["detail"])

    def test_doctor_deps_surfaces_publish_remote_timeout_without_false_missing_remote_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = self._init_repo(Path(tmp_dir))
            which_map = {
                "python3": shutil.which("python3"),
                "git": shutil.which("git"),
                "gh": None,
                "glab": None,
            }
            with mock.patch.object(
                doctor_runtime,
                "_command_exists",
                side_effect=lambda command: which_map.get(command),
            ):
                with mock.patch.object(
                    doctor_runtime,
                    "_git_output",
                    side_effect=[
                        (True, ".git", None),
                        (True, "origin", None),
                        (False, "git command timed out after 120s: git -C /tmp/demo remote get-url origin", "timeout"),
                    ],
                ):
                    payload = install_module.doctor_deps(project_root, ROOT, "generic")

            dependencies = {item["name"]: item for item in payload["dependencies"]}
            publish_remote = dependencies["publish_remote"]
            self.assertEqual(publish_remote["status"], "misconfigured")
            self.assertIn("git command timed out after 120s", publish_remote["detail"])
            self.assertNotIn("не найден", publish_remote["detail"])
            self.assertEqual(dependencies["gh"]["status"], "not-applicable")

    def test_doctor_deps_surfaces_broken_publish_remote_without_false_missing_remote_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = self._init_repo(Path(tmp_dir))
            which_map = {
                "python3": shutil.which("python3"),
                "git": shutil.which("git"),
                "gh": None,
                "glab": None,
            }
            with mock.patch.object(
                doctor_runtime,
                "_command_exists",
                side_effect=lambda command: which_map.get(command),
            ):
                with mock.patch.object(
                    doctor_runtime,
                    "_git_output",
                    side_effect=[
                        (True, ".git", None),
                        (True, "origin", None),
                        (False, "fatal: unable to read remote url for origin", None),
                    ],
                ):
                    payload = install_module.doctor_deps(project_root, ROOT, "generic")

            dependencies = {item["name"]: item for item in payload["dependencies"]}
            publish_remote = dependencies["publish_remote"]
            self.assertEqual(publish_remote["status"], "misconfigured")
            self.assertIn("unable to read remote url", publish_remote["detail"])
            self.assertNotIn("не найден", publish_remote["detail"])
            self.assertEqual(dependencies["gh"]["status"], "not-applicable")

    def test_migrate_cleanup_plan_discloses_scope_and_protected_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = self._init_repo(Path(tmp_dir))
            self._write_managed_agents(project_root)
            self._write_registry(project_root)
            task_dir = self._write_task_dir(project_root)
            snippet_path = project_root / "AGENTS.task-centric-knowledge.generic.md"
            snippet_path.write_text("snippet\n", encoding="utf-8")
            migration_note = project_root / "knowledge" / install_module.MIGRATION_NOTE_NAME
            migration_note.parent.mkdir(parents=True, exist_ok=True)
            migration_note.write_text("note\n", encoding="utf-8")
            foreign_path = project_root / "docs/tasks"
            foreign_path.mkdir(parents=True, exist_ok=True)

            payload = install_module.migrate_cleanup_plan(
                project_root,
                source_root=ROOT,
                profile="generic",
                existing_system_mode="migrate",
                script_path=INSTALL_SCRIPT,
                source_root_arg=None,
                output_format="text",
            )

            self.assertTrue(payload["ok"])
            self.assertEqual(payload["target_count"], 1)
            self.assertEqual(payload["count"], 1)
            self.assertEqual(payload["targets"], [str(snippet_path.resolve())])
            self.assertIn(payload["plan_fingerprint"], payload["confirm_command"])
            keep_paths = {item["path"] for item in payload["keep"]}
            manual_paths = {item["path"] for item in payload["manual_review"]}
            self.assertIn(str((project_root / "knowledge/tasks/registry.md").resolve()), keep_paths)
            self.assertIn(str(task_dir.resolve()), keep_paths)
            self.assertIn(str(migration_note.resolve()), keep_paths)
            self.assertIn(str(foreign_path.resolve()), manual_paths)

    def test_migrate_cleanup_plan_routes_symlinked_snippet_to_manual_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            project_root = self._init_repo(tmp_path)
            self._write_managed_agents(project_root)
            external_target = tmp_path / "external-snippet.md"
            external_target.write_text("external\n", encoding="utf-8")
            snippet_path = project_root / "AGENTS.task-centric-knowledge.generic.md"
            snippet_path.symlink_to(external_target)

            payload = install_module.migrate_cleanup_plan(
                project_root,
                source_root=ROOT,
                profile="generic",
                existing_system_mode="abort",
                script_path=INSTALL_SCRIPT,
                source_root_arg=None,
                output_format="text",
            )

            self.assertTrue(payload["ok"])
            self.assertEqual(payload["target_count"], 0)
            self.assertEqual(payload["count"], 0)
            self.assertEqual(payload["targets"], [])
            self.assertEqual(payload["confirm_command"], "—")
            manual_paths = {item["path"] for item in payload["manual_review"]}
            self.assertIn(str(snippet_path.absolute()), manual_paths)
            self.assertTrue(snippet_path.is_symlink())
            self.assertTrue(external_target.exists())

    def test_migrate_cleanup_plan_routes_directory_allowlist_to_manual_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = self._init_repo(Path(tmp_dir))
            self._write_managed_agents(project_root)
            snippet_path = project_root / "AGENTS.task-centric-knowledge.generic.md"
            snippet_path.mkdir()

            payload = install_module.migrate_cleanup_plan(
                project_root,
                source_root=ROOT,
                profile="generic",
                existing_system_mode="abort",
                script_path=INSTALL_SCRIPT,
                source_root_arg=None,
                output_format="text",
            )

            self.assertTrue(payload["ok"])
            self.assertEqual(payload["safe_delete"], [])
            self.assertEqual(payload["targets"], [])
            manual_paths = {item["path"] for item in payload["manual_review"]}
            self.assertIn(str(snippet_path.absolute()), manual_paths)
            self.assertTrue(snippet_path.is_dir())

    def test_migrate_cleanup_plan_text_cli_does_not_require_upgrade_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = self._init_repo(Path(tmp_dir))
            self._write_managed_agents(project_root)
            snippet_path = project_root / "AGENTS.task-centric-knowledge.generic.md"
            snippet_path.write_text("snippet\n", encoding="utf-8")

            env = os.environ.copy()
            pythonpath_parts = [str(SCRIPTS_DIR)]
            if env.get("PYTHONPATH"):
                pythonpath_parts.append(env["PYTHONPATH"])
            env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(INSTALL_SCRIPT),
                    "--project-root",
                    str(project_root),
                    "--mode",
                    "migrate-cleanup-plan",
                ],
                capture_output=True,
                text=True,
                check=False,
                env=env,
                timeout=SUBPROCESS_TIMEOUT_SECONDS,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("mode=migrate-cleanup-plan", completed.stdout)
            self.assertIn("TARGET_COUNT=1", completed.stdout)
            self.assertIn("COUNT=1", completed.stdout)
            self.assertIn("PLAN_FINGERPRINT=", completed.stdout)

    def test_migrate_cleanup_confirm_requires_fingerprint_and_yes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = self._init_repo(Path(tmp_dir))
            self._write_managed_agents(project_root)
            snippet_path = project_root / "AGENTS.task-centric-knowledge.generic.md"
            snippet_path.write_text("snippet\n", encoding="utf-8")

            missing_fingerprint = install_module.migrate_cleanup_confirm(
                project_root,
                source_root=ROOT,
                profile="generic",
                existing_system_mode="abort",
                script_path=INSTALL_SCRIPT,
                source_root_arg=None,
                output_format="text",
                confirm_fingerprint=None,
                assume_yes=True,
            )
            self.assertFalse(missing_fingerprint["ok"])

            plan = install_module.migrate_cleanup_plan(
                project_root,
                source_root=ROOT,
                profile="generic",
                existing_system_mode="abort",
                script_path=INSTALL_SCRIPT,
                source_root_arg=None,
                output_format="text",
            )
            missing_yes = install_module.migrate_cleanup_confirm(
                project_root,
                source_root=ROOT,
                profile="generic",
                existing_system_mode="abort",
                script_path=INSTALL_SCRIPT,
                source_root_arg=None,
                output_format="text",
                confirm_fingerprint=plan["plan_fingerprint"],
                assume_yes=False,
            )
            self.assertFalse(missing_yes["ok"])
            self.assertTrue(snippet_path.exists())

    def test_migrate_cleanup_confirm_applies_exact_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = self._init_repo(Path(tmp_dir))
            self._write_managed_agents(project_root)
            snippet_path = project_root / "AGENTS.task-centric-knowledge.generic.md"
            snippet_path.write_text("snippet\n", encoding="utf-8")

            plan = install_module.migrate_cleanup_plan(
                project_root,
                source_root=ROOT,
                profile="generic",
                existing_system_mode="abort",
                script_path=INSTALL_SCRIPT,
                source_root_arg=None,
                output_format="text",
            )
            payload = install_module.migrate_cleanup_confirm(
                project_root,
                source_root=ROOT,
                profile="generic",
                existing_system_mode="abort",
                script_path=INSTALL_SCRIPT,
                source_root_arg=None,
                output_format="text",
                confirm_fingerprint=plan["plan_fingerprint"],
                assume_yes=True,
            )

            self.assertTrue(payload["ok"])
            self.assertFalse(snippet_path.exists())
            self.assertTrue((project_root / "AGENTS.md").exists())

    def test_migrate_cleanup_confirm_rejects_scope_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = self._init_repo(Path(tmp_dir))
            self._write_managed_agents(project_root)
            snippet_path = project_root / "AGENTS.task-centric-knowledge.generic.md"
            snippet_path.write_text("snippet\n", encoding="utf-8")

            plan = install_module.migrate_cleanup_plan(
                project_root,
                source_root=ROOT,
                profile="generic",
                existing_system_mode="abort",
                script_path=INSTALL_SCRIPT,
                source_root_arg=None,
                output_format="text",
            )
            second_snippet = project_root / "AGENTS.task-centric-knowledge.1c.md"
            second_snippet.write_text("snippet\n", encoding="utf-8")

            payload = install_module.migrate_cleanup_confirm(
                project_root,
                source_root=ROOT,
                profile="generic",
                existing_system_mode="abort",
                script_path=INSTALL_SCRIPT,
                source_root_arg=None,
                output_format="text",
                confirm_fingerprint=plan["plan_fingerprint"],
                assume_yes=True,
            )

            self.assertFalse(payload["ok"])
            self.assertTrue(snippet_path.exists())
            self.assertTrue(second_snippet.exists())


if __name__ == "__main__":
    unittest.main()
