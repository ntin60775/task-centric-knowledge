"""Bootstrap orchestration for task-centric-knowledge."""

from __future__ import annotations

import subprocess  # noqa: F401 (reserved for future use)
from dataclasses import dataclass, field
from pathlib import Path

from task_knowledge.install_runtime import (
    check,
    detect_existing_system,
    doctor_deps,
    install,
    resolve_source,
)
from task_knowledge.workflow_runtime.git_ops import (
    current_git_branch,
    dirty_paths,
    run_git,
    worktree_is_clean,
)
from task_knowledge.workflow_runtime.models import StepResult


KNOWN_KNOWLEDGE_PATTERNS = (
    "knowledge/",
    "AGENTS",
    ".task-knowledge",
)


@dataclass
class BootstrapResult:
    ok: bool
    command: str
    profile: str
    project_root: Path
    steps: list[StepResult] = field(default_factory=list)
    error: str | None = None
    dry_run: bool = False


def _is_git_repo(project_root: Path) -> bool:
    try:
        run_git(project_root, "rev-parse", "--git-dir", check=False)
        return True
    except Exception:
        return False


def _is_worktree_clean(project_root: Path) -> bool:
    return worktree_is_clean(project_root)


def _get_dirty_paths_list(project_root: Path) -> list[str]:
    return dirty_paths(project_root)


def _only_knowledge_dirty(project_root: Path) -> bool:
    dirty = _get_dirty_paths_list(project_root)
    if not dirty:
        return False
    for path in dirty:
        if not any(path.startswith(pattern) for pattern in KNOWN_KNOWLEDGE_PATTERNS):
            return False
    return True


def _commit_knowledge_files(project_root: Path, dry_run: bool) -> list[StepResult]:
    results: list[StepResult] = []
    if dry_run:
        results.append(StepResult("git_commit", "skipped", "dry-run: commit knowledge files", str(project_root)))
        return results
    knowledge_paths = [p for p in _get_dirty_paths_list(project_root) if any(p.startswith(pat) for pat in KNOWN_KNOWLEDGE_PATTERNS)]
    if not knowledge_paths:
        results.append(StepResult("git_commit", "skipped", "no knowledge files to commit", str(project_root)))
        return results
    try:
        run_git(project_root, "add", *knowledge_paths)
        run_git(project_root, "commit", "-m", "task-knowledge bootstrap: initial knowledge setup")
        results.append(StepResult("git_commit", "ok", "Knowledge files committed", str(project_root)))
    except RuntimeError as e:
        results.append(StepResult("git_commit", "error", str(e), str(project_root)))
    return results


def _detect_system_classification(project_root: Path) -> tuple[str, str]:
    report = detect_existing_system(project_root)
    if report is None or not hasattr(report, 'classification'):
        return ("unknown", "unknown")
    return report.classification, report.recommendation


def _bootstrap_preflight(project_root: Path, profile: str) -> BootstrapResult:
    results: list[StepResult] = []
    if not project_root.exists():
        return BootstrapResult(
            ok=False,
            command="bootstrap",
            profile=profile,
            project_root=project_root,
            steps=results,
            error=f"project-root does not exist: {project_root}",
        )
    if not _is_git_repo(project_root):
        return BootstrapResult(
            ok=False,
            command="bootstrap",
            profile=profile,
            project_root=project_root,
            steps=results,
            error="Проект не является git-репозиторием. Bootstrap требует git.",
        )
    results.append(StepResult("git", "ok", "Git repository confirmed", str(project_root)))
    if _is_worktree_clean(project_root):
        results.append(StepResult("worktree", "ok", "Worktree is clean", str(project_root)))
    else:
        if _only_knowledge_dirty(project_root):
            results.append(StepResult("worktree", "warning", "Worktree has knowledge-only changes", str(project_root)))
        else:
            return BootstrapResult(
                ok=False,
                command="bootstrap",
                profile=profile,
                project_root=project_root,
                steps=results,
                error="Worktree is dirty with non-knowledge changes. Commit them before bootstrap.",
            )
    return BootstrapResult(ok=True, command="bootstrap", profile=profile, project_root=project_root, steps=results)


