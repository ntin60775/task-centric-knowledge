"""Forge adapter integrations for publish flow."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

from .git_ops import command_exists, remote_hostname, remote_url, run_command
from .models import DELIVERY_ROW_PLACEHOLDER, MERGE_REQUEST_URL_RE, PublicationSnapshot


def extract_publication_url(output_text: str) -> str | None:
    """Extract the first HTTP(S) URL found at the end of command output.

    Args:
        output_text: Raw command stdout text.

    Returns:
        URL string, or None if no URL is found.
    """
    for line in reversed(output_text.splitlines()):
        candidate = line.strip()
        if candidate.startswith("http://") or candidate.startswith("https://"):
            return candidate
    return None


def parse_merge_request_reference(reference: str, head_branch: str) -> str:
    """Parse a merge request reference string to extract an MR number.

    Args:
        reference: Reference string, potentially containing an MR URL.
        head_branch: Fallback branch name if no MR number is found.

    Returns:
        MR number or the fallback head_branch.
    """
    match = MERGE_REQUEST_URL_RE.search(reference)
    if match:
        return match.group("number")
    return head_branch


class ForgeAdapter:
    """Abstract base adapter for forge-specific publish operations.

    Note:
        Subclasses must set host_kind and cli_name class attributes.
    """
    host_kind = "generic"
    cli_name = ""

    def __init__(self, hostname: str) -> None:
        """Initialize the adapter with a forge hostname.

        Args:
            hostname: Forge hostname for auth checks.
        """
        self.hostname = hostname

    def ensure_cli(self) -> None:
        """Verify that the forge CLI is installed.

        Raises:
            ValueError: If the CLI is not found on PATH.
        """
        if not command_exists(self.cli_name):
            raise ValueError(f"Для host `{self.host_kind}` не найден CLI `{self.cli_name}`.")

    def ensure_auth(self, project_root: Path) -> None:
        """Verify that the user is authenticated with the forge.

        Args:
            project_root: Path to the project root.

        Raises:
            NotImplementedError: Always; must be overridden by subclasses.
        """
        raise NotImplementedError

    def create_publication(
        self,
        project_root: Path,
        *,
        head_branch: str,
        base_branch: str,
        title: str,
        body: str,
        draft: bool,
    ) -> PublicationSnapshot:
        """Create a new publication (PR/MR) on the forge.

        Args:
            project_root: Path to the project root.
            head_branch: Branch containing the changes.
            base_branch: Branch to merge into.
            title: Publication title.
            body: Publication body.
            draft: Whether to create as draft.

        Returns:
            Snapshot of the created publication.

        Raises:
            NotImplementedError: Always; must be overridden by subclasses.
        """
        raise NotImplementedError

    def update_publication(
        self,
        project_root: Path,
        *,
        reference: str,
        head_branch: str,
        base_branch: str,
    ) -> PublicationSnapshot:
        """Update an existing publication on the forge.

        Args:
            project_root: Path to the project root.
            reference: Publication reference (URL or number).
            head_branch: Branch containing the changes.
            base_branch: Branch to merge into.

        Returns:
            Snapshot of the updated publication.

        Raises:
            NotImplementedError: Always; must be overridden by subclasses.
        """
        raise NotImplementedError

    def read_publication(
        self,
        project_root: Path,
        *,
        reference: str,
        head_branch: str,
        base_branch: str,
    ) -> PublicationSnapshot:
        """Read the current state of a publication from the forge.

        Args:
            project_root: Path to the project root.
            reference: Publication reference (URL or number).
            head_branch: Branch containing the changes.
            base_branch: Branch to merge into.

        Returns:
            Snapshot of the publication.

        Raises:
            NotImplementedError: Always; must be overridden by subclasses.
        """
        raise NotImplementedError


class GitHubAdapter(ForgeAdapter):
    """Forge adapter for GitHub using the gh CLI."""
    host_kind = "github"
    cli_name = "gh"

    def ensure_auth(self, project_root: Path) -> None:
        """Verify GitHub CLI authentication for the configured hostname.

        Args:
            project_root: Path to the project root.

        Raises:
            ValueError: If gh auth status fails.
        """
        completed = run_command(
            project_root,
            "gh",
            "auth",
            "status",
            "--hostname",
            self.hostname,
            check=False,
        )
        if completed.returncode != 0:
            raise ValueError(
                f"`gh auth status --hostname {self.hostname}` завершился ошибкой. "
                "Publish-flow не должен обещать сетевые действия без валидной auth."
            )

    def create_publication(
        self,
        project_root: Path,
        *,
        head_branch: str,
        base_branch: str,
        title: str,
        body: str,
        draft: bool,
    ) -> PublicationSnapshot:
        """Create a pull request on GitHub.

        Args:
            project_root: Path to the project root.
            head_branch: Branch containing the changes.
            base_branch: Branch to merge into.
            title: PR title.
            body: PR body.
            draft: Whether to create as draft.

        Returns:
            Snapshot of the created PR.

        Raises:
            ValueError: If the PR URL cannot be extracted from CLI output.
        """
        self.ensure_cli()
        self.ensure_auth(project_root)
        command = [
            "gh",
            "pr",
            "create",
            "--base",
            base_branch,
            "--head",
            head_branch,
            "--title",
            title,
            "--body",
            body,
        ]
        if draft:
            command.append("--draft")
        completed = run_command(project_root, *command)
        publication_url = extract_publication_url(completed.stdout)
        if not publication_url:
            raise ValueError("`gh pr create` не вернул URL публикации.")
        return self.read_publication(
            project_root,
            reference=publication_url,
            head_branch=head_branch,
            base_branch=base_branch,
        )

    def update_publication(
        self,
        project_root: Path,
        *,
        reference: str,
        head_branch: str,
        base_branch: str,
    ) -> PublicationSnapshot:
        """Mark a GitHub pull request as ready for review.

        Args:
            project_root: Path to the project root.
            reference: PR reference (URL or number).
            head_branch: Branch containing the changes.
            base_branch: Branch to merge into.

        Returns:
            Snapshot of the updated PR.
        """
        self.ensure_cli()
        self.ensure_auth(project_root)
        run_command(project_root, "gh", "pr", "ready", reference)
        return self.read_publication(
            project_root,
            reference=reference,
            head_branch=head_branch,
            base_branch=base_branch,
        )

    def read_publication(
        self,
        project_root: Path,
        *,
        reference: str,
        head_branch: str,
        base_branch: str,
    ) -> PublicationSnapshot:
        """Read the current state of a GitHub pull request.

        Args:
            project_root: Path to the project root.
            reference: PR reference (URL or number).
            head_branch: Branch containing the changes.
            base_branch: Branch to merge into.

        Returns:
            Snapshot of the PR.
        """
        self.ensure_cli()
        self.ensure_auth(project_root)
        completed = run_command(
            project_root,
            "gh",
            "pr",
            "view",
            reference,
            "--json",
            "url,isDraft,state,headRefName,baseRefName,mergeCommit",
        )
        payload = json.loads(completed.stdout)
        merge_commit = payload.get("mergeCommit")
        merge_commit_value = DELIVERY_ROW_PLACEHOLDER
        if isinstance(merge_commit, dict):
            merge_commit_value = merge_commit.get("oid") or DELIVERY_ROW_PLACEHOLDER
        elif isinstance(merge_commit, str) and merge_commit.strip():
            merge_commit_value = merge_commit.strip()
        state = str(payload.get("state") or "").upper()
        if state == "MERGED" or merge_commit_value != DELIVERY_ROW_PLACEHOLDER:
            status = "merged"
        elif state == "CLOSED":
            status = "closed"
        elif payload.get("isDraft"):
            status = "draft"
        else:
            status = "review"
        return PublicationSnapshot(
            host="github",
            publication_type="pr",
            status=status,
            url=str(payload.get("url") or DELIVERY_ROW_PLACEHOLDER),
            head=str(payload.get("headRefName") or head_branch),
            base=str(payload.get("baseRefName") or base_branch),
            merge_commit=merge_commit_value,
        )


class GitLabAdapter(ForgeAdapter):
    """Forge adapter for GitLab using the glab CLI."""
    host_kind = "gitlab"
    cli_name = "glab"

    def ensure_auth(self, project_root: Path) -> None:
        """Verify GitLab CLI authentication for the configured hostname.

        Args:
            project_root: Path to the project root.

        Raises:
            ValueError: If glab auth status fails.
        """
        completed = run_command(
            project_root,
            "glab",
            "auth",
            "status",
            "--hostname",
            self.hostname,
            check=False,
        )
        if completed.returncode != 0:
            raise ValueError(
                f"`glab auth status --hostname {self.hostname}` завершился ошибкой. "
                "Publish-flow не должен обещать сетевые действия без валидной auth."
            )

    def create_publication(
        self,
        project_root: Path,
        *,
        head_branch: str,
        base_branch: str,
        title: str,
        body: str,
        draft: bool,
    ) -> PublicationSnapshot:
        """Create a merge request on GitLab.

        Args:
            project_root: Path to the project root.
            head_branch: Branch containing the changes.
            base_branch: Branch to merge into.
            title: MR title.
            body: MR description.
            draft: Whether to create as draft.

        Returns:
            Snapshot of the created MR.
        """
        self.ensure_cli()
        self.ensure_auth(project_root)
        command = [
            "glab",
            "mr",
            "create",
            "--source-branch",
            head_branch,
            "--target-branch",
            base_branch,
            "--title",
            title,
            "--description",
            body,
            "--yes",
        ]
        if draft:
            command.append("--draft")
        run_command(project_root, *command)
        return self.read_publication(
            project_root,
            reference=head_branch,
            head_branch=head_branch,
            base_branch=base_branch,
        )

    def update_publication(
        self,
        project_root: Path,
        *,
        reference: str,
        head_branch: str,
        base_branch: str,
    ) -> PublicationSnapshot:
        """Mark a GitLab merge request as ready for review.

        Args:
            project_root: Path to the project root.
            reference: MR reference (URL or number).
            head_branch: Branch containing the changes.
            base_branch: Branch to merge into.

        Returns:
            Snapshot of the updated MR.
        """
        self.ensure_cli()
        self.ensure_auth(project_root)
        run_command(
            project_root,
            "glab",
            "mr",
            "update",
            parse_merge_request_reference(reference, head_branch),
            "--ready",
            "--yes",
        )
        return self.read_publication(
            project_root,
            reference=reference,
            head_branch=head_branch,
            base_branch=base_branch,
        )

    def read_publication(
        self,
        project_root: Path,
        *,
        reference: str,
        head_branch: str,
        base_branch: str,
    ) -> PublicationSnapshot:
        """Read the current state of a GitLab merge request.

        Args:
            project_root: Path to the project root.
            reference: MR reference (URL or number).
            head_branch: Branch containing the changes.
            base_branch: Branch to merge into.

        Returns:
            Snapshot of the MR.
        """
        self.ensure_cli()
        self.ensure_auth(project_root)
        completed = run_command(
            project_root,
            "glab",
            "mr",
            "view",
            parse_merge_request_reference(reference, head_branch),
            "--output",
            "json",
        )
        payload = json.loads(completed.stdout)
        merge_commit_value = (
            payload.get("merge_commit_sha")
            or payload.get("mergeCommitSha")
            or DELIVERY_ROW_PLACEHOLDER
        )
        state = str(payload.get("state") or "").lower()
        is_draft = bool(payload.get("draft") or payload.get("work_in_progress"))
        if state == "merged" or merge_commit_value != DELIVERY_ROW_PLACEHOLDER:
            status = "merged"
        elif state == "closed":
            status = "closed"
        elif is_draft:
            status = "draft"
        else:
            status = "review"
        return PublicationSnapshot(
            host="gitlab",
            publication_type="mr",
            status=status,
            url=str(payload.get("web_url") or payload.get("webUrl") or DELIVERY_ROW_PLACEHOLDER),
            head=str(payload.get("source_branch") or payload.get("sourceBranch") or head_branch),
            base=str(payload.get("target_branch") or payload.get("targetBranch") or base_branch),
            merge_commit=str(merge_commit_value),
        )


# ---------------------------------------------------------------------------
# HTTPS API helper functions
# ---------------------------------------------------------------------------

_GITHUB_REMOTE_RE = re.compile(
    r"(?:https://github\.com/|git@github\.com:)(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$"
)
_GITLAB_REMOTE_RE = re.compile(
    r"(?:https://gitlab\.com/|git@gitlab\.com:)(?P<namespace>[^/]+)/(?P<project>[^/]+?)(?:\.git)?$"
)
_GITHUB_API_BASE = "https://api.github.com"
_GITLAB_API_BASE = "https://gitlab.com/api/v4"


def _parse_github_remote(url: str) -> tuple[str, str]:
    """Extract owner and repo from a GitHub remote URL.

    Args:
        url: Remote URL (HTTPS or SSH).

    Returns:
        Tuple of (owner, repo).

    Raises:
        ValueError: If the URL does not match the expected GitHub remote pattern.
    """
    match = _GITHUB_REMOTE_RE.search(url)
    if not match:
        raise ValueError(f"Не удалось извлечь owner/repo из GitHub remote URL: {url}")
    return match.group("owner"), match.group("repo")


def _parse_gitlab_remote(url: str) -> tuple[str, str]:
    """Extract namespace and project from a GitLab remote URL.

    Args:
        url: Remote URL (HTTPS or SSH).

    Returns:
        Tuple of (namespace, project). The project is the URL-encoded full path
        for subgroups (e.g. 'group/subgroup/project').

    Raises:
        ValueError: If the URL does not match the expected GitLab remote pattern.
    """
    match = _GITLAB_REMOTE_RE.search(url)
    if not match:
        raise ValueError(f"Не удалось извлечь namespace/project из GitLab remote URL: {url}")
    ns = match.group("namespace")
    proj = match.group("project")
    return ns, proj


def _http_request(
    method: str,
    url: str,
    *,
    data: dict | None = None,
    headers: dict | None = None,
    timeout: int = 30,
) -> dict:
    """Perform an HTTP request and return the parsed JSON response.

    Args:
        method: HTTP method (GET, POST, PATCH, PUT).
        url: Full URL.
        data: Optional JSON body.
        headers: Optional extra headers.
        timeout: Request timeout in seconds.

    Returns:
        Parsed JSON response as dict.

    Raises:
        ValueError: On HTTP error with details from the response.
        RuntimeError: On network or JSON parsing errors.
    """
    body_bytes = None
    if data is not None:
        body_bytes = json.dumps(data).encode("utf-8")

    all_headers = {"Accept": "application/vnd.github+json", "Content-Type": "application/json"}
    if headers:
        all_headers.update(headers)

    req = urllib.request.Request(url, data=body_bytes, headers=all_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            if not raw.strip():
                return {}
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        error_body = ""
        try:
            error_body = exc.read().decode("utf-8")
        except Exception:
            pass
        raise ValueError(
            f"HTTP {exc.code} при запросе {method} {url}: {error_body[:500]}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Сетевая ошибка при запросе {method} {url}: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Некорректный JSON-ответ от {url}: {exc}") from exc


def _resolve_remote_url(project_root: Path, remote_name: str, url: str | None) -> str:
    """Resolve the remote URL for a project.

    Args:
        project_root: Path to the project root.
        remote_name: Name of the git remote.
        url: Explicit remote URL, or None.

    Returns:
        Remote URL string.

    Raises:
        ValueError: If no remote URL can be resolved.
    """
    resolved = remote_hostname(url) or remote_url(project_root, remote_name)
    if not resolved:
        raise ValueError("Не удалось определить URL удалённого репозитория.")
    # remote_hostname returns just the hostname; we need the full URL.
    # Try both forms.
    full_url = url or remote_url(project_root, remote_name)
    if not full_url:
        raise ValueError("Не удалось определить URL удалённого репозитория.")
    return full_url


# ---------------------------------------------------------------------------
# HTTPS API adapters
# ---------------------------------------------------------------------------


class GitHubAPIAdapter(ForgeAdapter):
    """Forge adapter for GitHub using the HTTPS REST API."""
    host_kind = "github"
    cli_name = "gh-api"

    def ensure_cli(self) -> None:
        """No CLI is required; always succeeds."""
        return

    def ensure_auth(self, project_root: Path) -> None:
        """Verify that a GitHub token is available.

        Args:
            project_root: Path to the project root (unused).

        Raises:
            ValueError: If GITHUB_TOKEN is not set.
        """
        if not os.environ.get("GITHUB_TOKEN"):
            raise ValueError(
                "Переменная окружения GITHUB_TOKEN не установлена. "
                "Установите токен для аутентификации через GitHub HTTPS API."
            )

    def _auth_headers(self) -> dict:
        """Return authorization headers with the GitHub token."""
        token = os.environ.get("GITHUB_TOKEN", "")
        return {"Authorization": f"Bearer {token}"}

    def _owner_repo(self, project_root: Path, remote_name: str = "origin", url: str | None = None) -> tuple[str, str]:
        """Extract owner and repo from the project's git remote."""
        full_url = _resolve_remote_url(project_root, remote_name, url)
        return _parse_github_remote(full_url)

    def create_publication(
        self,
        project_root: Path,
        *,
        head_branch: str,
        base_branch: str,
        title: str,
        body: str,
        draft: bool,
    ) -> PublicationSnapshot:
        """Create a pull request via GitHub REST API."""
        self.ensure_cli()
        self.ensure_auth(project_root)
        owner, repo = self._owner_repo(project_root)
        api_url = f"{_GITHUB_API_BASE}/repos/{owner}/{repo}/pulls"
        payload = {
            "title": title,
            "head": head_branch,
            "base": base_branch,
            "body": body,
            "draft": draft,
        }
        pr_number = None
        try:
            response = _http_request("POST", api_url, data=payload, headers=self._auth_headers())
            pr_number = str(response.get("number", ""))
        except ValueError as exc:
            if "already exists" in str(exc).lower() or "422" in str(exc):
                pass  # PR already exists, proceed to read
            else:
                raise
        return self.read_publication(
            project_root,
            reference=pr_number or head_branch,
            head_branch=head_branch,
            base_branch=base_branch,
        )

    def update_publication(
        self,
        project_root: Path,
        *,
        reference: str,
        head_branch: str,
        base_branch: str,
    ) -> PublicationSnapshot:
        """Mark a GitHub draft PR as ready for review via REST API."""
        self.ensure_cli()
        self.ensure_auth(project_root)
        owner, repo = self._owner_repo(project_root)
        pr_number = _extract_pr_number(reference, owner, repo) or reference
        api_url = f"{_GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}"
        _http_request("PATCH", api_url, data={"draft": False}, headers=self._auth_headers())
        return self.read_publication(
            project_root,
            reference=reference,
            head_branch=head_branch,
            base_branch=base_branch,
        )

    def read_publication(
        self,
        project_root: Path,
        *,
        reference: str,
        head_branch: str,
        base_branch: str,
    ) -> PublicationSnapshot:
        """Read the current state of a GitHub pull request via REST API."""
        self.ensure_cli()
        self.ensure_auth(project_root)
        owner, repo = self._owner_repo(project_root)
        pr_number = _extract_pr_number(reference, owner, repo)
        if not pr_number:
            return _find_pr_by_head(
                owner,
                repo,
                head_branch,
                self._auth_headers(),
            )
        api_url = f"{_GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}"
        payload = _http_request("GET", api_url, headers=self._auth_headers())
        return _github_pr_to_snapshot(payload, head_branch, base_branch)


