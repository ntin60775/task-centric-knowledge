"""Task sync orchestration."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

from task_workflow_runtime.legacy_upgrade import (
    ensure_repo_upgrade_state,
    load_repo_upgrade_state,
    task_class_from_task_file,
    task_id_from_task_file,
    update_entry_status,
    write_repo_upgrade_state,
    write_task_migration_note,
)

from .git_ops import branch_exists, current_git_branch, has_remote, run_git, worktree_is_clean
from .models import FINAL_TASK_STATUSES, PLACEHOLDER_BRANCH_VALUES, StepResult, default_branch_name
from .path_safety import resolve_task_dir_inside_project
from .registry_sync import (
    dirty_paths_are_task_scoped,
    find_parent_branch,
    preflight_registry_summary,
    sync_preflight_ref_name,
    update_registry,
)
from .task_markdown import read_task_fields, task_summary_from_fields, update_task_file



@dataclass(frozen=True)
class BackfillContext:
    project_root: Path
    task_dir: Path
    task_file: Path
    scope: str
    summary: str | None
    today: str
    task_id: str
    task_class: str
    fields: dict[str, str]
    canonical_summary: str
    recorded_branch: str


VALID_BACKFILL_SCOPES = {"compatibility"}


def historical_branch_from_fields(fields: dict[str, str]) -> str:
    branch = fields.get("Ветка", "").strip()
    if branch in PLACEHOLDER_BRANCH_VALUES:
        raise ValueError(
            "historical_sync_blocked: у закрытой historical-задачи не зафиксировано поле `Ветка`; "
            "обычный sync не имеет права подставлять текущую активную ветку."
        )
    return branch


def should_use_historical_safe_sync(fields: dict[str, str], *, branch_name: str | None) -> bool:
    if fields.get("Статус", "").strip() not in FINAL_TASK_STATUSES:
        return False
    historical_branch = historical_branch_from_fields(fields)
    if branch_name and branch_name != historical_branch:
        raise ValueError(
            "historical_sync_blocked: ordinary sync закрытой historical-задачи не может менять protected field `Ветка`; "
            "используйте отдельный migration/backfill режим с явным scope."
        )
    return True


def resolve_target_branch(
    project_root: Path,
    task_dir: Path,
    fields: dict[str, str],
    *,
    branch_name: str | None,
    inherit_branch_from_parent: bool,
) -> str:
    if branch_name:
        return branch_name
    if inherit_branch_from_parent:
        return find_parent_branch(task_dir, project_root=project_root)
    recorded_branch = fields.get("Ветка", "").strip()
    if recorded_branch not in PLACEHOLDER_BRANCH_VALUES:
        return recorded_branch
    task_id = fields.get("ID задачи", "").strip()
    short_name = fields.get("Краткое имя", "").strip()
    if not task_id or not short_name:
        raise ValueError("В task.md должны быть заполнены поля `ID задачи` и `Краткое имя`.")
    return default_branch_name(task_id, short_name)


def _resolve_task_dir(project_root: Path, task_dir: Path) -> Path:
    return resolve_task_dir_inside_project(project_root, task_dir)


def _load_backfill_context(
    project_root: Path,
    task_dir: Path,
    *,
    scope: str,
    summary: str | None,
    today: str | None,
) -> BackfillContext:
    if scope not in VALID_BACKFILL_SCOPES:
        raise ValueError(f"Некорректный backfill scope: {scope!r}.")

    project_root = project_root.resolve()
    task_dir = _resolve_task_dir(project_root, task_dir)
    task_file = task_dir / "task.md"
    if not task_file.exists():
        raise ValueError(f"Не найден task.md по пути {task_file}.")

    _, fields = read_task_fields(task_file)
    task_id = task_id_from_task_file(task_file)
    return BackfillContext(
        project_root=project_root,
        task_dir=task_dir,
        task_file=task_file,
        scope=scope,
        summary=summary,
        today=today or date.today().isoformat(),
        task_id=task_id,
        task_class=task_class_from_task_file(task_file),
        fields=fields,
        canonical_summary=task_summary_from_fields(fields) or summary or "—",
        recorded_branch=fields.get("Ветка", "").strip(),
    )


def _backfill_payload(
    ctx: BackfillContext,
    *,
    backfill_status: str,
    branch: object,
    branch_action: str,
    results: list[StepResult],
    remote_present: object | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "ok": True,
        "task_id": ctx.task_id,
        "task_dir": str(ctx.task_dir),
        "action": "backfill",
        "scope": ctx.scope,
        "task_class": ctx.task_class,
        "backfill_status": backfill_status,
        "branch": branch,
        "branch_action": branch_action,
        "results": [asdict(item) for item in results],
    }
    if remote_present is not None:
        payload["remote_present"] = remote_present
    return payload


def _record_upgrade_state(
    ctx: BackfillContext,
    *,
    backfill_status: str,
    migration_note: str,
    decision: str,
):
    state = ensure_repo_upgrade_state(
        ctx.project_root,
        epoch="module-core-v1",
        last_upgrade_task=ctx.task_id,
        today=ctx.today,
    )
    state = update_entry_status(
        state,
        task_id=ctx.task_id,
        backfill_status=backfill_status,
        migration_note=migration_note,
        decision=decision,
        last_upgrade_task=ctx.task_id,
        today=ctx.today,
    )
    write_repo_upgrade_state(state)
    return state


def _backfill_reference_task(ctx: BackfillContext) -> dict[str, object]:
    results: list[StepResult] = []
    state = _record_upgrade_state(
        ctx,
        backfill_status="manual-reference",
        migration_note="—",
        decision="Справочная задача исключена из auto-backfill и оставлена на ручное решение.",
    )
    results.append(
        StepResult(
            "reference",
            "ok",
            "Reference-задача не мутировалась; в repo upgrade-state зафиксировано manual-reference решение.",
            str(ctx.task_file),
        )
    )
    results.append(
        StepResult(
            "upgrade_state",
            "ok",
            "Repo upgrade-state обновлён после manual-reference решения.",
            str(state.path),
        )
    )
    return _backfill_payload(
        ctx,
        backfill_status="manual-reference",
        branch=ctx.recorded_branch,
        branch_action="backfill_only",
        results=results,
    )


def _write_backfill_migration_note(ctx: BackfillContext, *, active_task: bool) -> str:
    updated_items = [
        "Создан task-local migration note.",
        "Repo upgrade-state синхронизирован с controlled backfill.",
    ]
    untouched_items = [
        "Historical narrative, даты, delivery fields и protected metadata не переписывались.",
    ]
    if active_task:
        updated_items.append("Task sync обновил allowlisted summary/branch metadata для active-задачи.")
        untouched_items = ["Narrative-секции задачи не переписывались автоматически."]
    return write_task_migration_note(
        ctx.project_root,
        ctx.task_dir,
        epoch_before="legacy-v1",
        epoch_after="module-core-v1",
        task_class=ctx.task_class,
        updated_items=updated_items,
        untouched_items=untouched_items,
        basis_task_id=ctx.task_id,
        today=ctx.today,
    )


def _backfill_historical_task(ctx: BackfillContext) -> dict[str, object]:
    results: list[StepResult] = []
    note_rel = _write_backfill_migration_note(ctx, active_task=False)
    results.append(
        StepResult(
            "migration_note",
            "ok",
            "Task-local migration note создан.",
            str(ctx.task_dir / "artifacts/migration/task-centric-knowledge-upgrade.md"),
        )
    )
    state = _record_upgrade_state(
        ctx,
        backfill_status="note-only",
        migration_note=note_rel,
        decision="Закрытая historical-задача получила только migration note без переписывания protected fields.",
    )
    results.append(
        StepResult(
            "historical_task",
            "ok",
            "Closed historical задача оставлена без изменения task-truth; применён только note-only backfill.",
            str(ctx.task_file),
        )
    )
    results.append(
        StepResult(
            "upgrade_state",
            "ok",
            "Repo upgrade-state обновлён после note-only backfill.",
            str(state.path),
        )
    )
    return _backfill_payload(
        ctx,
        backfill_status="note-only",
        branch=historical_branch_from_fields(ctx.fields),
        branch_action="backfill_only",
        results=results,
    )


def _sync_summary_for_active_backfill(ctx: BackfillContext) -> str | None:
    if ctx.canonical_summary == "—":
        return None
    return ctx.summary or ctx.canonical_summary


def _backfill_active_task(ctx: BackfillContext) -> dict[str, object]:
    results: list[StepResult] = []
    sync_payload = sync_task(
        ctx.project_root,
        ctx.task_dir,
        create_branch=False,
        register_if_missing=True,
        summary=_sync_summary_for_active_backfill(ctx),
        branch_name=None,
        inherit_branch_from_parent=False,
        today=ctx.today,
    )
    note_rel = _write_backfill_migration_note(ctx, active_task=True)
    results.append(
        StepResult(
            "migration_note",
            "ok",
            "Task-local migration note создан.",
            str(ctx.task_dir / "artifacts/migration/task-centric-knowledge-upgrade.md"),
        )
    )
    ensure_repo_upgrade_state(
        ctx.project_root,
        epoch="module-core-v1",
        last_upgrade_task=ctx.task_id,
        today=ctx.today,
    )
    state = load_repo_upgrade_state(ctx.project_root)
    assert state is not None
    state = update_entry_status(
        state,
        task_id=ctx.task_id,
        backfill_status="compatibility-backfilled",
        migration_note=note_rel,
        decision="Active-задача прошла controlled compatibility-backfill и остаётся в обычном task lifecycle.",
        last_upgrade_task=ctx.task_id,
        today=ctx.today,
    )
    write_repo_upgrade_state(state)
    results.extend(StepResult(**item) for item in sync_payload["results"])
    results.append(
        StepResult(
            "upgrade_state",
            "ok",
            "Repo upgrade-state обновлён после compatibility-backfilled active-задачи.",
            str(state.path),
        )
    )
    return _backfill_payload(
        ctx,
        backfill_status="compatibility-backfilled",
        branch=sync_payload["branch"],
        branch_action="backfill_sync",
        results=results,
        remote_present=sync_payload.get("remote_present"),
    )


def backfill_task(
    project_root: Path,
    task_dir: Path,
    *,
    scope: str,
    summary: str | None,
    today: str | None = None,
) -> dict[str, object]:
    ctx = _load_backfill_context(project_root, task_dir, scope=scope, summary=summary, today=today)
    if ctx.task_class == "reference":
        return _backfill_reference_task(ctx)
    if ctx.task_class == "closed historical":
        return _backfill_historical_task(ctx)
    return _backfill_active_task(ctx)

def sync_task(
    project_root: Path,
    task_dir: Path,
    *,
    create_branch: bool,
    register_if_missing: bool,
    summary: str | None,
    branch_name: str | None,
    inherit_branch_from_parent: bool,
    today: str | None = None,
) -> dict[str, object]:
    project_root = project_root.resolve()
    task_dir = _resolve_task_dir(project_root, task_dir)
    task_file = task_dir / "task.md"
    if not task_file.exists():
        raise ValueError(f"Не найден task.md по пути {task_file}.")

    results: list[StepResult] = []
    lines, fields = read_task_fields(task_file)
    del lines
    target_branch = resolve_target_branch(
        project_root,
        task_dir,
        fields,
        branch_name=branch_name,
        inherit_branch_from_parent=inherit_branch_from_parent,
    )
    resolved_summary = preflight_registry_summary(
        project_root,
        task_dir,
        register_if_missing=register_if_missing,
        summary=summary,
        ref_name=sync_preflight_ref_name(
            project_root,
            create_branch=create_branch,
            target_branch=target_branch,
        ),
        allow_untracked_fallback=True,
    )
    active_branch = current_git_branch(project_root)
    branch_action = "recorded"

    if should_use_historical_safe_sync(fields, branch_name=branch_name):
        target_branch = historical_branch_from_fields(fields)
        registry_inserted, registry_path = update_registry(
            project_root,
            task_dir,
            fields,
            branch_name=target_branch,
            register_if_missing=register_if_missing,
            summary=resolved_summary,
        )
        results.append(
            StepResult(
                "task",
                "skipped",
                "Закрытая historical-задача не изменена: protected fields сохраняют исторические значения",
                str(task_file),
            )
        )
        results.append(
            StepResult(
                "git_branch",
                "ok",
                f"Historical branch сохранена без переключения: branch={target_branch}",
            )
        )
        remote_present = has_remote(project_root)
        remote_detail = (
            "Связанный удалённый репозиторий обнаружен; push можно предлагать только после локальной фиксации изменений."
        )
        if not remote_present:
            remote_detail = "Связанный удалённый репозиторий не обнаружен; workflow остаётся только локальным."
        results.append(StepResult("git_remote", "ok", remote_detail))
        registry_detail = "Строка в registry.md обновлена в historical safe-sync режиме"
        if registry_inserted:
            registry_detail = "Строка в registry.md создана в historical safe-sync режиме"
        results.append(StepResult("registry", "ok", registry_detail, registry_path))
        return {
            "ok": True,
            "task_id": fields.get("ID задачи"),
            "task_dir": str(task_dir),
            "branch": target_branch,
            "branch_action": "historical_safe_sync",
            "remote_present": remote_present,
            "results": [asdict(item) for item in results],
        }

    if create_branch:
        if active_branch != target_branch:
            if not worktree_is_clean(project_root) and not dirty_paths_are_task_scoped(project_root, task_dir):
                raise ValueError("Рабочее дерево грязное; автоматическое переключение task-ветки остановлено.")
            if branch_exists(project_root, target_branch):
                run_git(project_root, "checkout", target_branch)
                branch_action = "switched"
            else:
                run_git(project_root, "checkout", "-b", target_branch)
                branch_action = "created"
        else:
            branch_action = "reused"
    elif active_branch:
        target_branch = active_branch

    today_value = today or date.today().isoformat()
    updated_fields = update_task_file(task_file, target_branch, today=today_value, summary=resolved_summary)
    registry_inserted, registry_path = update_registry(
        project_root,
        task_dir,
        updated_fields,
        branch_name=target_branch,
        register_if_missing=register_if_missing,
        summary=resolved_summary,
    )

    results.append(StepResult("task", "ok", "Карточка задачи синхронизирована с git-контекстом", str(task_file)))
    results.append(
        StepResult(
            "git_branch",
            "ok",
            f"Ветка задачи синхронизирована: action={branch_action}, branch={target_branch}",
        )
    )
    remote_present = has_remote(project_root)
    remote_detail = "Связанный удалённый репозиторий обнаружен; push можно предлагать только после локальной фиксации изменений."
    if not remote_present:
        remote_detail = "Связанный удалённый репозиторий не обнаружен; workflow остаётся только локальным."
    results.append(StepResult("git_remote", "ok", remote_detail))
    registry_detail = "Строка в registry.md обновлена"
    if registry_inserted:
        registry_detail = "Строка в registry.md создана"
    results.append(StepResult("registry", "ok", registry_detail, registry_path))

    return {
        "ok": True,
        "task_id": updated_fields.get("ID задачи"),
        "task_dir": str(task_dir),
        "branch": target_branch,
        "branch_action": branch_action,
        "remote_present": remote_present,
        "results": [asdict(item) for item in results],
    }