def _bootstrap_install(project_root: Path, source_root: Path, profile: str, dry_run: bool) -> BootstrapResult:
    results: list[StepResult] = []
    check_result = check(project_root, source_root, profile)
    if not check_result["ok"]:
        results.append(StepResult("install_check", "error", "install check failed", str(project_root)))
        return BootstrapResult(
            ok=False,
            command="bootstrap",
            profile=profile,
            project_root=project_root,
            steps=results,
            error="install check failed",
        )
    results.append(StepResult("install_check", "ok", "install check passed", str(project_root)))

    sys_class, _ = _detect_system_classification(project_root)
    if sys_class in ("foreign_system", "mixed_system"):
        return BootstrapResult(
            ok=False,
            command="bootstrap",
            profile=profile,
            project_root=project_root,
            steps=results,
            error=f"Existing system classification: {sys_class}. Bootstrap requires migration first.",
        )
    if sys_class == "partial_knowledge":
        return BootstrapResult(
            ok=False,
            command="bootstrap",
            profile=profile,
            project_root=project_root,
            steps=results,
            error=f"Existing system classification: {sys_class}. Manual resolution required before bootstrap.",
        )

    if dry_run:
        results.append(StepResult("install_apply", "skipped", "dry-run: would run install apply --force", str(project_root)))
        return BootstrapResult(ok=True, command="bootstrap", profile=profile, project_root=project_root, steps=results, dry_run=True)

    install_result = install(project_root, source_root, profile, force=True, existing_system_mode="adopt")
    if not install_result["ok"]:
        results.append(StepResult("install_apply", "error", "install apply failed", str(project_root)))
        return BootstrapResult(
            ok=False,
            command="bootstrap",
            profile=profile,
            project_root=project_root,
            steps=results,
            error="install apply failed",
        )
    results.append(StepResult("install_apply", "ok", "install apply completed", str(project_root)))
    return BootstrapResult(ok=True, command="bootstrap", profile=profile, project_root=project_root, steps=results, dry_run=False)


def _bootstrap_doctor(project_root: Path, source_root: Path, profile: str) -> BootstrapResult:
    results: list[StepResult] = []
    doctor_result = doctor_deps(project_root, source_root, profile)
    if not doctor_result["ok"]:
        results.append(StepResult("doctor_deps", "error", "doctor-deps check failed", str(project_root)))
        return BootstrapResult(
            ok=False,
            command="bootstrap",
            profile=profile,
            project_root=project_root,
            steps=results,
            error="doctor-deps check failed",
        )
    results.append(StepResult("doctor_deps", "ok", "doctor-deps check passed", str(project_root)))
    return BootstrapResult(ok=True, command="bootstrap", profile=profile, project_root=project_root, steps=results)


def _copy_template(src: Path, dst: Path, subs: dict[str, str]) -> None:
    content = src.read_text()
    for k, v in subs.items():
        content = content.replace(k, v)
    dst.write_text(content)


def _bootstrap_first_task(
    project_root: Path,
    task_id: str,
    task_name: str,
    dry_run: bool,
) -> BootstrapResult:
    results: list[StepResult] = []
    task_dir = project_root / "knowledge" / "tasks" / f"TASK-{task_id}"
    slug = task_name.lower().replace(" ", "-").replace("_", "-")
    task_branch = f"task/{task_id.lower()}-{slug}"
    today = __import__("datetime").date.today().isoformat()

    template_tasks_dir = project_root / "knowledge" / "tasks" / "_templates"
    task_template = template_tasks_dir / "task.md"
    plan_template = template_tasks_dir / "plan.md"

    if dry_run:
        results.append(StepResult("task_dir", "skipped", f"dry-run: would create {task_dir}", str(project_root)))
        results.append(StepResult("task_files", "skipped", f"dry-run: would copy templates to {task_dir}", str(project_root)))
        results.append(StepResult("task_branch", "skipped", f"dry-run: would create branch {task_branch}", str(project_root)))
        return BootstrapResult(ok=True, command="bootstrap", profile="generic", project_root=project_root, steps=results, dry_run=True)

    try:
        task_dir.mkdir(parents=True, exist_ok=True)
        results.append(StepResult("task_dir", "ok", f"Created task directory: {task_dir}", str(task_dir)))
    except OSError as e:
        results.append(StepResult("task_dir", "error", f"Failed to create task directory: {e}", str(project_root)))
        return BootstrapResult(ok=False, command="bootstrap", profile="generic", project_root=project_root, steps=results, error=str(e))

    if task_template.exists():
        _copy_template(
            task_template,
            task_dir / "task.md",
            {
                "TASK-2026-0001": f"TASK-{task_id}",
                "2026-0001": task_id,
                "zapolnit-korotkim-slug": slug,
                "Короткое описание задачи": task_name,
                "task/task-2026-0001-zapolnit-korotkim-slug": task_branch,
                "YYYY-MM-DD": today,
            },
        )
        results.append(StepResult("task_files", "ok", f"Copied task.md template", str(task_dir / "task.md")))
    else:
        task_md = task_dir / "task.md"
        task_md.write_text(
            f"# Карточка задачи TASK-{task_id}\n\n"
            f"## Паспорт\n\n| Поле | Значение |\n|------|----------|\n"
            f"| ID задачи | `TASK-{task_id}` |\n"
            f"| Parent ID | `—` |\n"
            f"| Краткое имя | `{slug}` |\n"
            f"| Человекочитаемое описание | {task_name} |\n"
            f"| Статус | `в работе` |\n"
            f"| Приоритет | `средний` |\n"
            f"| Ответственный | `не назначен` |\n"
            f"| Ветка | `{task_branch}` |\n"
            f"| Дата создания | `{today}` |\n"
            f"| Дата обновления | `{today}` |\n\n"
            f"## Цель\n\nКратко описать ожидаемый результат.\n\n"
            f"## Контур публикации\n\n"
            f"| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус |\n"
            f"|---------|------------|------|------|------|----------------|--------|\n"
            f"| `—` | — | `—` | `—` | `none` | `none` | `planned` |\n"
        )
        results.append(StepResult("task_files", "ok", f"Created minimal task.md", str(task_md)))

    if plan_template.exists():
        _copy_template(
            plan_template,
            task_dir / "plan.md",
            {
                "TASK-2026-0001": f"TASK-{task_id}",
                "2026-0001": task_id,
                "YYYY-MM-DD": today,
            },
        )
        results.append(StepResult("task_files", "ok", f"Copied plan.md template", str(task_dir / "plan.md")))

    return BootstrapResult(ok=True, command="bootstrap", profile="generic", project_root=project_root, steps=results, dry_run=False)


