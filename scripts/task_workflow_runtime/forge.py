"""Forge adapter integrations for publish flow."""

from __future__ import annotations

import json
from pathlib import Path

from .git_ops import command_exists, remote_hostname, remote_url, run_command
from .models import DELIVERY_ROW_PLACEHOLDER, MERGE_REQUEST_URL_RE, PublicationSnapshot


def extract_publication_url(output_text: str) -> str | None:
    for line in reversed(output_text.splitlines()):
        candidate = line.strip()
        if candidate.startswith("http://") or candidate.startswith("https://"):
            return candidate
    return None


def parse_merge_request_reference(reference: str, head_branch: str) -> str:
    match = MERGE_REQUEST_URL_RE.search(reference)
    if match:
        return match.group("number")
    return head_branch


class ForgeAdapter:
    host_kind = "generic"
    cli_name = ""

    def __init__(self, hostname: str) -> None:
        self.hostname = hostname

    def ensure_cli(self) -> None:
        if not command_exists(self.cli_name):
            raise ValueError(f"Для host `{self.host_kind}` не найден CLI `{self.cli_name}`.")

    def ensure_auth(self, project_root: Path) -> None:
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
        raise NotImplementedError

    def update_publication(
        self,
        project_root: Path,
        *,
        reference: str,
        head_branch: str,
        base_branch: str,
    ) -> PublicationSnapshot:
        raise NotImplementedError

    def read_publication(
        self,
        project_root: Path,
        *,
        reference: str,
        head_branch: str,
        base_branch: str,
    ) -> PublicationSnapshot:
        raise NotImplementedError


class GitHubAdapter(ForgeAdapter):
    host_kind = "github"
    cli_name = "gh"

    def ensure_auth(self, project_root: Path) -> None:
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
    host_kind = "gitlab"
    cli_name = "glab"

    def ensure_auth(self, project_root: Path) -> None:
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


def resolve_forge_adapter(project_root: Path, host_kind: str, remote_name: str, url: str | None) -> ForgeAdapter:
    hostname = remote_hostname(url) or remote_hostname(remote_url(project_root, remote_name))
    if not hostname:
        raise ValueError("Не удалось определить hostname forge-хостинга по remote или URL.")
    if host_kind == "github":
        return GitHubAdapter(hostname)
    if host_kind == "gitlab":
        return GitLabAdapter(hostname)
    raise ValueError(f"Для host `{host_kind}` нет сетевого adapter-а.")