class GitLabAPIAdapter(ForgeAdapter):
    """Forge adapter for GitLab using the HTTPS REST API."""
    host_kind = "gitlab"
    cli_name = "glab-api"

    def ensure_cli(self) -> None:
        """No CLI is required; always succeeds."""
        return

    def ensure_auth(self, project_root: Path) -> None:
        """Verify that a GitLab token is available.

        Args:
            project_root: Path to the project root (unused).

        Raises:
            ValueError: If GITLAB_TOKEN is not set.
        """
        if not os.environ.get("GITLAB_TOKEN"):
            raise ValueError(
                "Переменная окружения GITLAB_TOKEN не установлена. "
                "Установите токен для аутентификации через GitLab HTTPS API."
            )

    def _auth_headers(self) -> dict:
        """Return authorization headers with the GitLab token."""
        token = os.environ.get("GITLAB_TOKEN", "")
        return {"PRIVATE-TOKEN": token}

    def _project_id(self, project_root: Path, remote_name: str = "origin", url: str | None = None) -> str:
        """Resolve the URL-encoded GitLab project path."""
        full_url = _resolve_remote_url(project_root, remote_name, url)
        ns, proj = _parse_gitlab_remote(full_url)
        return urllib.request.quote(f"{ns}/{proj}", safe="")

    def create_publication(
        self,
        project_root: Path,
        *,
        head_branch: str,
        base_branch: str,
        title: str,
        body: str,
        draft: bool,
    ) -> PublicationSnapshot:
        """Create a merge request via GitLab REST API."""
        self.ensure_cli()
        self.ensure_auth(project_root)
        project_id = self._project_id(project_root)
        api_url = f"{_GITLAB_API_BASE}/projects/{project_id}/merge_requests"
        payload = {
            "source_branch": head_branch,
            "target_branch": base_branch,
            "title": title,
            "description": body,
            "draft": draft,
        }
        try:
            _http_request("POST", api_url, data=payload, headers=self._auth_headers())
        except ValueError as exc:
            if "already exists" in str(exc).lower() or "409" in str(exc):
                pass  # MR already exists, proceed to read
            else:
                raise
        return self.read_publication(
            project_root,
            reference=head_branch,
            head_branch=head_branch,
            base_branch=base_branch,
        )

    def update_publication(
        self,
        project_root: Path,
        *,
        reference: str,
        head_branch: str,
        base_branch: str,
    ) -> PublicationSnapshot:
        """Mark a GitLab draft MR as ready via REST API."""
        self.ensure_cli()
        self.ensure_auth(project_root)
        project_id = self._project_id(project_root)
        mr_iid = parse_merge_request_reference(reference, head_branch)
        api_url = f"{_GITLAB_API_BASE}/projects/{project_id}/merge_requests/{mr_iid}"
        _http_request("PUT", api_url, data={"draft": False}, headers=self._auth_headers())
        return self.read_publication(
            project_root,
            reference=reference,
            head_branch=head_branch,
            base_branch=base_branch,
        )

    def read_publication(
        self,
        project_root: Path,
        *,
        reference: str,
        head_branch: str,
        base_branch: str,
    ) -> PublicationSnapshot:
        """Read the current state of a GitLab merge request via REST API."""
        self.ensure_cli()
        self.ensure_auth(project_root)
        project_id = self._project_id(project_root)
        mr_iid = parse_merge_request_reference(reference, head_branch)
        # Search for MR by source branch if no explicit IID
        if mr_iid == head_branch:
            api_url = (
                f"{_GITLAB_API_BASE}/projects/{project_id}/merge_requests"
                f"?source_branch={urllib.request.quote(head_branch)}"
                f"&state=opened&order_by=updated_at&sort=desc&per_page=1"
            )
            results = _http_request("GET", api_url, headers=self._auth_headers())
            if isinstance(results, list) and results:
                return _gitlab_mr_to_snapshot(results[0], head_branch, base_branch)
            return PublicationSnapshot(
                host="gitlab",
                publication_type="mr",
                status="local",
                url=DELIVERY_ROW_PLACEHOLDER,
                head=head_branch,
                base=base_branch,
                merge_commit=DELIVERY_ROW_PLACEHOLDER,
            )
        api_url = f"{_GITLAB_API_BASE}/projects/{project_id}/merge_requests/{mr_iid}"
        payload = _http_request("GET", api_url, headers=self._auth_headers())
        return _gitlab_mr_to_snapshot(payload, head_branch, base_branch)