def _bootstrap_sync(
    project_root: Path,
    task_dir: Path,
    dry_run: bool,
) -> BootstrapResult:
    results: list[StepResult] = []
    task_file = task_dir / "task.md"
    if not task_file.exists():
        if dry_run:
            results.append(StepResult("sync", "skipped", "dry-run: task.md would be created by bootstrap", str(task_dir)))
            return BootstrapResult(ok=True, command="bootstrap", profile="generic", project_root=project_root, steps=results, dry_run=True)
        results.append(StepResult("sync", "error", f"task.md not found: {task_file}", str(task_dir)))
        return BootstrapResult(
            ok=False,
            command="bootstrap",
            profile="generic",
            project_root=project_root,
            steps=results,
            error=f"task.md not found: {task_file}",
        )

    if dry_run:
        results.append(StepResult("sync", "skipped", "dry-run: would run workflow sync", str(task_dir)))
        return BootstrapResult(ok=True, command="bootstrap", profile="generic", project_root=project_root, steps=results, dry_run=True)

    from task_knowledge.workflow_runtime import sync_task
    sync_result = sync_task(
        project_root,
        task_dir,
        create_branch=True,
        register_if_missing=True,
        summary=None,
        branch_name=None,
        inherit_branch_from_parent=False,
    )
    if sync_result["ok"]:
        results.append(StepResult("sync", "ok", f"Workflow synced: branch={sync_result.get('branch')}", str(task_dir)))
    else:
        results.append(StepResult("sync", "error", "sync failed", str(task_dir)))
    return BootstrapResult(ok=True, command="bootstrap", profile="generic", project_root=project_root, steps=results, dry_run=False)


def bootstrap(
    project_root: Path,
    *,
    profile: str = "generic",
    dry_run: bool = False,
    first_task_id: str | None = None,
    first_task_name: str | None = None,
) -> BootstrapResult:
    """Perform full bootstrap of task-centric-knowledge in a project.

    Args:
        project_root: Absolute path to project root.
        profile: Managed-block profile (`generic` or `1c`).
        dry_run: If True, show planned actions without mutating.
        first_task_id: Task ID for the first task (e.g. `2026-0001`).
        first_task_name: Short name slug for the first task.

    Returns:
        BootstrapResult with steps and status.
    """
    project_root = project_root.resolve()
    source_root = resolve_source(None)
    if source_root is None or not source_root.exists():
        return BootstrapResult(
            ok=False,
            command="bootstrap",
            profile=profile,
            project_root=project_root,
            steps=[],
            error="source_root resolve failed: source is None or does not exist",
        )

    preflight = _bootstrap_preflight(project_root, profile)
    if not preflight.ok:
        return preflight

    install_result = _bootstrap_install(project_root, source_root, profile, dry_run)
    if not install_result.ok:
        return install_result

    if _only_knowledge_dirty(project_root):
        commit_results = _commit_knowledge_files(project_root, dry_run)
        preflight.steps.extend(commit_results)

    doctor_result = _bootstrap_doctor(project_root, source_root, profile)
    if not doctor_result.ok:
        return doctor_result
    preflight.steps.extend(doctor_result.steps)

    task_id = first_task_id or "2026-0001"
    task_name = first_task_name or "initial-setup"

    first_task_result = _bootstrap_first_task(project_root, task_id, task_name, dry_run)
    if not first_task_result.ok:
        return first_task_result
    preflight.steps.extend(first_task_result.steps)

    task_dir = project_root / "knowledge" / "tasks" / f"TASK-{task_id}"
    sync_result = _bootstrap_sync(project_root, task_dir, dry_run)
    preflight.steps.extend(sync_result.steps)
    if not sync_result.ok:
        preflight.ok = False
        preflight.error = sync_result.error
        return preflight

    preflight.ok = True
    preflight.dry_run = dry_run
    return preflight
