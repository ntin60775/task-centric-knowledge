from __future__ import annotations

import unittest

from task_workflow_runtime.models import DeliveryUnit, DeliveryUnitVersion
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


class TestTaskWorkflowRegistry(TaskWorkflowRegistryTests, unittest.TestCase):
    pass
