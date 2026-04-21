from __future__ import annotations

import json
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))
SCRIPTS_DIR = TESTS_DIR.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from borrowings_runtime.grace import BorrowingsError, apply_refresh, build_refresh_plan, read_status
from task_workflow_testlib import TempRepoCase, git


class BorrowingsRuntimeTests(TempRepoCase):
    def write_manifest(self, skill_root: Path, *, pinned_revision: str, local_target: str = "borrowings/grace/upstream/example.md") -> None:
        manifest_path = skill_root / "borrowings/grace/source.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "source_id": "grace-marketplace",
                    "origin_url": "https://github.com/osovv/grace-marketplace.git",
                    "pinned_revision": pinned_revision,
                    "upstream_version": "test",
                    "local_checkout_override": {
                        "cli_option": "--checkout",
                        "env": "TASK_KNOWLEDGE_GRACE_CHECKOUT",
                        "required": False,
                    },
                    "surfaces": [
                        {
                            "surface_id": "example",
                            "adoption_mode": "reference",
                            "concepts": ["example"],
                            "upstream_paths": ["docs/example.md"],
                            "local_targets": [local_target],
                            "mappings": [
                                {
                                    "upstream_path": "docs/example.md",
                                    "local_target": local_target,
                                }
                            ],
                        }
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def make_checkout(self, root: Path) -> tuple[Path, str]:
        checkout = root / "checkout"
        checkout.mkdir()
        git(checkout, "init")
        git(checkout, "config", "user.name", "Test User")
        git(checkout, "config", "user.email", "test@example.com")
        source_path = checkout / "docs/example.md"
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text("borrowed source\n", encoding="utf-8")
        git(checkout, "add", ".")
        git(checkout, "commit", "-m", "source")
        return checkout, git(checkout, "rev-parse", "HEAD")

    def test_refresh_apply_requires_matching_preview_fingerprint(self) -> None:
        with self.make_tempdir() as tmp_dir:
            root = Path(tmp_dir)
            project_root = root / "project"
            project_root.mkdir()
            skill_root = root / "skill"
            checkout, revision = self.make_checkout(root)
            self.write_manifest(skill_root, pinned_revision=revision)

            plan = build_refresh_plan(skill_root, project_root, source="grace", checkout=str(checkout))

            self.assertTrue(plan["ok"])
            self.assertEqual(plan["pending_action_count"], 1)
            self.assertEqual(plan["actions"][0]["action"], "create")

            unconfirmed = apply_refresh(
                skill_root,
                project_root,
                source="grace",
                checkout=str(checkout),
                plan_fingerprint=str(plan["plan_fingerprint"]),
                assume_yes=False,
            )

            self.assertFalse(unconfirmed["ok"])
            self.assertEqual(unconfirmed["results"][0]["key"], "confirmation")

            rejected = apply_refresh(
                skill_root,
                project_root,
                source="grace",
                checkout=str(checkout),
                plan_fingerprint="bad",
                assume_yes=True,
            )

            self.assertFalse(rejected["ok"])
            self.assertEqual(rejected["results"][0]["key"], "plan_fingerprint")

            applied = apply_refresh(
                skill_root,
                project_root,
                source="grace",
                checkout=str(checkout),
                plan_fingerprint=str(plan["plan_fingerprint"]),
                assume_yes=True,
            )

            self.assertTrue(applied["ok"])
            self.assertEqual(applied["applied_count"], 1)
            target_path = skill_root / "borrowings/grace/upstream/example.md"
            self.assertEqual(target_path.read_text(encoding="utf-8"), "borrowed source\n")

            next_plan = build_refresh_plan(skill_root, project_root, source="grace", checkout=str(checkout))

            self.assertTrue(next_plan["ok"])
            self.assertEqual(next_plan["pending_action_count"], 0)
            self.assertEqual(next_plan["actions"][0]["action"], "noop")

    def test_target_drift_changes_refresh_fingerprint(self) -> None:
        with self.make_tempdir() as tmp_dir:
            root = Path(tmp_dir)
            project_root = root / "project"
            project_root.mkdir()
            skill_root = root / "skill"
            checkout, revision = self.make_checkout(root)
            self.write_manifest(skill_root, pinned_revision=revision)

            first_plan = build_refresh_plan(skill_root, project_root, source="grace", checkout=str(checkout))
            target_path = skill_root / "borrowings/grace/upstream/example.md"
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text("local drift\n", encoding="utf-8")
            second_plan = build_refresh_plan(skill_root, project_root, source="grace", checkout=str(checkout))

            self.assertTrue(first_plan["ok"])
            self.assertTrue(second_plan["ok"])
            self.assertNotEqual(first_plan["plan_fingerprint"], second_plan["plan_fingerprint"])
            self.assertEqual(second_plan["actions"][0]["action"], "update")

    def test_manifest_rejects_target_outside_skill_root(self) -> None:
        with self.make_tempdir() as tmp_dir:
            root = Path(tmp_dir)
            project_root = root / "project"
            project_root.mkdir()
            skill_root = root / "skill"
            checkout, revision = self.make_checkout(root)
            self.write_manifest(skill_root, pinned_revision=revision, local_target="../escape.md")

            with self.assertRaises(BorrowingsError):
                read_status(skill_root, project_root, source="grace", checkout=str(checkout))

    def test_refresh_plan_blocks_wrong_checkout_revision(self) -> None:
        with self.make_tempdir() as tmp_dir:
            root = Path(tmp_dir)
            project_root = root / "project"
            project_root.mkdir()
            skill_root = root / "skill"
            checkout, _revision = self.make_checkout(root)
            self.write_manifest(skill_root, pinned_revision="0" * 40)

            plan = build_refresh_plan(skill_root, project_root, source="grace", checkout=str(checkout))

            self.assertFalse(plan["ok"])
            self.assertEqual(plan["results"][0]["key"], "pinned_revision")

    def test_refresh_plan_blocks_dirty_mapped_checkout(self) -> None:
        with self.make_tempdir() as tmp_dir:
            root = Path(tmp_dir)
            project_root = root / "project"
            project_root.mkdir()
            skill_root = root / "skill"
            checkout, revision = self.make_checkout(root)
            self.write_manifest(skill_root, pinned_revision=revision)

            (checkout / "docs/example.md").write_text("dirty source\n", encoding="utf-8")

            plan = build_refresh_plan(skill_root, project_root, source="grace", checkout=str(checkout))

            self.assertFalse(plan["ok"])
            self.assertEqual(plan["results"][0]["key"], "checkout_dirty")
            self.assertTrue(plan["dirty_paths"])
            self.assertIn("docs/example.md", "\n".join(plan["dirty_paths"]))

    def test_status_reports_dirty_mapped_checkout(self) -> None:
        with self.make_tempdir() as tmp_dir:
            root = Path(tmp_dir)
            project_root = root / "project"
            project_root.mkdir()
            skill_root = root / "skill"
            checkout, revision = self.make_checkout(root)
            self.write_manifest(skill_root, pinned_revision=revision)

            (checkout / "docs/example.md").write_text("dirty source\n", encoding="utf-8")

            payload = read_status(skill_root, project_root, source="grace", checkout=str(checkout))

            self.assertTrue(payload["ok"])
            self.assertTrue(payload["mapped_paths_dirty"])
            self.assertTrue(payload["dirty_paths"])
            self.assertIn("checkout_dirty", {warning["key"] for warning in payload["warnings"]})

    def test_manifest_rejects_duplicate_local_targets(self) -> None:
        with self.make_tempdir() as tmp_dir:
            root = Path(tmp_dir)
            project_root = root / "project"
            project_root.mkdir()
            skill_root = root / "skill"
            checkout, revision = self.make_checkout(root)
            self.write_manifest(skill_root, pinned_revision=revision)

            manifest_path = skill_root / "borrowings/grace/source.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["surfaces"].append(
                {
                    "surface_id": "duplicate-target",
                    "adoption_mode": "reference",
                    "concepts": ["duplicate"],
                    "upstream_paths": ["docs/example.md"],
                    "local_targets": ["borrowings/grace/upstream/example.md"],
                    "mappings": [
                        {
                            "upstream_path": "docs/example.md",
                            "local_target": "borrowings/grace/upstream/example.md",
                        }
                    ],
                }
            )
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

            with self.assertRaisesRegex(BorrowingsError, "local_target должен быть уникальным"):
                read_status(skill_root, project_root, source="grace", checkout=str(checkout))

    def test_manifest_rejects_surface_summary_drift(self) -> None:
        with self.make_tempdir() as tmp_dir:
            root = Path(tmp_dir)
            project_root = root / "project"
            project_root.mkdir()
            skill_root = root / "skill"
            checkout, revision = self.make_checkout(root)
            self.write_manifest(skill_root, pinned_revision=revision)

            manifest_path = skill_root / "borrowings/grace/source.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["surfaces"][0]["local_targets"] = ["borrowings/grace/upstream/other.md"]
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

            with self.assertRaisesRegex(BorrowingsError, "drift между local_targets и mappings"):
                read_status(skill_root, project_root, source="grace", checkout=str(checkout))


if __name__ == "__main__":
    import unittest

    unittest.main()
