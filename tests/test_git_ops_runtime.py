from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from task_workflow_runtime import git_ops


class GitOpsRuntimeTests(unittest.TestCase):
    def _timeout(self, command: list[str]) -> subprocess.TimeoutExpired:
        return subprocess.TimeoutExpired(command, git_ops.SUBPROCESS_TIMEOUT_SECONDS)

    def test_run_git_timeout_raises_runtime_error_even_with_check_false(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            command = ["git", "-C", str(project_root), "status"]
            with mock.patch.object(git_ops.subprocess, "run", side_effect=self._timeout(command)):
                with self.assertRaises(RuntimeError) as error_ctx:
                    git_ops.run_git(project_root, "status", check=False)

        self.assertIn("git command timed out after 120s", str(error_ctx.exception))

    def test_branch_exists_surfaces_git_timeout_instead_of_returning_false(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            command = ["git", "-C", str(project_root), "rev-parse", "--verify", "refs/heads/main"]
            with mock.patch.object(git_ops.subprocess, "run", side_effect=self._timeout(command)):
                with self.assertRaises(RuntimeError) as error_ctx:
                    git_ops.branch_exists(project_root, "main")

        self.assertIn("git command timed out after 120s", str(error_ctx.exception))

    def test_ref_exists_surfaces_git_timeout_instead_of_returning_false(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            command = ["git", "-C", str(project_root), "rev-parse", "--verify", "refs/heads/main"]
            with mock.patch.object(git_ops.subprocess, "run", side_effect=self._timeout(command)):
                with self.assertRaises(RuntimeError) as error_ctx:
                    git_ops.ref_exists(project_root, "refs/heads/main")

        self.assertIn("git command timed out after 120s", str(error_ctx.exception))

    def test_remote_url_surfaces_git_timeout_instead_of_returning_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            command = ["git", "-C", str(project_root), "remote", "get-url", "origin"]
            with mock.patch.object(git_ops.subprocess, "run", side_effect=self._timeout(command)):
                with self.assertRaises(RuntimeError) as error_ctx:
                    git_ops.remote_url(project_root)

        self.assertIn("git command timed out after 120s", str(error_ctx.exception))

    def test_infer_base_branch_does_not_fallback_after_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            command = ["git", "-C", str(project_root), "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD"]
            with mock.patch.object(git_ops.subprocess, "run", side_effect=self._timeout(command)):
                with self.assertRaises(RuntimeError) as error_ctx:
                    git_ops.infer_base_branch(project_root)

        self.assertIn("git command timed out after 120s", str(error_ctx.exception))

    def test_run_command_timeout_raises_runtime_error_even_with_check_false(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            command = ["gh", "auth", "status"]
            with mock.patch.object(git_ops.subprocess, "run", side_effect=self._timeout(command)):
                with self.assertRaises(RuntimeError) as error_ctx:
                    git_ops.run_command(project_root, *command, check=False)

        self.assertIn("command timed out after 120s", str(error_ctx.exception))
