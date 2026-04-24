"""CLI for read-only task reporting."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .read_model import (
    build_status_snapshot,
    current_task_resolution_to_dict,
    current_task_snapshot,
    exact_task_snapshot,
    matching_task_snapshots,
    status_snapshot_to_dict,
    task_preview_to_dict,
    task_snapshot_to_dict,
)


def render_header(summary: dict[str, object]) -> list[str]:
    return [
        f"{summary['task_id']} · {summary['short_name']}",
        str(summary["human_description"]),
    ]


def render_preview(item: dict[str, object]) -> list[str]:
    summary = item["summary"]
    assert isinstance(summary, dict)
    lines = render_header(summary)
    lines.append(f"status={item['status']} priority={item['priority']} branch={item['branch']}")
    if item.get("current_stage"):
        lines.append(f"stage={item['current_stage']}")
    return lines


def append_section(lines: list[str], title: str, rows: list[str]) -> None:
    if not rows:
        return
    if lines:
        lines.append("")
    lines.append(title)
    lines.extend(rows)


def format_warnings(warnings: list[dict[str, object]]) -> list[str]:
    rows: list[str] = []
    for warning in warnings:
        path = f" path={warning['path']}" if warning.get("path") else ""
        rows.append(f"- [{warning['severity']}] {warning['code']}: {warning['detail']}{path}")
    return rows


def format_status_payload(payload: dict[str, object]) -> str:
    lines: list[str] = ["status"]
    append_section(
        lines,
        "Repository / branch",
        [
            f"project_root={payload['project_root']}",
            f"active_branch={payload['active_branch'] or '—'}",
        ],
    )
    health = payload["knowledge_health"]
    assert isinstance(health, dict)
    append_section(
        lines,
        "Knowledge health",
        [
            f"knowledge_exists={health['knowledge_exists']}",
            f"registry_exists={health['registry_exists']}",
            f"managed_block_state={health['managed_block_state']}",
            f"task_count={health['task_count']}",
        ],
    )
    upgrade = payload["upgrade_governance"]
    assert isinstance(upgrade, dict)
    append_section(
        lines,
        "Upgrade governance",
        [
            f"state_exists={upgrade['state_exists']}",
            f"compatibility_epoch={upgrade['compatibility_epoch']}",
            f"upgrade_status={upgrade['upgrade_status']}",
            f"execution_rollout={upgrade['execution_rollout']}",
            f"legacy_pending_count={upgrade['legacy_pending_count']}",
            f"reference_manual_count={upgrade['reference_manual_count']}",
        ],
    )
    current_task = payload["current_task"]
    assert isinstance(current_task, dict)
    if current_task["state"] == "resolved" and current_task["task"]:
        task = current_task["task"]
        assert isinstance(task, dict)
        rows = render_header(task["summary"])
        rows.extend(
            [
                f"status={task['status']} priority={task['priority']} branch={task['branch']}",
                f"current_stage={task['current_stage'] or '—'}",
                f"next_step={task['next_step'] or '—'}",
            ]
        )
        append_section(lines, "Current task", rows)
    elif current_task["state"] == "ambiguous":
        rows = [f"reason={current_task['reason']}"]
        rows.extend(
            line
            for candidate in current_task["candidates"]
            for line in ["", *render_preview(candidate)]
        )
        append_section(lines, "Ambiguous current task", [row for row in rows if row != ""])
    else:
        append_section(lines, "Current task", ["Активная задача не определена."])
    counters = payload["task_counters"]
    assert isinstance(counters, dict)
    append_section(lines, "Task counters", [f"- {status}: {count}" for status, count in counters.items()])
    if payload["high_priority_open"]:
        append_section(
            lines,
            "High priority open tasks",
            [line for item in payload["high_priority_open"] for line in render_preview(item) + [""]],
        )
        while lines and lines[-1] == "":
            lines.pop()
    if payload["review_tasks"]:
        append_section(
            lines,
            "Review tasks",
            [line for item in payload["review_tasks"] for line in render_preview(item) + [""]],
        )
        while lines and lines[-1] == "":
            lines.pop()
    if payload["open_delivery_units"]:
        append_section(
            lines,
            "Open delivery units",
            [
                (
                    f"- {item['unit_id']} | {item['status']} | {item['host']} | "
                    f"{item['task_id']} | {item['short_name']} | {item['url']}"
                )
                for item in payload["open_delivery_units"]
            ],
        )
    append_section(lines, "Warnings", format_warnings(payload["warnings"]))
    return "\n".join(lines) + "\n"


def format_current_task_payload(payload: dict[str, object]) -> str:
    resolution = payload["resolution"]
    assert isinstance(resolution, dict)
    lines: list[str] = ["current-task", f"project_root={payload['project_root']}"]
    if resolution["state"] == "resolved" and resolution["task"]:
        task = resolution["task"]
        assert isinstance(task, dict)
        append_section(lines, "Task", render_header(task["summary"]))
        append_section(
            lines,
            "Status / branch",
            [
                f"status={task['status']}",
                f"priority={task['priority']}",
                f"branch={task['branch']}",
            ],
        )
        append_section(lines, "Текущий этап", [task["current_stage"] or "—"])
        if task["subtasks"]:
            append_section(
                lines,
                "Подзадачи",
                [line for item in task["subtasks"] for line in render_preview(item) + [""]],
            )
            while lines and lines[-1] == "":
                lines.pop()
        if task["delivery_units"]:
            append_section(
                lines,
                "Delivery units",
                [
                    f"- {item['unit_id']} | {item['host']} | {item['status']} | {item['url']}"
                    for item in task["delivery_units"]
                ],
            )
        append_section(lines, "Следующий шаг", [task["next_step"] or "—"])
        append_section(lines, "Blockers / ручной остаток", task["blockers"] + task["manual_remainder"] or ["—"])
        append_section(lines, "Warnings", format_warnings(payload["warnings"]))
        return "\n".join(lines) + "\n"
    if resolution["state"] == "ambiguous":
        append_section(lines, "Ambiguous current task", [f"reason={resolution['reason']}"])
        append_section(
            lines,
            "Candidates",
            [line for item in resolution["candidates"] for line in render_preview(item) + [""]],
        )
        while lines and lines[-1] == "":
            lines.pop()
    else:
        append_section(lines, "Current task", ["Активная задача не определена."])
    append_section(lines, "Warnings", format_warnings(payload["warnings"]))
    return "\n".join(lines) + "\n"


def format_task_show_payload(payload: dict[str, object]) -> str:
    lines: list[str] = ["task show", f"selector={payload['selector']}"]
    resolution = payload.get("resolution")
    if resolution is not None:
        assert isinstance(resolution, dict)
        append_section(lines, "Resolution", [f"state={resolution['state']}", f"reason={resolution['reason']}"])
        if resolution["state"] != "resolved":
            if resolution["candidates"]:
                append_section(
                    lines,
                    "Candidates",
                    [line for item in resolution["candidates"] for line in render_preview(item) + [""]],
                )
                while lines and lines[-1] == "":
                    lines.pop()
            append_section(lines, "Warnings", format_warnings(payload["warnings"]))
            return "\n".join(lines) + "\n"
    task = payload["task"]
    if task is None:
        append_section(lines, "Результат", ["Задача не найдена."])
        append_section(lines, "Warnings", format_warnings(payload["warnings"]))
        return "\n".join(lines) + "\n"
    assert isinstance(task, dict)
    append_section(lines, "Task", render_header(task["summary"]))
    append_section(
        lines,
        "Паспорт",
        [
            f"parent_id={task['parent_id']}",
            f"status={task['status']}",
            f"priority={task['priority']}",
            f"branch={task['branch']}",
        ],
    )
    append_section(lines, "Цель", [task["goal"] or "—"])
    append_section(lines, "Текущий этап", [task["current_stage"] or "—"])
    append_section(lines, "Связанные материалы", [f"- {key}: {value}" for key, value in task["files"].items()])
    if task["subtasks"]:
        append_section(
            lines,
            "Подзадачи",
            [line for item in task["subtasks"] for line in render_preview(item) + [""]],
        )
        while lines and lines[-1] == "":
            lines.pop()
    if task["delivery_units"]:
        append_section(
            lines,
            "Контур публикации",
            [
                f"- {item['unit_id']} | {item['head']} | {item['base']} | {item['status']} | {item['url']}"
                for item in task["delivery_units"]
            ],
        )
    append_section(
        lines,
        "Verify",
        [*task["verify"]["automated"], *task["verify"]["manual"]] or ["—"],
    )
    append_section(lines, "Warnings", format_warnings(payload["warnings"]))
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    format_parent = argparse.ArgumentParser(add_help=False)
    format_parent.add_argument("--format", choices=("text", "json"), default="text", help="Формат вывода.")
    parser = argparse.ArgumentParser(
        description="Read-only operator CLI for task-centric knowledge reporting.",
        allow_abbrev=False,
    )
    parser.add_argument("--project-root", required=True, help="Абсолютный путь к корню проекта.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status", parents=[format_parent], help="Сводка knowledge-системы и активной задачи.")
    subparsers.add_parser("current-task", parents=[format_parent], help="Текущая активная задача и следующий шаг.")
    task_parser = subparsers.add_parser("task", help="Просмотр конкретной задачи.")
    task_subparsers = task_parser.add_subparsers(dest="task_command", required=True)
    show_parser = task_subparsers.add_parser("show", parents=[format_parent], help="Показать карточку задачи.")
    show_parser.add_argument("selector", help="Точный TASK-ID или `current`.")
    return parser


def dispatch(args: argparse.Namespace) -> tuple[dict[str, object], int]:
    project_root = Path(args.project_root).resolve()
    if args.command == "status":
        snapshot = build_status_snapshot(project_root)
        payload = {
            "ok": True,
            "command": "status",
            **status_snapshot_to_dict(snapshot),
        }
        return payload, 0
    if args.command == "current-task":
        resolution = current_task_snapshot(project_root)
        resolution_payload = current_task_resolution_to_dict(resolution)
        payload = {
            "ok": True,
            "command": "current-task",
            "project_root": str(project_root),
            "resolution": resolution_payload,
            "warnings": resolution_payload["warnings"],
        }
        return payload, 0
    selector = args.selector
    if selector == "current":
        resolution = current_task_snapshot(project_root)
        resolution_payload = current_task_resolution_to_dict(resolution)
        payload = {
            "ok": resolution.state == "resolved",
            "command": "task show",
            "project_root": str(project_root),
            "selector": selector,
            "resolution": resolution_payload,
            "task": task_snapshot_to_dict(resolution.task) if resolution.task else None,
            "warnings": resolution_payload["warnings"],
        }
        return payload, 0 if resolution.state == "resolved" else 2
    matches = matching_task_snapshots(project_root, selector)
    if len(matches) > 1:
        warning = {
            "code": "duplicate_task_id",
            "severity": "error",
            "detail": f"Найдено несколько карточек с ID `{selector}`; exact selector стал неоднозначным.",
            "path": None,
        }
        payload = {
            "ok": False,
            "command": "task show",
            "project_root": str(project_root),
            "selector": selector,
            "resolution": {
                "state": "ambiguous",
                "reason": "duplicate_task_id",
                "task": None,
                "candidates": [task_preview_to_dict(match.preview()) for match in matches],
                "warnings": [warning],
            },
            "task": None,
            "warnings": [warning],
        }
        return payload, 2
    task = matches[0] if matches else exact_task_snapshot(project_root, selector)
    if task is None:
        detail = "Поддерживаются только точный TASK-ID или `current`."
        if selector.strip() and all(not char.isspace() for char in selector) and "/" not in selector and "\\" not in selector:
            detail = f"Задача с ID `{selector}` не найдена."
        payload = {
            "ok": False,
            "command": "task show",
            "project_root": str(project_root),
            "selector": selector,
            "task": None,
            "warnings": [
                {
                    "code": "task_not_found",
                    "severity": "error",
                    "detail": detail,
                    "path": None,
                }
            ],
        }
        return payload, 2
    task_payload = task_snapshot_to_dict(task)
    payload = {
        "ok": True,
        "command": "task show",
        "project_root": str(project_root),
        "selector": selector,
        "task": task_payload,
        "warnings": task_payload["warnings"],
    }
    return payload, 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    payload, exit_code = dispatch(args)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return exit_code
    if args.command == "status":
        print(format_status_payload(payload), end="")
    elif args.command == "current-task":
        print(format_current_task_payload(payload), end="")
    else:
        print(format_task_show_payload(payload), end="")
    return exit_code
