from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from task_knowledge.version import (  # noqa: E402
    CONSUMER_RUNTIME_CONTRACT,
    CONSUMER_RUNTIME_MANIFEST_KEYS,
    CONSUMER_RUNTIME_SCHEMA_VERSION,
)


class ConsumerRuntimeContractTests(unittest.TestCase):
    def test_consumer_runtime_v1_manifest_minimum_shape_is_documented(self) -> None:
        manifest = {
            "integration_contract": CONSUMER_RUNTIME_CONTRACT,
            "pinned_commit": "abc123",
            "included_paths": ["scripts/task_knowledge_cli.py"],
            "consumer_runtime_root": "knowledge/runtime/example",
            "consumer_entrypoint": "task-knowledge task status --project-root /abs/project",
            "schema_version": CONSUMER_RUNTIME_SCHEMA_VERSION,
        }

        for key in CONSUMER_RUNTIME_MANIFEST_KEYS:
            self.assertIn(key, manifest)
        self.assertEqual(manifest["integration_contract"], "consumer-runtime-v1")
        self.assertTrue(str(manifest["consumer_runtime_root"]).startswith("knowledge/runtime/"))
        json.dumps(manifest)

    def test_consumer_runtime_contract_doc_keeps_update_ownership_on_consumer_side(self) -> None:
        text = (ROOT / "references" / "consumer-runtime-v1.md").read_text(encoding="utf-8")

        self.assertIn("consumer-runtime-v1", text)
        self.assertIn("`project_root`", text)
        self.assertIn("`runtime_root`", text)
        self.assertIn("`source_root`", text)
        self.assertIn("Потребитель сам выполняет pull/update embedded subset-а", text)
        self.assertNotIn("task-knowledge consumer sync-apply", text)


if __name__ == "__main__":
    unittest.main()