# ---------------------------------------------------------------------------
# Snapshot construction helpers
# ---------------------------------------------------------------------------


def _extract_pr_number(reference: str, owner: str, repo: str) -> str | None:
    """Extract a GitHub PR number from a reference string."""
    import re as _re
    match = _re.search(r"github\.com/[^/]+/[^/]+/pull/(\d+)", reference)
    if match:
        return match.group(1)
    if reference.isdigit():
        return reference
    return None


def _github_pr_to_snapshot(
    payload: dict,
    head_branch: str,
    base_branch: str,
) -> PublicationSnapshot:
    """Map a GitHub API PR response to a PublicationSnapshot."""
    merge_commit = payload.get("merge_commit_sha") or DELIVERY_ROW_PLACEHOLDER
    state = str(payload.get("state") or "").upper()
    if state == "MERGED" or merge_commit != DELIVERY_ROW_PLACEHOLDER:
        status = "merged"
    elif state == "CLOSED":
        status = "closed"
    elif payload.get("draft"):
        status = "draft"
    else:
        status = "review"
    return PublicationSnapshot(
        host="github",
        publication_type="pr",
        status=status,
        url=str(payload.get("html_url") or DELIVERY_ROW_PLACEHOLDER),
        head=str(payload.get("head", {}).get("ref") or head_branch),
        base=str(payload.get("base", {}).get("ref") or base_branch),
        merge_commit=str(merge_commit),
    )


