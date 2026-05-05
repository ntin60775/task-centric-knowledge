from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "scripts" / "install_skill_runtime"


class TestInstallSkillArchitecture(unittest.TestCase):
    def test_runtime_modules_follow_allowed_internal_import_graph(self) -> None:
        allowed = {
            "models.py": set(),
            "environment.py": {"models"},
            "doctor.py": {"environment", "models"},
            "cleanup.py": {"environment", "models"},
            "cli.py": set(),
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
