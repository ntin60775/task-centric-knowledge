"""Git and command helpers for task workflow runtime."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from .models import DELIVERY_ROW_PLACEHOLDER, VALID_HOSTS, VALID_PUBLICATION_TYPES


## @brief Default timeout in seconds for subprocess git and shell commands.
SUBPROCESS_TIMEOUT_SECONDS = 120


def _timeout_stream(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _timeout_completed_process(
    command: list[str],
    error: subprocess.TimeoutExpired,
    *,
    kind: str,
) -> subprocess.CompletedProcess[str]:
    command_text = " ".join(command)
    message = f"{kind} timed out after {SUBPROCESS_TIMEOUT_SECONDS}s: {command_text}"
    stdout = _timeout_stream(error.stdout)
    stderr = _timeout_stream(error.stderr)
    if stderr:
        return f"{message}\n{stderr.rstrip()}"
    if stdout:
        return f"{message}\n{stdout.rstrip()}"
    return message


## @brief Run a git command inside the project repository.
#  @param project_root Path to the project root.
#  @param args Git command arguments.
#  @param check If True, raise on non-zero exit code.
#  @return Completed subprocess result.
#  @exception RuntimeError If the command times out or fails with check=True.
def run_git(project_root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    command = ["git", "-C", str(project_root), *args]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(_timeout_completed_process(command, error, kind="git command")) from error
    if check and completed.returncode != 0:
        stderr = completed.stderr.strip()
        stdout = completed.stdout.strip()
        message = stderr or stdout or "git command failed"
        raise RuntimeError(message)
    return completed


## @brief Return the name of the current git branch.
#  @param project_root Path to the project root.
#  @return Name of the active branch.
def current_git_branch(project_root: Path) -> str:
    return run_git(project_root, "branch", "--show-current").stdout.strip()


## @brief Check whether the git worktree has no uncommitted changes.
#  @param project_root Path to the project root.
#  @return True if the worktree is clean, False otherwise.
def worktree_is_clean(project_root: Path) -> bool:
    return run_git(project_root, "status", "--porcelain").stdout.strip() == ""


## @brief List paths that have uncommitted changes in the worktree.
#  @param project_root Path to the project root.
#  @return List of dirty file paths.
def dirty_paths(project_root: Path) -> list[str]:
    output = run_git(project_root, "status", "--porcelain").stdout.splitlines()
    paths: list[str] = []
    for line in output:
        if len(line) < 4:
            continue
        candidate = line[3:]
        if " -> " in candidate:
            candidate = candidate.split(" -> ", 1)[1]
        paths.append(candidate.strip())
    return paths


## @brief Check whether a local branch exists.
#  @param project_root Path to the project root.
#  @param branch_name Name of the branch to check.
#  @return True if the branch exists, False otherwise.
def branch_exists(project_root: Path, branch_name: str) -> bool:
    completed = run_git(project_root, "rev-parse", "--verify", f"refs/heads/{branch_name}", check=False)
    return completed.returncode == 0


## @brief Check whether the repository has at least one configured remote.
#  @param project_root Path to the project root.
#  @return True if a remote exists, False otherwise.
def has_remote(project_root: Path) -> bool:
    return bool(run_git(project_root, "remote").stdout.split())


## @brief Get the URL of a named remote.
#  @param project_root Path to the project root.
#  @param remote_name Name of the remote to query (default "origin").
#  @return Remote URL, or None if the remote does not exist.
def remote_url(project_root: Path, remote_name: str = "origin") -> str | None:
    completed = run_git(project_root, "remote", "get-url", remote_name, check=False)
    if completed.returncode != 0:
        return None
    url = completed.stdout.strip()
    return url or None


## @brief Extract the hostname from a git remote URL.
#  @param url Git remote URL, or None.
#  @return Lower-case hostname, or None if the URL is empty or unparsable.
def remote_hostname(url: str | None) -> str | None:
    if not url:
        return None
    if "://" in url:
        parsed = urlparse(url)
        return parsed.hostname.lower() if parsed.hostname else None
    if url.startswith("git@") and ":" in url:
        host_part = url.split("@", 1)[1].split(":", 1)[0].strip()
        return host_part.lower() if host_part else None
    return None


## @brief Normalize a raw host value to a canonical host kind.
#  @param host_value Raw host string, or None.
#  @return Canonical host kind: "none", "github", "gitlab", or "generic".
def detect_host_kind(host_value: str | None) -> str:
    if not host_value or host_value == DELIVERY_ROW_PLACEHOLDER:
        return "none"
    lowered = host_value.lower()
    if lowered in VALID_HOSTS:
        return lowered
    if "github" in lowered:
        return "github"
    if "gitlab" in lowered:
        return "gitlab"
    return "generic"


## @brief Return the default publication type for a given host kind.
#  @param host_kind Canonical host kind.
#  @return Default publication type, or None for generic hosts.
def default_publication_type_for_host(host_kind: str) -> str | None:
    if host_kind == "none":
        return "none"
    if host_kind == "github":
        return "pr"
    if host_kind == "gitlab":
        return "mr"
    return None


## @brief Normalize and validate a publication type against a host kind.
#  @param publication_type Explicit publication type, or None to use the host default.
#  @param host_kind Canonical host kind.
#  @return Normalized publication type.
#  @exception ValueError If the publication type is invalid or required but missing.
def normalize_publication_type(publication_type: str | None, host_kind: str) -> str:
    if publication_type:
        normalized = publication_type.strip().lower()
        if normalized not in VALID_PUBLICATION_TYPES:
            raise ValueError(
                f"Некорректный тип публикации: {publication_type!r}. "
                "Допустимы `none`, `pr`, `mr`."
            )
        return normalized
    default_type = default_publication_type_for_host(host_kind)
    if default_type is None:
        raise ValueError("Для host=`generic` нужно явно указать `--publication-type`.")
    return default_type


## @brief Infer the base branch of the repository.
#  @param project_root Path to the project root.
#  @return Name of the inferred base branch.
#  @exception ValueError If the base branch cannot be determined unambiguously.
def infer_base_branch(project_root: Path) -> str:
    completed = run_git(project_root, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD", check=False)
    if completed.returncode == 0:
        ref = completed.stdout.strip()
        if ref:
            return ref.rsplit("/", 1)[-1]
    candidates = [branch for branch in ("main", "master") if branch_exists(project_root, branch)]
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        raise ValueError("Невозможно автоматически определить base-ветку: найдены и `main`, и `master`.")
    active_branch = current_git_branch(project_root)
    if active_branch and not active_branch.startswith("du/"):
        return active_branch
    raise ValueError("Не удалось определить base-ветку. Укажите `--base-branch`.")


## @brief Check whether a git ref exists.
#  @param project_root Path to the project root.
#  @param ref_name Name of the ref to verify.
#  @return True if the ref exists, False otherwise.
def ref_exists(project_root: Path, ref_name: str) -> bool:
    completed = run_git(project_root, "rev-parse", "--verify", ref_name, check=False)
    return completed.returncode == 0


## @brief Resolve the starting ref for a delivery branch.
#  @param project_root Path to the project root.
#  @param base_branch Name of the base branch.
#  @param from_ref Explicit starting ref, or None for automatic selection.
#  @return Resolved starting ref name.
#  @exception ValueError If the explicit ref does not exist or auto-selection is unsafe.
def resolve_delivery_start_ref(
    project_root: Path,
    *,
    base_branch: str,
    from_ref: str | None,
) -> str:
    if from_ref:
        if not ref_exists(project_root, from_ref):
            raise ValueError(f"Не найден `--from-ref`: {from_ref}.")
        return from_ref
    active_branch = current_git_branch(project_root)
    if active_branch == base_branch or not active_branch:
        return base_branch
    raise ValueError(
        "Нельзя безопасно выбрать стартовую точку delivery-ветки автоматически: "
        f"активная ветка `{active_branch}` не совпадает с base `{base_branch}`. "
        "Укажите `--from-ref`."
    )


## @brief Ensure a delivery branch exists and is checked out.
#  @param project_root Path to the project root.
#  @param target_branch Name of the delivery branch to ensure.
#  @param base_branch Name of the base branch.
#  @param from_ref Explicit starting ref, or None.
#  @return Action taken: "reused", "switched", or "created".
#  @exception ValueError If the worktree is dirty and a branch switch is required.
def ensure_delivery_branch(
    project_root: Path,
    *,
    target_branch: str,
    base_branch: str,
    from_ref: str | None,
) -> str:
    active_branch = current_git_branch(project_root)
    if active_branch == target_branch:
        return "reused"
    if not worktree_is_clean(project_root):
        raise ValueError("Для `start` нужен чистый worktree перед переключением delivery-ветки.")
    if branch_exists(project_root, target_branch):
        run_git(project_root, "checkout", target_branch)
        return "switched"
    start_ref = resolve_delivery_start_ref(project_root, base_branch=base_branch, from_ref=from_ref)
    run_git(project_root, "checkout", "-b", target_branch, start_ref)
    return "created"


## @brief Check whether a command is available on the system PATH.
#  @param command_name Name of the command to look up.
#  @return True if the command exists, False otherwise.
def command_exists(command_name: str) -> bool:
    return shutil.which(command_name) is not None


## @brief Run an arbitrary shell command inside the project directory.
#  @param project_root Path to the project root.
#  @param args Command and arguments.
#  @param check If True, raise on non-zero exit code.
#  @return Completed subprocess result.
#  @exception RuntimeError If the command times out or fails with check=True.
def run_command(
    project_root: Path,
    *args: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    command = list(args)
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=project_root,
            check=False,
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(_timeout_completed_process(command, error, kind="command")) from error
    if check and completed.returncode != 0:
        stderr = completed.stderr.strip()
        stdout = completed.stdout.strip()
        message = stderr or stdout or "command failed"
        raise RuntimeError(message)
    return completed
