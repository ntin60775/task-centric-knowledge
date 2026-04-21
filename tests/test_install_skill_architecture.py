from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "scripts" / "install_skill_runtime"
FACADE_PATH = ROOT / "scripts" / "install_skill.py"


class TestInstallSkillArchitecture(unittest.TestCase):
    def test_runtime_modules_follow_allowed_internal_import_graph(self) -> None:
        allowed = {
            "models.py": set(),
            "environment.py": {"models"},
            "doctor.py": {"environment", "models"},
            "cleanup.py": {"environment", "models"},
            "cli.py": {"cleanup", "doctor", "environment", "models"},
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

    def test_install_skill_facade_is_thin_entrypoint(self) -> None:
        source = FACADE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        function_names = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]
        class_defs = [node.name for node in tree.body if isinstance(node, ast.ClassDef)]

        assert len(source.splitlines()) <= 70
        assert class_defs == []
        assert function_names == [
            "install",
            "doctor_deps",
            "migrate_cleanup_plan",
            "migrate_cleanup_confirm",
        ]


if __name__ == "__main__":
    unittest.main()
