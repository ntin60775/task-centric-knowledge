from __future__ import annotations

import ast
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path
import sys


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

    def test_version_and_consumer_contract_have_single_python_source(self) -> None:
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        version_text = (ROOT / "scripts" / "task_knowledge" / "version.py").read_text(encoding="utf-8")
        init_text = (ROOT / "scripts" / "task_knowledge" / "__init__.py").read_text(encoding="utf-8")
        cli_text = (ROOT / "scripts" / "task_knowledge_cli.py").read_text(encoding="utf-8")

        self.assertIn(f'__version__ = "{pyproject["project"]["version"]}"', version_text)
        self.assertIn("CLI_VERSION = __version__", version_text)
        self.assertIn('CONSUMER_RUNTIME_CONTRACT = "consumer-runtime-v1"', version_text)
        self.assertIn("from .version import __version__", init_text)
        self.assertIn("from task_knowledge.version import CLI_VERSION", cli_text)

    def test_makefile_keeps_offline_fallback_for_local_install(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        self.assertIn("PYTHON_EXTERNALLY_MANAGED", makefile)
        self.assertIn("PYTHON_HAS_SETUPTOOLS", makefile)
        self.assertIn("task_knowledge_local.pth", makefile)
        self.assertIn("install-wrapper", makefile)

    def test_make_install_local_uses_wrapper_for_managed_python(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            user_bin = Path(tmp_dir) / "bin"
            python_site = Path(tmp_dir) / "site-packages"
            result = subprocess.run(
                [
                    "make",
                    "install-local",
                    f"PYTHON={sys.executable}",
                    f"USER_BIN={user_bin}",
                    f"PYTHON_SITE={python_site}",
                    "PYTHON_EXTERNALLY_MANAGED=1",
                    "PYTHON_HAS_PIP=1",
                    "PYTHON_HAS_SETUPTOOLS=1",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
            wrapper_path = user_bin / "task-knowledge"
            self.assertTrue(wrapper_path.exists())
            self.assertIn("scripts/task_knowledge_cli.py", wrapper_path.read_text(encoding="utf-8"))
            pth_path = python_site / "task_knowledge_local.pth"
            self.assertEqual(pth_path.read_text(encoding="utf-8").strip(), str(ROOT / "scripts"))

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
