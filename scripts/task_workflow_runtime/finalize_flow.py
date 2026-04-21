"""Local-only finalize flow for task branches."""

from __future__ import annotations

from dataclasses import asdict
from datetime import date
from pathlib import Path

from .git_ops import branch_exists, current_git_branch, has_remote, infer_base_branch, run_git
from .models import DELIVERY_ROW_PLACEHOLDER, FINAL_TASK_STATUSES, PLACEHOLDER_BRANCH_VALUES, StepResult, default_branch_name
from .registry_sync import collect_delivery_units, update_registry
from .task_markdown import derive_goal_summary_from_lines, read_task_fields, task_summary_from_fields, update_task_file


OPEN_DELIVERY_STATUSES = {"planned", "local", "draft", "review"}


def _blocker(key: str, detail: str, *, next_action: str, path: str | None = None) -> dict[str, str | None]:
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


def finalize_task(
    project_root: Path,
    task_dir: Path,
    *,
    base_branch: str | None,
    commit_message: str | None,
    today: str | None = None,
) -> dict[str, object]:
    project_root = project_root.resolve()
    task_dir = (project_root / task_dir).resolve() if not task_dir.is_absolute() else task_dir.resolve()
    task_file = task_dir / "task.md"
    if not task_file.exists():
        raise ValueError(f"Не найден task.md по пути {task_file}.")

    lines, fields = read_task_fields(task_file)
    task_id = fields.get("ID задачи", "").strip()
    short_name = fields.get("Краткое имя", "").strip()
    if not task_id or not short_name:
        raise ValueError("В task.md должны быть заполнены поля `ID задачи` и `Краткое имя`.")

    active_branch = current_git_branch(project_root)
    selected_base_branch = base_branch or infer_base_branch(project_root)
    task_branch = _resolve_task_branch(fields)
    summary = task_summary_from_fields(fields) or derive_goal_summary_from_lines(lines) or short_name
    blockers: list[dict[str, str | None]] = []

    if not active_branch:
        blockers.append(
            _blocker(
                "active_branch",
                "Finalize требует явной checkout-ветки задачи.",
                next_action="Переключитесь на task-ветку задачи и повторите finalize.",
            )
        )
    elif active_branch == selected_base_branch:
        blockers.append(
            _blocker(
                "active_branch",
                "Finalize нельзя запускать из base-ветки.",
                next_action=f"Переключитесь на `{task_branch}` и повторите finalize.",
            )
        )
    elif active_branch != task_branch:
        blockers.append(
            _blocker(
                "task_branch_mismatch",
                f"Текущая ветка `{active_branch}` не совпадает с task-контекстом `{task_branch}`.",
                next_action="Синхронизируйте поле `Ветка` через workflow sync или переключитесь на корректную task-ветку.",
            )
        )

    if not branch_exists(project_root, selected_base_branch):
        blockers.append(
            _blocker(
                "base_branch_missing",
                f"Base-ветка `{selected_base_branch}` не найдена локально.",
                next_action="Создайте или явно укажите существующую base-ветку через `--base-branch`.",
            )
        )

    delivery_units = collect_delivery_units(project_root, task_dir, fields, lines)
    open_units = [unit for unit in delivery_units if unit.status in OPEN_DELIVERY_STATUSES]
    if open_units:
        unit_ids = ", ".join(unit.unit_id for unit in open_units)
        blockers.append(
            _blocker(
                "open_delivery_units",
                f"Нельзя завершить задачу, пока delivery units не закрыты: {unit_ids}.",
                next_action="Доведите все delivery units до `merged` или `closed`, затем повторите finalize.",
                path=str(task_file),
            )
        )

    if active_branch and active_branch != selected_base_branch and branch_exists(project_root, selected_base_branch):
        if not _is_ancestor(project_root, selected_base_branch, active_branch):
            blockers.append(
                _blocker(
                    "base_branch_diverged",
                    f"Base-ветка `{selected_base_branch}` ушла вперёд и fast-forward finalize небезопасен.",
                    next_action="Сначала вручную синхронизируйте task-ветку с base-веткой, затем повторите finalize.",
                )
            )

    if blockers:
        return {
            "ok": False,
            "outcome": "blocked",
            "task_id": task_id,
            "task_dir": str(task_dir),
            "action": "finalize",
            "branch": active_branch or DELIVERY_ROW_PLACEHOLDER,
            "branch_action": "blocked",
            "task_branch": task_branch,
            "base_branch": selected_base_branch,
            "commit_created": False,
            "merge_commit": None,
            "remote_present": has_remote(project_root),
            "results": [],
            "blockers": blockers,
            "next_actions": [item["next_action"] for item in blockers],
        }

    today_value = today or date.today().isoformat()
    results: list[StepResult] = []

    if fields.get("Статус", "").strip() not in FINAL_TASK_STATUSES:
        fields = update_task_file(
            task_file,
            selected_base_branch,
            today=today_value,
            status="завершена",
        )
        results.append(
            StepResult(
                "task_metadata",
                "ok",
                "task.md синхронизирован под итоговое локальное состояние задачи.",
                str(task_file),
            )
        )
    else:
        fields = update_task_file(
            task_file,
            selected_base_branch,
            today=today_value,
            status=fields.get("Статус"),
        )
        results.append(
            StepResult(
                "task_metadata",
                "ok",
                "task.md уже был в финальном статусе; branch/date синхронизированы под итоговое локальное состояние.",
                str(task_file),
            )
        )

    update_registry(
        project_root,
        task_dir,
        fields,
        branch_name=selected_base_branch,
        register_if_missing=False,
        summary=None,
    )
    results.append(
        StepResult(
            "registry",
            "ok",
            "registry.md синхронизирован с финальным локальным branch-state задачи.",
            str(project_root / "knowledge/tasks/registry.md"),
        )
    )

    run_git(project_root, "add", "-A")
    commit_created = False
    commit_id: str | None = None
    if _has_staged_changes(project_root):
        run_git(project_root, "commit", "-m", commit_message or _default_commit_message(task_id, summary))
        commit_created = True
        commit_id = _head_commit(project_root)
        results.append(
            StepResult(
                "commit",
                "ok",
                "Task-scoped commit создан перед локальным finalize.",
                commit_id,
            )
        )
    else:
        results.append(
            StepResult(
                "commit",
                "ok",
                "Новых staged-изменений нет; finalize продолжен без дополнительного commit.",
                None,
            )
        )

    run_git(project_root, "checkout", selected_base_branch)
    results.append(
        StepResult(
            "checkout",
            "ok",
            f"Переключение на base-ветку `{selected_base_branch}` выполнено.",
            selected_base_branch,
        )
    )
    run_git(project_root, "merge", "--ff-only", task_branch)
    merge_commit = _head_commit(project_root)
    results.append(
        StepResult(
            "merge",
            "ok",
            f"Local finalize завершён через fast-forward merge `{task_branch}` -> `{selected_base_branch}`.",
            merge_commit,
        )
    )
    if has_remote(project_root):
        results.append(
            StepResult(
                "remote",
                "ok",
                "Связанный remote обнаружен; push при необходимости выполняется отдельным шагом после local finalize.",
                None,
            )
        )

    return {
        "ok": True,
        "outcome": "finalized",
        "task_id": task_id,
        "task_dir": str(task_dir),
        "action": "finalize",
        "branch": selected_base_branch,
        "branch_action": "finalized",
        "task_branch": task_branch,
        "base_branch": selected_base_branch,
        "commit_created": commit_created,
        "commit_id": commit_id,
        "merge_commit": merge_commit,
        "remote_present": has_remote(project_root),
        "results": [asdict(item) for item in results],
        "blockers": [],
        "next_actions": [],
    }
