"""Local-only finalize flow for task branches."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Sequence

from .git_ops import branch_exists, current_git_branch, has_remote, infer_base_branch, run_git
from .models import (
    DELIVERY_ROW_PLACEHOLDER,
    FINAL_TASK_STATUSES,
    PLACEHOLDER_BRANCH_VALUES,
    DeliveryUnit,
    StepResult,
    default_branch_name,
)
from .registry_sync import collect_delivery_units, update_registry
from .task_markdown import derive_goal_summary_from_lines, read_task_fields, task_summary_from_fields, update_task_file


OPEN_DELIVERY_STATUSES = {"planned", "local", "draft", "review"}
FINAL_STAGE_TEXT = (
    "Локальный finalize выполнен: task-ветка влита в base-ветку, "
    "рабочий контекст переведён на base-ветку, `push` остаётся отдельным шагом."
)


@dataclass(frozen=True)
class FinalizeContext:
    project_root: Path
    task_dir: Path
    task_file: Path
    registry_path: Path
    lines: list[str]
    fields: dict[str, str]
    task_id: str
    short_name: str
    active_branch: str | None
    selected_base_branch: str
    task_branch: str
    summary: str


@dataclass
class FinalizeProgress:
    results: list[StepResult]
    commit_created: bool = False
    commit_id: str | None = None
    merge_commit: str | None = None


@dataclass(frozen=True)
class _OriginalTruth:
    task_text: str
    registry_text: str


Blocker = dict[str, str | None]


def _blocker(key: str, detail: str, *, next_action: str, path: str | None = None) -> Blocker:
    return {
        "key": key,
        "status": "blocked",
        "detail": detail,
        "path": path,
        "next_action": next_action,
    }


def _head_commit(project_root: Path, ref_name: str = "HEAD") -> str:
    return run_git(project_root, "rev-parse", ref_name).stdout.strip()


def _is_ancestor(project_root: Path, ancestor: str, descendant: str) -> bool:
    completed = run_git(project_root, "merge-base", "--is-ancestor", ancestor, descendant, check=False)
    if completed.returncode == 0:
        return True
    if completed.returncode == 1:
        return False
    message = completed.stderr.strip() or completed.stdout.strip() or "git merge-base failed"
    raise RuntimeError(message)


def _has_staged_changes(project_root: Path) -> bool:
    completed = run_git(project_root, "diff", "--cached", "--quiet", check=False)
    if completed.returncode == 0:
        return False
    if completed.returncode == 1:
        return True
    message = completed.stderr.strip() or completed.stdout.strip() or "git diff --cached failed"
    raise RuntimeError(message)


def _resolve_task_branch(fields: dict[str, str]) -> str:
    recorded_branch = fields.get("Ветка", "").strip()
    if recorded_branch not in PLACEHOLDER_BRANCH_VALUES:
        return recorded_branch
    task_id = fields.get("ID задачи", "").strip()
    short_name = fields.get("Краткое имя", "").strip()
    if not task_id or not short_name:
        raise ValueError("В task.md должны быть заполнены поля `ID задачи` и `Краткое имя`.")
    return default_branch_name(task_id, short_name)


def _default_commit_message(task_id: str, summary: str | None) -> str:
    suffix = (summary or "finalize local task lifecycle").replace("\n", " ").strip()
    if not suffix:
        suffix = "finalize local task lifecycle"
    return f"{task_id}: {suffix}"


def _safe_current_git_branch(project_root: Path) -> str | None:
    try:
        return current_git_branch(project_root)
    except Exception:  # noqa: BLE001
        return None


def _safe_has_remote(project_root: Path) -> bool:
    try:
        return has_remote(project_root)
    except Exception:  # noqa: BLE001
        return False


def _detect_remote_presence(project_root: Path) -> tuple[bool, str | None]:
    try:
        return has_remote(project_root), None
    except Exception as error:  # noqa: BLE001
        return False, str(error)


def _runtime_failure_payload(
    *,
    task_id: str,
    task_dir: Path,
    active_branch: str | None,
    task_branch: str | None,
    base_branch: str | None,
    commit_created: bool,
    commit_id: str | None,
    detail: str,
    next_action: str,
    results: list[StepResult],
    project_root: Path,
) -> dict[str, object]:
    return {
        "ok": False,
        "outcome": "blocked",
        "task_id": task_id,
        "task_dir": str(task_dir),
        "action": "finalize",
        "branch": active_branch or DELIVERY_ROW_PLACEHOLDER,
        "branch_action": "blocked",
        "task_branch": task_branch or DELIVERY_ROW_PLACEHOLDER,
        "base_branch": base_branch or DELIVERY_ROW_PLACEHOLDER,
        "commit_created": commit_created,
        "commit_id": commit_id,
        "merge_commit": None,
        "remote_present": _safe_has_remote(project_root),
        "results": [asdict(item) for item in results],
        "blockers": [_blocker("git_runtime_failure", detail, next_action=next_action)],
        "next_actions": [next_action],
    }


def _resolve_task_dir(project_root: Path, task_dir: Path) -> Path:
    if task_dir.is_absolute():
        return task_dir.resolve()
    return (project_root / task_dir).resolve()


def _load_finalize_context(project_root: Path, task_dir: Path, base_branch: str | None) -> FinalizeContext:
    project_root = project_root.resolve()
    task_dir = _resolve_task_dir(project_root, task_dir)
    task_file = task_dir / "task.md"
    if not task_file.exists():
        raise ValueError(f"Не найден task.md по пути {task_file}.")

    lines, fields = read_task_fields(task_file)
    task_id = fields.get("ID задачи", "").strip()
    short_name = fields.get("Краткое имя", "").strip()
    if not task_id or not short_name:
        raise ValueError("В task.md должны быть заполнены поля `ID задачи` и `Краткое имя`.")

    return FinalizeContext(
        project_root=project_root,
        task_dir=task_dir,
        task_file=task_file,
        registry_path=project_root / "knowledge/tasks/registry.md",
        lines=lines,
        fields=fields,
        task_id=task_id,
        short_name=short_name,
        active_branch=current_git_branch(project_root),
        selected_base_branch=base_branch or infer_base_branch(project_root),
        task_branch=_resolve_task_branch(fields),
        summary=task_summary_from_fields(fields) or derive_goal_summary_from_lines(lines) or short_name,
    )


def _collect_finalize_blockers(ctx: FinalizeContext, delivery_units: Sequence[DeliveryUnit]) -> list[Blocker]:
    blockers: list[Blocker] = []
    blockers.extend(_branch_context_blockers(ctx))
    blockers.extend(_delivery_unit_blockers(ctx, delivery_units))
    blockers.extend(_base_fast_forward_blockers(ctx))
    return blockers


def _branch_context_blockers(ctx: FinalizeContext) -> list[Blocker]:
    if not ctx.active_branch:
        return [
            _blocker(
                "active_branch",
                "Finalize требует явной checkout-ветки задачи.",
                next_action="Переключитесь на task-ветку задачи и повторите finalize.",
            )
        ]
    if ctx.active_branch == ctx.selected_base_branch:
        return [
            _blocker(
                "active_branch",
                "Finalize нельзя запускать из base-ветки.",
                next_action=f"Переключитесь на `{ctx.task_branch}` и повторите finalize.",
            )
        ]
    if ctx.active_branch != ctx.task_branch:
        return [
            _blocker(
                "task_branch_mismatch",
                f"Текущая ветка `{ctx.active_branch}` не совпадает с task-контекстом `{ctx.task_branch}`.",
                next_action="Синхронизируйте поле `Ветка` через workflow sync или переключитесь на корректную task-ветку.",
            )
        ]
    return []


def _delivery_unit_blockers(ctx: FinalizeContext, delivery_units: Sequence[DeliveryUnit]) -> list[Blocker]:
    open_units = [unit for unit in delivery_units if unit.status in OPEN_DELIVERY_STATUSES]
    if not open_units:
        return []
    unit_ids = ", ".join(unit.unit_id for unit in open_units)
    return [
        _blocker(
            "open_delivery_units",
            f"Нельзя завершить задачу, пока delivery units не закрыты: {unit_ids}.",
            next_action="Доведите все delivery units до `merged` или `closed`, затем повторите finalize.",
            path=str(ctx.task_file),
        )
    ]


def _base_fast_forward_blockers(ctx: FinalizeContext) -> list[Blocker]:
    if not branch_exists(ctx.project_root, ctx.selected_base_branch):
        return [
            _blocker(
                "base_branch_missing",
                f"Base-ветка `{ctx.selected_base_branch}` не найдена локально.",
                next_action="Создайте или явно укажите существующую base-ветку через `--base-branch`.",
            )
        ]
    if ctx.active_branch and ctx.active_branch != ctx.selected_base_branch:
        if not _is_ancestor(ctx.project_root, ctx.selected_base_branch, ctx.active_branch):
            return [
                _blocker(
                    "base_branch_diverged",
                    f"Base-ветка `{ctx.selected_base_branch}` ушла вперёд и fast-forward finalize небезопасен.",
                    next_action="Сначала вручную синхронизируйте task-ветку с base-веткой, затем повторите finalize.",
                )
            ]
    return []


def _blocked_payload(ctx: FinalizeContext, blockers: Sequence[Blocker]) -> dict[str, object]:
    return {
        "ok": False,
        "outcome": "blocked",
        "task_id": ctx.task_id,
        "task_dir": str(ctx.task_dir),
        "action": "finalize",
        "branch": ctx.active_branch or DELIVERY_ROW_PLACEHOLDER,
        "branch_action": "blocked",
        "task_branch": ctx.task_branch,
        "base_branch": ctx.selected_base_branch,
        "commit_created": False,
        "merge_commit": None,
        "remote_present": _safe_has_remote(ctx.project_root),
        "results": [],
        "blockers": list(blockers),
        "next_actions": [item["next_action"] for item in blockers],
    }


def _snapshot_original_truth(ctx: FinalizeContext) -> _OriginalTruth:
    return _OriginalTruth(
        task_text=ctx.task_file.read_text(encoding="utf-8"),
        registry_text=ctx.registry_path.read_text(encoding="utf-8"),
    )


def _sync_final_task_truth(ctx: FinalizeContext, today_value: str, results: list[StepResult]) -> dict[str, str]:
    if ctx.fields.get("Статус", "").strip() not in FINAL_TASK_STATUSES:
        updated_fields = update_task_file(
            ctx.task_file,
            ctx.selected_base_branch,
            today=today_value,
            status="завершена",
            current_stage=FINAL_STAGE_TEXT,
        )
        detail = "task.md синхронизирован под итоговое локальное состояние задачи."
    else:
        updated_fields = update_task_file(
            ctx.task_file,
            ctx.selected_base_branch,
            today=today_value,
            status=ctx.fields.get("Статус"),
            current_stage=FINAL_STAGE_TEXT,
        )
        detail = "task.md уже был в финальном статусе; branch/date синхронизированы под итоговое локальное состояние."
    results.append(StepResult("task_metadata", "ok", detail, str(ctx.task_file)))

    update_registry(
        ctx.project_root,
        ctx.task_dir,
        updated_fields,
        branch_name=ctx.selected_base_branch,
        register_if_missing=False,
        summary=None,
    )
    results.append(
        StepResult(
            "registry",
            "ok",
            "registry.md синхронизирован с финальным локальным branch-state задачи.",
            str(ctx.registry_path),
        )
    )
    return updated_fields


def _commit_final_task_truth(
    ctx: FinalizeContext,
    *,
    commit_message: str | None,
    results: list[StepResult],
) -> tuple[bool, str | None]:
    run_git(ctx.project_root, "add", "-A")
    if not _has_staged_changes(ctx.project_root):
        results.append(
            StepResult(
                "commit",
                "ok",
                "Новых staged-изменений нет; finalize продолжен без дополнительного commit.",
                None,
            )
        )
        return False, None

    run_git(ctx.project_root, "commit", "-m", commit_message or _default_commit_message(ctx.task_id, ctx.summary))
    commit_id = _head_commit(ctx.project_root)
    results.append(
        StepResult(
            "commit",
            "ok",
            "Task-scoped commit создан перед локальным finalize.",
            commit_id,
        )
    )
    return True, commit_id


def _merge_finalized_task_branch(ctx: FinalizeContext, results: list[StepResult]) -> str:
    run_git(ctx.project_root, "checkout", ctx.selected_base_branch)
    results.append(
        StepResult(
            "checkout",
            "ok",
            f"Переключение на base-ветку `{ctx.selected_base_branch}` выполнено.",
            ctx.selected_base_branch,
        )
    )
    run_git(ctx.project_root, "merge", "--ff-only", ctx.task_branch)
    merge_commit = _head_commit(ctx.project_root)
    results.append(
        StepResult(
            "merge",
            "ok",
            f"Local finalize завершён через fast-forward merge `{ctx.task_branch}` -> `{ctx.selected_base_branch}`.",
            merge_commit,
        )
    )
    return merge_commit


def _rollback_uncommitted_truth(ctx: FinalizeContext, original_truth: _OriginalTruth, results: list[StepResult]) -> None:
    ctx.task_file.write_text(original_truth.task_text, encoding="utf-8")
    ctx.registry_path.write_text(original_truth.registry_text, encoding="utf-8")
    results.append(
        StepResult(
            "rollback",
            "ok",
            "Task truth откатан после runtime-сбоя до создания commit.",
            str(ctx.task_file),
        )
    )


def _finalize_failure_payload(ctx: FinalizeContext, progress: FinalizeProgress, error: Exception) -> dict[str, object]:
    current_branch = _safe_current_git_branch(ctx.project_root) or ctx.active_branch or DELIVERY_ROW_PLACEHOLDER
    detail = f"Local finalize остановлен из-за ошибки git/runtime: {error}"
    if not progress.commit_created:
        next_action = "Повторите finalize после устранения ошибки доступа к git; task truth уже восстановлен."
    else:
        next_action = "Проверьте локальный finalize commit и повторите merge/checkout после устранения ошибки git."
    return {
        "ok": False,
        "outcome": "blocked",
        "task_id": ctx.task_id,
        "task_dir": str(ctx.task_dir),
        "action": "finalize",
        "branch": current_branch,
        "branch_action": "blocked",
        "task_branch": ctx.task_branch,
        "base_branch": ctx.selected_base_branch,
        "commit_created": progress.commit_created,
        "commit_id": progress.commit_id,
        "merge_commit": None,
        "remote_present": _safe_has_remote(ctx.project_root),
        "results": [asdict(item) for item in progress.results],
        "blockers": [_blocker("git_runtime_failure", detail, next_action=next_action)],
        "next_actions": [next_action],
    }


def _append_remote_note(ctx: FinalizeContext, results: list[StepResult]) -> bool:
    remote_present, remote_error = _detect_remote_presence(ctx.project_root)
    if remote_error:
        results.append(
            StepResult(
                "remote",
                "warning",
                f"Не удалось проверить связанный remote после local finalize: {remote_error}",
                None,
            )
        )
        return False
    if remote_present:
        results.append(
            StepResult(
                "remote",
                "ok",
                "Связанный remote обнаружен; push при необходимости выполняется отдельным шагом после local finalize.",
                None,
            )
        )
    return remote_present


def _finalize_success_payload(
    ctx: FinalizeContext,
    progress: FinalizeProgress,
    *,
    remote_present: bool,
) -> dict[str, object]:
    return {
        "ok": True,
        "outcome": "finalized",
        "task_id": ctx.task_id,
        "task_dir": str(ctx.task_dir),
        "action": "finalize",
        "branch": ctx.selected_base_branch,
        "branch_action": "finalized",
        "task_branch": ctx.task_branch,
        "base_branch": ctx.selected_base_branch,
        "commit_created": progress.commit_created,
        "commit_id": progress.commit_id,
        "merge_commit": progress.merge_commit,
        "remote_present": remote_present,
        "results": [asdict(item) for item in progress.results],
        "blockers": [],
        "next_actions": [],
    }


def finalize_task(
    project_root: Path,
    task_dir: Path,
    *,
    base_branch: str | None,
    commit_message: str | None,
    today: str | None = None,
) -> dict[str, object]:
    project_root = project_root.resolve()
    resolved_task_dir = _resolve_task_dir(project_root, task_dir)

    try:
        ctx = _load_finalize_context(project_root, resolved_task_dir, base_branch)
    except Exception as error:  # noqa: BLE001
        task_id = resolved_task_dir.name
        task_branch: str | None = None
        task_file = resolved_task_dir / "task.md"
        if task_file.exists():
            try:
                _, fields = read_task_fields(task_file)
                task_id = fields.get("ID задачи", "").strip() or task_id
                task_branch = _resolve_task_branch(fields)
            except Exception:  # noqa: BLE001
                task_branch = None
        detail = f"Local finalize остановлен из-за ошибки git/runtime: {error}"
        next_action = "Повторите finalize после устранения ошибки доступа к git и повторной проверки branch/base preflight."
        return _runtime_failure_payload(
            task_id=task_id,
            task_dir=resolved_task_dir,
            active_branch=_safe_current_git_branch(project_root),
            task_branch=task_branch,
            base_branch=base_branch,
            commit_created=False,
            commit_id=None,
            detail=detail,
            next_action=next_action,
            results=[],
            project_root=project_root,
        )

    try:
        delivery_units = collect_delivery_units(ctx.project_root, ctx.task_dir, ctx.fields, ctx.lines)
        blockers = _collect_finalize_blockers(ctx, delivery_units)
    except Exception as error:  # noqa: BLE001
        detail = f"Local finalize остановлен из-за ошибки git/runtime: {error}"
        next_action = "Повторите finalize после устранения ошибки доступа к git и повторной проверки preflight-инвариантов."
        return _runtime_failure_payload(
            task_id=ctx.task_id,
            task_dir=ctx.task_dir,
            active_branch=ctx.active_branch,
            task_branch=ctx.task_branch,
            base_branch=ctx.selected_base_branch,
            commit_created=False,
            commit_id=None,
            detail=detail,
            next_action=next_action,
            results=[],
            project_root=ctx.project_root,
        )

    if blockers:
        return _blocked_payload(ctx, blockers)

    progress = FinalizeProgress(results=[])
    original_truth = _snapshot_original_truth(ctx)
    try:
        _sync_final_task_truth(ctx, today or date.today().isoformat(), progress.results)
        progress.commit_created, progress.commit_id = _commit_final_task_truth(
            ctx,
            commit_message=commit_message,
            results=progress.results,
        )
        progress.merge_commit = _merge_finalized_task_branch(ctx, progress.results)
    except Exception as error:  # noqa: BLE001
        if not progress.commit_created:
            _rollback_uncommitted_truth(ctx, original_truth, progress.results)
        return _finalize_failure_payload(ctx, progress, error)

    remote_present = _append_remote_note(ctx, progress.results)
    return _finalize_success_payload(ctx, progress, remote_present=remote_present)