def _find_pr_by_head(
    owner: str,
    repo: str,
    head_branch: str,
    auth_headers: dict,
) -> PublicationSnapshot:
    """Find a GitHub PR by head branch reference."""
    import urllib.parse as _uparse
    api_url = (
        f"{_GITHUB_API_BASE}/repos/{owner}/{repo}/pulls"
        f"?head={owner}:{_uparse.quote(head_branch)}"
        f"&state=all&per_page=1"
    )
    results = _http_request("GET", api_url, headers=auth_headers)
    if isinstance(results, list) and results:
        return _github_pr_to_snapshot(results[0], head_branch, head_branch)
    return PublicationSnapshot(
        host="github",
        publication_type="pr",
        status="local",
        url=DELIVERY_ROW_PLACEHOLDER,
        head=head_branch,
        base="main",
        merge_commit=DELIVERY_ROW_PLACEHOLDER,
    )


def _gitlab_mr_to_snapshot(
    payload: dict,
    head_branch: str,
    base_branch: str,
) -> PublicationSnapshot:
    """Map a GitLab API MR response to a PublicationSnapshot."""
    merge_commit_value = (
        payload.get("merge_commit_sha")
        or payload.get("mergeCommitSha")
        or DELIVERY_ROW_PLACEHOLDER
    )
    state = str(payload.get("state") or "").lower()
    is_draft = bool(payload.get("draft") or payload.get("work_in_progress"))
    if state == "merged" or merge_commit_value != DELIVERY_ROW_PLACEHOLDER:
        status = "merged"
    elif state == "closed":
        status = "closed"
    elif is_draft:
        status = "draft"
    else:
        status = "review"
    return PublicationSnapshot(
        host="gitlab",
        publication_type="mr",
        status=status,
        url=str(payload.get("web_url") or DELIVERY_ROW_PLACEHOLDER),
        head=str(payload.get("source_branch") or head_branch),
        base=str(payload.get("target_branch") or base_branch),
        merge_commit=str(merge_commit_value),
    )


