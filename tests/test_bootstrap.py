"""Tests for bootstrap module."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest import TestCase


class BootstrapTestCase(TestCase):
    """Bootstrap integration tests."""

    @classmethod
    def setUpClass(cls):
        cls.skill_src = Path("/home/prog7/MyWorkspace/20-Personal/PetProjects/Active/task-centric-knowledge")
        cls.pythonpath = str(cls.skill_src / "src")

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _run_git(self, *args):
        subprocess.run(
            ["git", "-C", str(self.project_root), *args],
            check=True,
            capture_output=True,
            text=True,
        )

    def _init_repo(self):
        self._run_git("init")
        self._run_git("config", "user.email", "test@test.com")
        self._run_git("config", "user.name", "Test")

    def _bootstrap(self, extra_args: list[str] | None = None):
        argv = [
            "python3", "-m", "task_knowledge", "bootstrap",
            "--project-root", str(self.project_root),
        ]
        if extra_args:
            argv.extend(extra_args)
        result = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            env={**subprocess.os.environ, "PYTHONPATH": self.pythonpath},
        )
        return result

    def test_bootstrap_dry_run_no_mutation(self):
        """INV-02: dry-run создаёт файлы."""
        self._init_repo()
        result = self._bootstrap(["--dry-run"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("skipped", result.stdout)
        self.assertIn("dry-run", result.stdout)
        self.assertFalse((self.project_root / "knowledge").exists())

    def test_bootstrap_clean_project_full(self):
        """INV-01/INV-03: полный bootstrap на чистом проекте."""
        self._init_repo()
        result = self._bootstrap()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ok=True", result.stdout)
        self.assertTrue((self.project_root / "knowledge/tasks/TASK-2026-0001/task.md").exists())
        self.assertTrue((self.project_root / "knowledge/tasks/TASK-2026-0001/plan.md").exists())

    def test_bootstrap_non_git_error(self):
        """INV-06: не-git проект возвращает ошибку."""
        result = subprocess.run(
            ["python3", "-m", "task_knowledge", "bootstrap",
             "--project-root", str(self.project_root)],
            capture_output=True,
            text=True,
            env={**subprocess.os.environ, "PYTHONPATH": self.pythonpath},
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("git", result.stdout.lower())

    def test_bootstrap_dirty_worktree_with_non_knowledge_rejects(self):
        """INV-05: чужие dirty-изменения отклоняются."""
        self._init_repo()
        self._run_git("commit", "--allow-empty", "-m", "initial")
        (self.project_root / "src").mkdir()
        (self.project_root / "src" / "main.py").write_text("print('hello')")
        self._run_git("add", "src/main.py")
        result = self._bootstrap()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("dirty", result.stdout.lower())

    def test_bootstrap_profile_1c(self):
        """INV-07: bootstrap с profile=1c корректно применяет блок."""
        self._init_repo()
        result = self._bootstrap(["--profile", "1c"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ok=True", result.stdout)

    def test_bootstrap_knowledge_only_dirty_commits(self):
        """INV-07: знание only dirty tree авто-коммитится."""
        self._init_repo()
        self._run_git("commit", "--allow-empty", "-m", "initial")
        (self.project_root / "knowledge").mkdir(parents=True, exist_ok=True)
        (self.project_root / "knowledge" / "tasks").mkdir(parents=True, exist_ok=True)
        (self.project_root / "knowledge" / "tasks" / "test.md").write_text("# Test")
        self._run_git("add", ".")
        result = self._bootstrap()
        self.assertEqual(result.returncode, 0, result.stderr)
        log_result = subprocess.run(
            ["git", "-C", str(self.project_root), "log", "--oneline", "-1"],
            capture_output=True, text=True,
        )
        self.assertIn("task-knowledge bootstrap", log_result.stdout)

    def test_bootstrap_unknown_system_classification(self):
        """INV-04: unknown classification не блокирует bootstrap."""
        self._init_repo()
        self._run_git("commit", "--allow-empty", "-m", "initial")
        (self.project_root / ".task-knowledge").mkdir(parents=True, exist_ok=True)
        (self.project_root / ".task-knowledge" / "config").write_text("some content")
        self._run_git("add", ".")
        result = self._bootstrap()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ok=True", result.stdout)
