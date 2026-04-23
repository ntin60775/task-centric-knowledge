from __future__ import annotations

import ast
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PythonHardeningContractsTests(unittest.TestCase):
    def test_pyproject_declares_package_entrypoint_and_dev_static_tools(self) -> None:
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

        self.assertEqual(pyproject["project"]["scripts"]["task-knowledge"], "task_knowledge.__main__:main")
        dev_dependencies = "\n".join(pyproject["project"]["optional-dependencies"]["dev"])
        self.assertIn("mypy", dev_dependencies)
        self.assertIn("ruff", dev_dependencies)
        self.assertIn("ruff", pyproject["tool"])
        self.assertIn("mypy", pyproject["tool"])

    def test_python_module_entrypoint_exists(self) -> None:
        main_path = ROOT / "scripts" / "task_knowledge" / "__main__.py"
        self.assertTrue(main_path.exists())
        self.assertIn("from task_knowledge_cli import main", main_path.read_text(encoding="utf-8"))

    def test_makefile_keeps_offline_fallback_for_local_install(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        self.assertIn("import setuptools", makefile)
        self.assertIn("task_knowledge_local.pth", makefile)
        self.assertIn("install-wrapper", makefile)

    def test_primary_runtime_hotspots_remain_decomposed(self) -> None:
        limits = {
            ("scripts/task_knowledge_cli.py", "build_parser"): 40,
            ("scripts/task_workflow_runtime/finalize_flow.py", "finalize_task"): 90,
            ("scripts/task_workflow_runtime/publish_flow.py", "run_publish_flow"): 90,
            ("scripts/task_workflow_runtime/sync_flow.py", "backfill_task"): 40,
            ("scripts/module_core_runtime/read_model.py", "_record_from_directory"): 120,
        }
        for (path_text, function_name), max_lines in limits.items():
            with self.subTest(path=path_text, function=function_name):
                function_length = self._function_length(ROOT / path_text, function_name)
                self.assertLessEqual(function_length, max_lines)

    def _function_length(self, path: Path, function_name: str) -> int:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                assert node.end_lineno is not None
                return node.end_lineno - node.lineno + 1
        raise AssertionError(f"Function {function_name!r} not found in {path}")


if __name__ == "__main__":
    unittest.main()
