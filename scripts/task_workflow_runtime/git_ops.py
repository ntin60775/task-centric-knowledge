"""Git and command helpers for task workflow runtime."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from .models import DELIVERY_ROW_PLACEHOLDER, VALID_HOSTS, VALID_PUBLICATION_TYPES


def run_git(project_root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["git", "-C", str(project_root), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if check and completed.returncode != 0:
        stderr = completed.stderr.strip()
        stdout = completed.stdout.strip()
        message = stderr or stdout or "git command failed"
        raise RuntimeError(message)
    return completed


def current_git_branch(project_root: Path) -> str:
    return run_git(project_root, "branch", "--show-current").stdout.strip()


def worktree_is_clean(project_root: Path) -> bool:
    return run_git(project_root, "status", "--porcelain").stdout.strip() == ""


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


def branch_exists(project_root: Path, branch_name: str) -> bool:
    completed = run_git(project_root, "rev-parse", "--verify", f"refs/heads/{branch_name}", check=False)
    return completed.returncode == 0


def has_remote(project_root: Path) -> bool:
    return bool(run_git(project_root, "remote").stdout.split())


def remote_url(project_root: Path, remote_name: str = "origin") -> str | None:
    completed = run_git(project_root, "remote", "get-url", remote_name, check=False)
    if completed.returncode != 0:
        return None
    url = completed.stdout.strip()
    return url or None


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


def default_publication_type_for_host(host_kind: str) -> str | None:
    if host_kind == "none":
        return "none"
    if host_kind == "github":
        return "pr"
    if host_kind == "gitlab":
        return "mr"
    return None


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


def ref_exists(project_root: Path, ref_name: str) -> bool:
    completed = run_git(project_root, "rev-parse", "--verify", ref_name, check=False)
    return completed.returncode == 0


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


def command_exists(command_name: str) -> bool:
    return shutil.which(command_name) is not None


def run_command(
    project_root: Path,
    *args: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        list(args),
        capture_output=True,
        text=True,
        cwd=project_root,
        check=False,
    )
    if check and completed.returncode != 0:
        stderr = completed.stderr.strip()
        stdout = completed.stdout.strip()
        message = stderr or stdout or "command failed"
        raise RuntimeError(message)
    return completed