def _try_cli_adapter(host_kind: str, hostname: str) -> ForgeAdapter | None:
    """Try to create a CLI-based adapter, returning None if CLI is unavailable."""
    if host_kind == "github":
        adapter = GitHubAdapter(hostname)
    elif host_kind == "gitlab":
        adapter = GitLabAdapter(hostname)
    else:
        return None
    try:
        adapter.ensure_cli()
        return adapter
    except (ValueError, RuntimeError):
        return None


def _try_http_adapter(host_kind: str, hostname: str) -> ForgeAdapter | None:
    """Try to create an HTTP-based adapter, returning None if auth is unavailable."""
    if host_kind == "github":
        adapter = GitHubAPIAdapter(hostname)
    elif host_kind == "gitlab":
        adapter = GitLabAPIAdapter(hostname)
    else:
        return None
    try:
        adapter.ensure_cli()
        return adapter
    except (ValueError, RuntimeError):
        return None


def resolve_forge_adapter(project_root: Path, host_kind: str, remote_name: str, url: str | None) -> ForgeAdapter:
    """Resolve the appropriate forge adapter for a host kind and remote URL.

    Priority: CLI adapter first, then HTTP API adapter as fallback.
    Both require successful ensure_cli/ensure_auth to be returned.

    Args:
        project_root: Path to the project root.
        host_kind: Canonical host kind.
        remote_name: Name of the git remote.
        url: Explicit remote URL, or None.

    Returns:
        Initialized forge adapter.

    Raises:
        ValueError: If the hostname cannot be determined or the host kind is unsupported.
    """
    hostname = remote_hostname(url) or remote_hostname(remote_url(project_root, remote_name))
    if not hostname:
        raise ValueError("Не удалось определить hostname forge-хостинга по remote или URL.")

    # 1. Try CLI adapter first
    cli_adapter = _try_cli_adapter(host_kind, hostname)
    if cli_adapter is not None:
        try:
            cli_adapter.ensure_auth(project_root)
            return cli_adapter
        except (ValueError, RuntimeError):
            pass  # CLI present but not authenticated, fall through to HTTP

    # 2. Try HTTP adapter as fallback
    http_adapter = _try_http_adapter(host_kind, hostname)
    if http_adapter is not None:
        try:
            http_adapter.ensure_auth(project_root)
            return http_adapter
        except (ValueError, RuntimeError):
            pass

    # 3. No adapter available
    if host_kind == "github":
        raise ValueError(
            "Для GitHub не найден доступный publish-адаптер. "
            "Установите `gh` CLI и выполните `gh auth login`, "
            "либо установите переменную окружения GITHUB_TOKEN."
        )
    if host_kind == "gitlab":
        raise ValueError(
            "Для GitLab не найден доступный publish-адаптер. "
            "Установите `glab` CLI и выполните `glab auth login`, "
            "либо установите переменную окружения GITLAB_TOKEN."
        )
    raise ValueError(f"Для host `{host_kind}` нет сетевого adapter-а.")
