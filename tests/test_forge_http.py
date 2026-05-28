"""Tests for HTTP API forge adapters (GitHubAPIAdapter, GitLabAPIAdapter)."""

from __future__ import annotations

import json
import os
import unittest
from pathlib import Path
from unittest import mock

from src.task_knowledge.workflow_runtime.forge import (
    GitHubAPIAdapter,
    GitLabAPIAdapter,
    _github_pr_to_snapshot,
    _gitlab_mr_to_snapshot,
    _parse_github_remote,
    _parse_gitlab_remote,
    resolve_forge_adapter,
)


class TestRemoteParsing(unittest.TestCase):
    """Tests for URL parsing helper functions."""

    def test_parse_github_remote_https(self):
        owner, repo = _parse_github_remote("https://github.com/owner/repo.git")
        self.assertEqual(owner, "owner")
        self.assertEqual(repo, "repo")

    def test_parse_github_remote_ssh(self):
        owner, repo = _parse_github_remote("git@github.com:owner/repo.git")
        self.assertEqual(owner, "owner")
        self.assertEqual(repo, "repo")

    def test_parse_github_remote_no_git_suffix(self):
        owner, repo = _parse_github_remote("https://github.com/org/project")
        self.assertEqual(owner, "org")
        self.assertEqual(repo, "project")

    def test_parse_github_remote_invalid(self):
        with self.assertRaises(ValueError):
            _parse_github_remote("https://gitlab.com/owner/repo.git")

    def test_parse_gitlab_remote_https(self):
        ns, proj = _parse_gitlab_remote("https://gitlab.com/namespace/project.git")
        self.assertEqual(ns, "namespace")
        self.assertEqual(proj, "project")

    def test_parse_gitlab_remote_ssh(self):
        ns, proj = _parse_gitlab_remote("git@gitlab.com:namespace/project.git")
        self.assertEqual(ns, "namespace")
        self.assertEqual(proj, "project")


