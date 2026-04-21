from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from task_workflow_testlib import ROOT


RUNTIME_DIR = ROOT / "scripts" / "module_core_runtime"


class TestModuleQueryArchitecture(unittest.TestCase):
    def test_module_query_runtime_modules_follow_allowed_internal_import_graph(self) -> None:
        allowed = {
            "read_model.py": {"file_local_contracts", "verification"},
            "query_cli.py": {"read_model"},
        }

        for filename, expected in allowed.items():
            source = (RUNTIME_DIR / filename).read_text(encoding="utf-8")
            tree = ast.parse(source)
            actual = {
                node.module.split(".")[-1]
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module and node.level == 1
            }
            assert actual <= expected, (filename, actual, expected)


if __name__ == "__main__":
    unittest.main()
