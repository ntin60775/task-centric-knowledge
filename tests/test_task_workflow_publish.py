from __future__ import annotations

import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

SCRIPTS_DIR = TESTS_DIR.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from task_workflow_runtime.models import DeliveryUnit
from task_workflow_runtime.publish_flow import branch_for_task_context, resolve_publish_snapshot
from task_workflow_testlib import TempRepoCase, git


class TestTaskWorkflowPublish(TempRepoCase):
    def test_resolve_publish_snapshot_uses_explicit_values_without_adapter(self) -> None:
        current_unit = DeliveryUnit(
            unit_id="DU-01",
            purpose="Первая поставка",
            head="du/task-2026-0001-u01-demo",
            base="main",
            host="none",
            publication_type="none",
            status="local",
            url="—",
            merge_commit="—",
            cleanup="не требуется",
        )

        snapshot = resolve_publish_snapshot(
            Path("."),
            Path("."),
            {"ID задачи": "TASK-2026-0001"},
            current_unit,
            action="publish",
            requested_host="github",
            requested_publication_type="pr",
            requested_status="draft",
            url="https://example.test/pr/1",
            merge_commit=None,
            remote_name="origin",
            create_publication=False,
            sync_from_host=False,
            title=None,
            body=None,
            summary="Summary",
        )

        self.assertEqual(snapshot.host, "github")
        self.assertEqual(snapshot.publication_type, "pr")
        self.assertEqual(snapshot.status, "draft")
        self.assertEqual(snapshot.url, "https://example.test/pr/1")

    def test_branch_for_task_context_accepts_current_task_branch(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            branch_name = "task/task-2026-0001-demo"
            git(project_root, "checkout", "-b", branch_name)
            delivery_unit = DeliveryUnit(
                unit_id="DU-01",
                purpose="Первая поставка",
                head="du/task-2026-0001-u01-demo",
                base="main",
                host="none",
                publication_type="none",
                status="local",
                url="—",
                merge_commit="—",
                cleanup="не требуется",
            )

            resolved = branch_for_task_context(
                project_root,
                project_root / "knowledge/tasks/TASK-2026-0001-demo",
                {
                    "ID задачи": "TASK-2026-0001",
                    "Краткое имя": "demo",
                    "Ветка": branch_name,
                },
                delivery_unit,
            )

            self.assertEqual(resolved, branch_name)
