from __future__ import annotations

import sys
import unittest.mock as mock
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from task_workflow_runtime.models import DeliveryUnit, DeliveryUnitVersion
from task_workflow_runtime import registry_sync
from task_workflow_runtime.registry_sync import merge_delivery_unit_versions, preferred_registry_summary


class TaskWorkflowRegistryTests:
    def test_preferred_registry_summary_prefers_task_human_description(self) -> None:
        summary = preferred_registry_summary(
            {"Человекочитаемое описание": "Каноническая summary"},
            goal_summary="Goal fallback",
            summary="Legacy summary",
            existing_summary="Registry cache",
        )
        assert summary == "Каноническая summary"

    def test_merge_delivery_unit_versions_prefers_richer_metadata_from_fresher_version(self) -> None:
        merged = merge_delivery_unit_versions(
            [
                DeliveryUnitVersion(
                    DeliveryUnit(
                        unit_id="DU-01",
                        purpose="Первая поставка",
                        head="du/task-1-u01",
                        base="main",
                        host="none",
                        publication_type="none",
                        status="draft",
                        url="—",
                        merge_commit="—",
                        cleanup="не требуется",
                    ),
                    (1, 100, 1, "old"),
                ),
                DeliveryUnitVersion(
                    DeliveryUnit(
                        unit_id="DU-01",
                        purpose="Первая поставка",
                        head="du/task-1-u01",
                        base="main",
                        host="github",
                        publication_type="pr",
                        status="draft",
                        url="https://example.test/pr/1",
                        merge_commit="—",
                        cleanup="ожидается",
                    ),
                    (1, 200, 1, "new"),
                ),
            ]
        )

        assert merged.host == "github"
        assert merged.publication_type == "pr"
        assert merged.url == "https://example.test/pr/1"
        assert merged.cleanup == "ожидается"

    def test_read_registry_lines_timeout_is_not_treated_as_missing_ref(self) -> None:
        with mock.patch.object(
            registry_sync,
            "run_git",
            side_effect=RuntimeError("git command timed out after 120s: git -C /tmp/project show main:knowledge/tasks/registry.md"),
        ):
            with self.assertRaises(RuntimeError) as error_ctx:
                registry_sync.read_registry_lines(Path("/tmp/project"), ref_name="main")

        assert "git command timed out after 120s" in str(error_ctx.exception)


class TestTaskWorkflowRegistry(TaskWorkflowRegistryTests, unittest.TestCase):
    pass