class TestGitHubAPIAdapter(unittest.TestCase):
    """Tests for GitHubAPIAdapter using mocked HTTP."""

    def setUp(self):
        # Ensure GITHUB_TOKEN is set for tests
        os.environ["GITHUB_TOKEN"] = "test-token"

    def tearDown(self):
        pass  # keep token for other tests

    def test_ensure_auth_with_token(self):
        adapter = GitHubAPIAdapter("github.com")
        adapter.ensure_auth(Path("/tmp"))  # should not raise

    def test_ensure_auth_without_token(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            adapter = GitHubAPIAdapter("github.com")
            with self.assertRaises(ValueError) as ctx:
                adapter.ensure_auth(Path("/tmp"))
            self.assertIn("GITHUB_TOKEN", str(ctx.exception))

    def _mock_urlopen(self, status=200, response_body=None, content_type="application/json"):
        """Create a mock for urllib.request.urlopen."""
        if response_body is None:
            response_body = {}
        body_bytes = json.dumps(response_body).encode("utf-8")

        mock_response = mock.MagicMock()
        mock_response.__enter__ = mock.MagicMock(return_value=mock_response)
        mock_response.__exit__ = mock.MagicMock(return_value=None)
        mock_response.read.return_value = body_bytes
        mock_response.status = status

        return mock.MagicMock(return_value=mock_response)

    @mock.patch("src.task_knowledge.workflow_runtime.forge.urllib.request.urlopen")
    @mock.patch("src.task_knowledge.workflow_runtime.forge._resolve_remote_url")
    def test_create_publication_github(self, mock_resolve, mock_urlopen):
        mock_resolve.return_value = "https://github.com/owner/repo.git"
        post_response_body = {
            "html_url": "https://github.com/owner/repo/pull/1",
            "number": 1,
            "state": "open",
            "draft": False,
            "head": {"ref": "feature-branch"},
            "base": {"ref": "main"},
            "merge_commit_sha": None,
        }
        get_response = self._mock_urlopen(200, post_response_body)
        post_response = self._mock_urlopen(201, post_response_body)
        mock_urlopen.side_effect = [post_response(), get_response()]

        adapter = GitHubAPIAdapter("github.com")
        snap = adapter.create_publication(
            Path("/tmp/test"),
            head_branch="feature-branch",
            base_branch="main",
            title="Test PR",
            body="Test body",
            draft=False,
        )

        self.assertEqual(snap.host, "github")
        self.assertEqual(snap.publication_type, "pr")
        self.assertEqual(snap.status, "review")
        self.assertEqual(snap.url, "https://github.com/owner/repo/pull/1")

    @mock.patch("src.task_knowledge.workflow_runtime.forge.urllib.request.urlopen")
    @mock.patch("src.task_knowledge.workflow_runtime.forge._resolve_remote_url")
    def test_create_publication_draft(self, mock_resolve, mock_urlopen):
        mock_resolve.return_value = "https://github.com/owner/repo.git"
        post_response_body = {
            "html_url": "https://github.com/owner/repo/pull/2",
            "number": 2,
            "state": "open",
            "draft": True,
            "head": {"ref": "feature"},
            "base": {"ref": "main"},
            "merge_commit_sha": None,
        }
        get_response = self._mock_urlopen(200, post_response_body)
        post_response = self._mock_urlopen(201, post_response_body)
        mock_urlopen.side_effect = [post_response(), get_response()]

        adapter = GitHubAPIAdapter("github.com")
        snap = adapter.create_publication(
            Path("/tmp/test"),
            head_branch="feature",
            base_branch="main",
            title="Draft",
            body="",
            draft=True,
        )

        self.assertEqual(snap.status, "draft")

    @mock.patch("src.task_knowledge.workflow_runtime.forge.urllib.request.urlopen")
    @mock.patch("src.task_knowledge.workflow_runtime.forge._resolve_remote_url")
    def test_read_publication_merged(self, mock_resolve, mock_urlopen):
        mock_resolve.return_value = "https://github.com/owner/repo.git"
        mock_response = self._mock_urlopen(200, {
            "html_url": "https://github.com/owner/repo/pull/1",
            "state": "closed",
            "draft": False,
            "head": {"ref": "feature"},
            "base": {"ref": "main"},
            "merge_commit_sha": "abc123def",
        })
        mock_urlopen.return_value = mock_response()

        adapter = GitHubAPIAdapter("github.com")
        snap = adapter.read_publication(
            Path("/tmp/test"),
            reference="https://github.com/owner/repo/pull/1",
            head_branch="feature",
            base_branch="main",
        )

        self.assertEqual(snap.status, "merged")
        self.assertEqual(snap.merge_commit, "abc123def")

    @mock.patch("src.task_knowledge.workflow_runtime.forge.urllib.request.urlopen")
    @mock.patch("src.task_knowledge.workflow_runtime.forge._resolve_remote_url")
    def test_read_publication_closed(self, mock_resolve, mock_urlopen):
        mock_resolve.return_value = "https://github.com/owner/repo.git"
        mock_response = self._mock_urlopen(200, {
            "html_url": "https://github.com/owner/repo/pull/3",
            "state": "closed",
            "draft": False,
            "head": {"ref": "feature"},
            "base": {"ref": "main"},
            "merge_commit_sha": None,
        })
        mock_urlopen.return_value = mock_response()

        adapter = GitHubAPIAdapter("github.com")
        snap = adapter.read_publication(
            Path("/tmp/test"),
            reference="https://github.com/owner/repo/pull/3",
            head_branch="feature",
            base_branch="main",
        )

        self.assertEqual(snap.status, "closed")


class TestGitLabAPIAdapter(unittest.TestCase):
    """Tests for GitLabAPIAdapter using mocked HTTP."""

    def setUp(self):
        os.environ["GITLAB_TOKEN"] = "test-token"

    def test_ensure_auth_without_token(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            adapter = GitLabAPIAdapter("gitlab.com")
            with self.assertRaises(ValueError) as ctx:
                adapter.ensure_auth(Path("/tmp"))
            self.assertIn("GITLAB_TOKEN", str(ctx.exception))

    def _mock_urlopen(self, status=200, response_body=None):
        if response_body is None:
            response_body = {}
        body_bytes = json.dumps(response_body).encode("utf-8")

        mock_response = mock.MagicMock()
        mock_response.__enter__ = mock.MagicMock(return_value=mock_response)
        mock_response.__exit__ = mock.MagicMock(return_value=None)
        mock_response.read.return_value = body_bytes

        return mock.MagicMock(return_value=mock_response)

    @mock.patch("src.task_knowledge.workflow_runtime.forge.urllib.request.urlopen")
    @mock.patch("src.task_knowledge.workflow_runtime.forge._resolve_remote_url")
    def test_create_publication_gitlab(self, mock_resolve, mock_urlopen):
        mock_resolve.return_value = "https://gitlab.com/namespace/project.git"

        mr_payload = {
            "web_url": "https://gitlab.com/namespace/project/-/merge_requests/1",
            "state": "opened",
            "draft": False,
            "source_branch": "feature",
            "target_branch": "main",
            "merge_commit_sha": None,
        }
        # POST returns 201, then GET (search) returns list with one MR
        post_response = self._mock_urlopen(201, mr_payload)
        get_response = self._mock_urlopen(200, [mr_payload])
        mock_urlopen.side_effect = [post_response(), get_response()]

        adapter = GitLabAPIAdapter("gitlab.com")
        snap = adapter.create_publication(
            Path("/tmp/test"),
            head_branch="feature",
            base_branch="main",
            title="Test MR",
            body="Body",
            draft=False,
        )

        self.assertEqual(snap.host, "gitlab")
        self.assertEqual(snap.publication_type, "mr")
        self.assertEqual(snap.status, "review")

    @mock.patch("src.task_knowledge.workflow_runtime.forge.urllib.request.urlopen")
    @mock.patch("src.task_knowledge.workflow_runtime.forge._resolve_remote_url")
    def test_read_publication_gitlab(self, mock_resolve, mock_urlopen):
        mock_resolve.return_value = "https://gitlab.com/ns/proj.git"
        mock_response = self._mock_urlopen(200, {
            "web_url": "https://gitlab.com/ns/proj/-/merge_requests/5",
            "state": "merged",
            "draft": False,
            "source_branch": "feature",
            "target_branch": "main",
            "merge_commit_sha": "abc123",
        })
        mock_urlopen.return_value = mock_response()

        adapter = GitLabAPIAdapter("gitlab.com")
        snap = adapter.read_publication(
            Path("/tmp/test"),
            reference="https://gitlab.com/ns/proj/-/merge_requests/5",
            head_branch="feature",
            base_branch="main",
        )

        self.assertEqual(snap.status, "merged")
        self.assertEqual(snap.merge_commit, "abc123")


class TestSnapshotHelpers(unittest.TestCase):
    """Tests for snapshot mapping functions."""

    def test_github_pr_to_snapshot_review(self):
        payload = {
            "html_url": "https://github.com/o/r/pull/1",
            "state": "open",
            "draft": False,
            "head": {"ref": "feat"},
            "base": {"ref": "main"},
            "merge_commit_sha": None,
        }
        snap = _github_pr_to_snapshot(payload, "feat", "main")
        self.assertEqual(snap.status, "review")

    def test_github_pr_to_snapshot_draft(self):
        payload = {
            "html_url": "https://github.com/o/r/pull/1",
            "state": "open",
            "draft": True,
            "head": {"ref": "feat"},
            "base": {"ref": "main"},
            "merge_commit_sha": None,
        }
        snap = _github_pr_to_snapshot(payload, "feat", "main")
        self.assertEqual(snap.status, "draft")

    def test_github_pr_to_snapshot_merged(self):
        payload = {
            "html_url": "https://github.com/o/r/pull/1",
            "state": "closed",
            "draft": False,
            "head": {"ref": "feat"},
            "base": {"ref": "main"},
            "merge_commit_sha": "abc123",
        }
        snap = _github_pr_to_snapshot(payload, "feat", "main")
        self.assertEqual(snap.status, "merged")

    def test_github_pr_to_snapshot_closed(self):
        payload = {
            "html_url": "https://github.com/o/r/pull/1",
            "state": "closed",
            "draft": False,
            "head": {"ref": "feat"},
            "base": {"ref": "main"},
            "merge_commit_sha": None,
        }
        snap = _github_pr_to_snapshot(payload, "feat", "main")
        self.assertEqual(snap.status, "closed")

    def test_gitlab_mr_to_snapshot(self):
        payload = {
            "web_url": "https://gitlab.com/o/r/-/merge_requests/1",
            "state": "opened",
            "draft": False,
            "source_branch": "feat",
            "target_branch": "main",
            "merge_commit_sha": None,
        }
        snap = _gitlab_mr_to_snapshot(payload, "feat", "main")
        self.assertEqual(snap.status, "review")


class TestResolveForgeAdapter(unittest.TestCase):
    """Tests for the resolve_forge_adapter function."""

    def setUp(self):
        os.environ["GITHUB_TOKEN"] = "test-token"

    @mock.patch("src.task_knowledge.workflow_runtime.forge.remote_hostname")
    @mock.patch("src.task_knowledge.workflow_runtime.forge.remote_url")
    @mock.patch("src.task_knowledge.workflow_runtime.forge.command_exists")
    def test_resolve_github_cli_preferred(self, mock_cmd_exists, mock_remote_url, mock_remote_hostname):
        mock_remote_hostname.return_value = "github.com"
        mock_remote_url.return_value = "git@github.com:owner/repo.git"
        mock_cmd_exists.return_value = True

        with mock.patch("src.task_knowledge.workflow_runtime.forge.run_command") as mock_run:
            mock_run.return_value = mock.MagicMock(returncode=0)
            adapter = resolve_forge_adapter(Path("/tmp"), "github", "origin", None)
            self.assertIsInstance(adapter, GitHubAPIAdapter.__bases__[0])  # ForgeAdapter

    @mock.patch("src.task_knowledge.workflow_runtime.forge.remote_hostname")
    @mock.patch("src.task_knowledge.workflow_runtime.forge.remote_url")
    @mock.patch("src.task_knowledge.workflow_runtime.forge.command_exists")
    def test_resolve_falls_back_to_http_when_cli_missing(self, mock_cmd_exists, mock_remote_url, mock_remote_hostname):
        mock_remote_hostname.return_value = "github.com"
        mock_remote_url.return_value = "https://github.com/owner/repo.git"
        mock_cmd_exists.return_value = False  # gh not installed

        adapter = resolve_forge_adapter(Path("/tmp"), "github", "origin", None)
        self.assertIsInstance(adapter, GitHubAPIAdapter)

    @mock.patch("src.task_knowledge.workflow_runtime.forge.remote_hostname")
    @mock.patch("src.task_knowledge.workflow_runtime.forge.remote_url")
    @mock.patch("src.task_knowledge.workflow_runtime.forge.command_exists")
    def test_resolve_raises_when_no_adapter_available(self, mock_cmd_exists, mock_remote_url, mock_remote_hostname):
        mock_remote_hostname.return_value = "github.com"
        mock_remote_url.return_value = "https://github.com/owner/repo.git"
        mock_cmd_exists.return_value = False

        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as ctx:
                resolve_forge_adapter(Path("/tmp"), "github", "origin", None)
            self.assertIn("не найден", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
