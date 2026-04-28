from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from task_workflow_testlib import ROOT


RUNTIME_DIR = ROOT / "scripts" / "task_workflow_runtime"
FACADE_PATH = ROOT / "scripts" / "task_workflow.py"


class TestTaskWorkflowArchitecture(unittest.TestCase):
    def test_runtime_modules_follow_allowed_internal_import_graph(self) -> None:
        allowed = {
            "git_ops.py": {"models"},
            "task_markdown.py": {"models"},
            "registry_sync.py": {"git_ops", "models", "task_markdown"},
            "forge.py": {"git_ops", "models"},
            "path_safety.py": set(),
            "sync_flow.py": {"git_ops", "models", "path_safety", "registry_sync", "task_markdown"},
            "publish_flow.py": {"forge", "git_ops", "models", "path_safety", "registry_sync", "task_markdown"},
            "finalize_flow.py": {"git_ops", "models", "path_safety", "registry_sync", "task_markdown"},
            "cli.py": {"finalize_flow", "models", "publish_flow", "sync_flow"},
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

    def test_task_workflow_facade_is_thin_entrypoint(self) -> None:
        source = FACADE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        function_names = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]
        class_defs = [node.name for node in tree.body if isinstance(node, ast.ClassDef)]

        assert len(source.splitlines()) <= 50
        assert class_defs == []
        assert function_names == ["sync_task", "run_publish_flow", "finalize_task"]
