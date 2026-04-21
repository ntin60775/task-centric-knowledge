#!/usr/bin/env python3
"""Unified operator CLI for task-centric knowledge workflows."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from borrowings_runtime import apply_refresh, build_refresh_plan, read_status
from install_skill_runtime import check, doctor_deps, install, migrate_cleanup_confirm, migrate_cleanup_plan, resolve_source
from install_skill_runtime.cli import main as legacy_install_main
from install_skill_runtime.cli import print_text_report as print_install_text_report
from module_core_runtime.query_cli import (
    dispatch_file,
    dispatch_module,
    format_file_show_payload,
    format_module_find_payload,
    format_module_show_payload,
)
from task_workflow_runtime import backfill_task, finalize_task, run_publish_flow, sync_task
from task_workflow_runtime.cli import print_text_report as print_workflow_text_report
from task_workflow_runtime.query_cli import (
    dispatch as dispatch_query,
    format_current_task_payload,
    format_status_payload,
    format_task_show_payload,
)


COMMAND_NAME = "task-knowledge"
CLI_VERSION = "0.1.0"
SUPPORTED_COMMANDS = ["doctor", "install", "task", "module", "file", "workflow", "borrowings"]


def _command_prefix(*parts: str) -> tuple[str, ...]:
    return (COMMAND_NAME, *parts)


def _output_format(json_mode: bool) -> str:
    return "json" if json_mode else "text"


def _common_install_parent() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--project-root", required=True, help="Абсолютный путь к корню целевого проекта.")
    parser.add_argument("--source-root", help="Путь к исходному skill. По умолчанию — текущий каталог skill.")
    parser.add_argument("--profile", choices=("generic", "1c"), default="generic", help="Профиль managed-блока для AGENTS.md.")
    return parser


def _common_workflow_parent() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--project-root", required=True, help="Абсолютный путь к корню проекта.")
    parser.add_argument("--task-dir", required=True, help="Путь к каталогу задачи относительно project-root или абсолютный путь.")
    return parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Единый CLI для install/query/workflow контуров task-centric knowledge.",
        allow_abbrev=False,
    )
    parser.add_argument("--json", action="store_true", help="Вернуть машиночитаемый JSON.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {CLI_VERSION}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor_parser = subparsers.add_parser("doctor", parents=[_common_install_parent()], help="Проверить runtime, source-root и целевой проект.")
    doctor_parser.add_argument(
        "--check-command-path",
        action="store_true",
        help="Отмечать отсутствие команды в PATH как проблему окружения.",
    )

    install_parser = subparsers.add_parser("install", help="Install/upgrade governance контур.")
    install_subparsers = install_parser.add_subparsers(dest="install_command", required=True)

    install_subparsers.add_parser("check", parents=[_common_install_parent()], help="Read-only проверка проекта и source-root.")

    apply_parser = install_subparsers.add_parser("apply", parents=[_common_install_parent()], help="Установить или обновить knowledge-систему.")
    apply_parser.add_argument("--force", action="store_true", help="Перезаписать обновляемые managed-файлы шаблонами из дистрибутива.")
    apply_parser.add_argument(
        "--existing-system-mode",
        choices=("abort", "adopt", "migrate"),
        default="abort",
        help="Как вести себя при обнаружении существующей системы хранения.",
    )

    install_subparsers.add_parser("doctor-deps", parents=[_common_install_parent()], help="Диагностика install/upgrade зависимостей.")

    cleanup_plan_parser = install_subparsers.add_parser(
        "cleanup-plan",
        parents=[_common_install_parent()],
        help="Показать безопасный cleanup-plan после миграции.",
    )
    cleanup_plan_parser.add_argument(
        "--existing-system-mode",
        choices=("abort", "adopt", "migrate"),
        default="abort",
        help="Как классифицировать existing system при расчёте cleanup scope.",
    )

    cleanup_confirm_parser = install_subparsers.add_parser(
        "cleanup-confirm",
        parents=[_common_install_parent()],
        help="Применить ранее показанный cleanup-plan.",
    )
    cleanup_confirm_parser.add_argument(
        "--existing-system-mode",
        choices=("abort", "adopt", "migrate"),
        default="abort",
        help="Как классифицировать existing system при confirm.",
    )
    cleanup_confirm_parser.add_argument("--confirm-fingerprint", required=True, help="Fingerprint ранее показанного cleanup-plan.")
    cleanup_confirm_parser.add_argument("--yes", action="store_true", help="Явно подтвердить применение cleanup-plan.")

    task_parser = subparsers.add_parser("task", help="Read-only отчётность по knowledge-задачам.")
    task_subparsers = task_parser.add_subparsers(dest="task_command", required=True)
    task_status_parser = task_subparsers.add_parser("status", help="Сводка knowledge-системы и активной задачи.")
    task_status_parser.add_argument("--project-root", required=True, help="Абсолютный путь к корню проекта.")
    task_current_parser = task_subparsers.add_parser("current", help="Текущая активная задача и следующий шаг.")
    task_current_parser.add_argument("--project-root", required=True, help="Абсолютный путь к корню проекта.")
    task_show_parser = task_subparsers.add_parser("show", help="Показать карточку задачи.")
    task_show_parser.add_argument("--project-root", required=True, help="Абсолютный путь к корню проекта.")
    task_show_parser.add_argument("selector", help="Точный TASK-ID или `current`.")

    module_parser = subparsers.add_parser("module", help="Read-only навигация по Module Core.")
    module_subparsers = module_parser.add_subparsers(dest="module_command", required=True)
    module_find_parser = module_subparsers.add_parser("find", help="Найти governed module.")
    module_find_parser.add_argument("--project-root", required=True, help="Абсолютный путь к корню проекта.")
    module_find_parser.add_argument("query", help="Поисковая строка по MODULE-ID, slug, ref или governed file.")
    module_find_parser.add_argument("--limit", type=int, default=20, help="Ограничить число результатов.")
    module_find_parser.add_argument(
        "--readiness",
        choices=("ready", "partial", "blocked"),
        help="Фильтр по ExecutionReadiness.",
    )
    module_find_parser.add_argument(
        "--source-state",
        choices=("verification_only", "passport_ready", "partial"),
        help="Фильтр по состоянию provider merge.",
    )
    module_show_parser = module_subparsers.add_parser("show", help="Показать read-model модуля.")
    module_show_parser.add_argument("--project-root", required=True, help="Абсолютный путь к корню проекта.")
    module_show_parser.add_argument("selector", help="Точный MODULE-ID или уникальный slug.")
    module_show_parser.add_argument(
        "--with",
        dest="with_sections",
        action="append",
        choices=("verification", "files", "relations", "all"),
        default=[],
        help="Дополнительные секции text-вывода.",
    )

    file_parser = subparsers.add_parser("file", help="Read-only навигация по governed files.")
    file_subparsers = file_parser.add_subparsers(dest="file_command", required=True)
    file_show_parser = file_subparsers.add_parser("show", help="Показать file-local read-model.")
    file_show_parser.add_argument("--project-root", required=True, help="Абсолютный путь к корню проекта.")
    file_show_parser.add_argument("path", help="Project-relative или абсолютный путь к файлу.")
    file_show_parser.add_argument("--module", help="Точный MODULE-ID или уникальный slug для фильтрации владельца.")
    file_show_parser.add_argument(
        "--contracts",
        action="store_true",
        help="Показать секцию contract markers для `MODULE_CONTRACT`, `MODULE_MAP`, `CHANGE_SUMMARY`.",
    )
    file_show_parser.add_argument(
        "--blocks",
        action="store_true",
        help="Показать секцию block anchors из file-local contract layer.",
    )

    workflow_parser = subparsers.add_parser("workflow", help="Синхронизация задач и publish helper.")
    workflow_subparsers = workflow_parser.add_subparsers(dest="workflow_command", required=True)

    workflow_sync_parser = workflow_subparsers.add_parser("sync", parents=[_common_workflow_parent()], help="Синхронизировать git-контекст и registry/task.md.")
    workflow_sync_parser.add_argument("--create-branch", action="store_true", help="Создать или переключить task-ветку.")
    workflow_sync_parser.add_argument("--register-if-missing", action="store_true", help="Создать строку в registry.md, если она отсутствует.")
    workflow_sync_parser.add_argument("--summary", help="Legacy-fallback описание для registry.md.")
    workflow_sync_parser.add_argument("--branch-name", help="Явно задать имя ветки.")
    workflow_sync_parser.add_argument(
        "--inherit-branch-from-parent",
        action="store_true",
        help="Для подзадачи использовать ветку родителя вместо отдельной ветки.",
    )
    workflow_backfill_parser = workflow_subparsers.add_parser(
        "backfill",
        parents=[_common_workflow_parent()],
        help="Controlled compatibility-backfill для legacy-задачи.",
    )
    workflow_backfill_parser.add_argument(
        "--scope",
        choices=("compatibility",),
        default="compatibility",
        help="Тип governed backfill.",
    )
    workflow_backfill_parser.add_argument("--summary", help="Явная summary для active legacy-задачи, если нужен controlled backfill.")

    workflow_finalize_parser = workflow_subparsers.add_parser(
        "finalize",
        parents=[_common_workflow_parent()],
        help="Local-only finalize задачи: commit, fast-forward merge в base и checkout base.",
    )
    workflow_finalize_parser.add_argument("--base-branch", help="Целевая base-ветка для local finalize.")
    workflow_finalize_parser.add_argument("--commit-message", help="Явное сообщение commit для local finalize.")

    workflow_publish_parser = workflow_subparsers.add_parser("publish", parents=[_common_workflow_parent()], help="Publish helper поверх delivery unit.")
    workflow_publish_parser.add_argument("action", choices=("start", "publish", "sync", "merge", "close"), help="Publish-helper действие.")
    workflow_publish_parser.add_argument("--unit-id", help="Delivery unit в формате `DU-01`.")
    workflow_publish_parser.add_argument("--purpose", help="Назначение delivery unit для `start` или нового unit.")
    workflow_publish_parser.add_argument("--base-branch", help="Целевая base-ветка для публикации и merge.")
    workflow_publish_parser.add_argument("--head-branch", help="Явно задать head-ветку delivery unit.")
    workflow_publish_parser.add_argument("--from-ref", help="Ref, от которого создавать новую delivery-ветку.")
    workflow_publish_parser.add_argument("--host", help="Host публикации: `github`, `gitlab`, `generic`, `none` или `auto`.")
    workflow_publish_parser.add_argument("--publication-type", help="Тип публикации: `pr`, `mr`, `none`.")
    workflow_publish_parser.add_argument("--url", help="URL опубликованного PR/MR.")
    workflow_publish_parser.add_argument("--merge-commit", help="Merge commit SHA или ID.")
    workflow_publish_parser.add_argument("--cleanup", help="Состояние cleanup: `не требуется`, `ожидается`, `выполнено`.")
    workflow_publish_parser.add_argument("--remote-name", default="origin", help="Имя git remote для auto-detect хостинга.")
    workflow_publish_parser.add_argument("--status", help="Явно задать publish-статус delivery unit.")
    workflow_publish_parser.add_argument("--create-publication", action="store_true", help="Попробовать создать PR/MR через host adapter.")
    workflow_publish_parser.add_argument("--sync-from-host", action="store_true", help="Прочитать состояние существующего PR/MR через host adapter.")
    workflow_publish_parser.add_argument("--title", help="Заголовок публикации для `--create-publication`.")
    workflow_publish_parser.add_argument("--body", help="Тело публикации для `--create-publication`.")
    workflow_publish_parser.add_argument("--summary", help="Legacy-fallback описание для registry.md.")

    borrowings_parser = subparsers.add_parser("borrowings", help="Local-first borrowed-layer governance.")
    borrowings_subparsers = borrowings_parser.add_subparsers(dest="borrowings_command", required=True)

    borrowings_parent = argparse.ArgumentParser(add_help=False)
    borrowings_parent.add_argument("--project-root", required=True, help="Абсолютный путь к корню проекта.")
    borrowings_parent.add_argument("--source", choices=("grace",), required=True, help="Borrowed source manifest.")
    borrowings_parent.add_argument("--checkout", help="Абсолютный путь к локальному upstream checkout.")

    borrowings_subparsers.add_parser("status", parents=[borrowings_parent], help="Показать состояние borrowed manifest и checkout.")
    borrowings_subparsers.add_parser("refresh-plan", parents=[borrowings_parent], help="Построить preview borrowed refresh.")
    refresh_apply_parser = borrowings_subparsers.add_parser("refresh-apply", parents=[borrowings_parent], help="Применить подтверждённый borrowed refresh-plan.")
    refresh_apply_parser.add_argument("--plan-fingerprint", required=True, help="Fingerprint ранее построенного refresh-plan.")
    refresh_apply_parser.add_argument("--yes", action="store_true", help="Явно подтвердить применение refresh-plan.")

    return parser


def _render_json(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _render_doctor_text(payload: dict[str, object]) -> None:
    print("doctor")
    print(f"ok={payload['ok']}")
    print(f"version={payload['version']}")
    print(f"command_name={payload['command_name']}")
    print(f"command_in_path={payload['command_in_path']}")
    if payload.get("command_path"):
        print(f"command_path={payload['command_path']}")
    print(f"python={payload['python']}")
    print(f"git_available={payload['git_available']}")
    print(f"project_root={payload['project_root']}")
    print(f"source_root={payload['source_root']}")
    print(f"profile={payload['profile']}")
    for item in payload["results"]:
        suffix = f" path={item['path']}" if item.get("path") else ""
        print(f"- [{item['status']}] {item['key']}: {item['detail']}{suffix}")
    print(f"supported_commands={', '.join(SUPPORTED_COMMANDS)}")


def _render_query_text(payload: dict[str, object]) -> None:
    command = payload["command"]
    if command == "status":
        print(format_status_payload(payload), end="")
    elif command == "current-task":
        print(format_current_task_payload(payload), end="")
    else:
        print(format_task_show_payload(payload), end="")


def _render_module_query_text(
    payload: dict[str, object],
    *,
    with_sections: set[str] | None = None,
    show_contracts: bool = False,
    show_blocks: bool = False,
) -> None:
    command = payload["command"]
    if command == "module find":
        print(format_module_find_payload(payload), end="")
    elif command == "module show":
        print(format_module_show_payload(payload, with_sections=with_sections), end="")
    else:
        print(format_file_show_payload(payload, show_contracts=show_contracts, show_blocks=show_blocks), end="")


def _render_borrowings_text(payload: dict[str, object]) -> None:
    print(str(payload["command"]))
    print(f"ok={payload['ok']}")
    print(f"source={payload['source']}")
    if payload.get("manifest_path"):
        print(f"manifest_path={payload['manifest_path']}")
    if payload.get("checkout_state"):
        print(f"checkout_state={payload['checkout_state']}")
    if payload.get("checkout_path"):
        print(f"checkout_path={payload['checkout_path']}")
    if payload.get("checkout_revision"):
        print(f"checkout_revision={payload['checkout_revision']}")
    if payload.get("pinned_revision"):
        print(f"pinned_revision={payload['pinned_revision']}")
    if payload.get("plan_fingerprint"):
        print(f"plan_fingerprint={payload['plan_fingerprint']}")
    if "pending_action_count" in payload:
        print(f"pending_action_count={payload['pending_action_count']}")
    if "applied_count" in payload:
        print(f"applied_count={payload['applied_count']}")
    for item in payload.get("results", []):
        if isinstance(item, dict):
            suffix = f" path={item['path']}" if item.get("path") else ""
            print(f"- [{item['status']}] {item['key']}: {item['detail']}{suffix}")
    for item in payload.get("warnings", []):
        if isinstance(item, dict):
            suffix = f" path={item['path']}" if item.get("path") else ""
            print(f"- [{item['status']}] {item['key']}: {item['detail']}{suffix}")


def _doctor(args: argparse.Namespace) -> tuple[dict[str, object], int]:
    project_root = Path(args.project_root).resolve()
    source_root = resolve_source(args.source_root)
    install_check = check(project_root, source_root, args.profile)
    dependency_check = doctor_deps(project_root, source_root, args.profile)
    command_path = shutil.which(COMMAND_NAME)
    results = [
        *install_check["results"],
        *dependency_check["results"],
    ]
    if command_path:
        results.append(
            {
                "key": "command_path",
                "status": "ok",
                "detail": "Команда доступна из PATH.",
                "path": command_path,
            }
        )
    else:
        results.append(
            {
                "key": "command_path",
                "status": "warning",
                "detail": "Команда пока не установлена в PATH; используй `make install-local`.",
                "path": None,
            }
        )

    git_available = shutil.which("git") is not None
    if git_available:
        results.append({"key": "git", "status": "ok", "detail": "Git найден в PATH.", "path": shutil.which("git")})
    else:
        results.append({"key": "git", "status": "error", "detail": "Git не найден в PATH.", "path": None})

    ok = bool(install_check["ok"]) and bool(dependency_check["ok"]) and git_available
    if args.check_command_path:
        ok = ok and command_path is not None
    payload = {
        "ok": ok,
        "command": "doctor",
        "command_name": COMMAND_NAME,
        "command_in_path": command_path is not None,
        "command_path": command_path,
        "version": CLI_VERSION,
        "python": sys.executable,
        "git_available": git_available,
        "project_root": str(project_root),
        "source_root": str(source_root),
        "profile": args.profile,
        "results": results,
        "install_check": install_check,
        "dependency_check": dependency_check,
        "supported_commands": SUPPORTED_COMMANDS,
    }
    return payload, 0 if ok else 2


def _install(args: argparse.Namespace, *, json_mode: bool) -> tuple[dict[str, object], int]:
    project_root = Path(args.project_root).resolve()
    source_root = resolve_source(args.source_root)
    output_format = _output_format(json_mode)
    if args.install_command == "check":
        payload = check(project_root, source_root, args.profile)
    elif args.install_command == "apply":
        payload = install(
            project_root,
            source_root,
            args.profile,
            force=args.force,
            existing_system_mode=args.existing_system_mode,
        )
    elif args.install_command == "doctor-deps":
        payload = doctor_deps(project_root, source_root, args.profile)
    elif args.install_command == "cleanup-plan":
        payload = migrate_cleanup_plan(
            project_root,
            source_root=source_root,
            profile=args.profile,
            existing_system_mode=args.existing_system_mode,
            script_path=Path(__file__).resolve(),
            source_root_arg=args.source_root,
            output_format=output_format,
            command_prefix=_command_prefix("install", "cleanup-confirm"),
        )
    else:
        payload = migrate_cleanup_confirm(
            project_root,
            source_root=source_root,
            profile=args.profile,
            existing_system_mode=args.existing_system_mode,
            script_path=Path(__file__).resolve(),
            source_root_arg=args.source_root,
            output_format=output_format,
            confirm_fingerprint=args.confirm_fingerprint,
            assume_yes=args.yes,
            command_prefix=_command_prefix("install", "cleanup-confirm"),
        )
    return payload, 0 if payload["ok"] else 2


def _task(args: argparse.Namespace) -> tuple[dict[str, object], int]:
    query_args = argparse.Namespace(project_root=args.project_root, format="json")
    if args.task_command == "status":
        query_args.command = "status"
    elif args.task_command == "current":
        query_args.command = "current-task"
    else:
        query_args.command = "task"
        query_args.task_command = "show"
        query_args.selector = args.selector
    return dispatch_query(query_args)


def _module(args: argparse.Namespace) -> tuple[dict[str, object], int]:
    query_args = argparse.Namespace(
        project_root=Path(args.project_root),
        module_command=args.module_command,
        query=getattr(args, "query", None),
        selector=getattr(args, "selector", None),
        readiness=getattr(args, "readiness", None),
        source_state=getattr(args, "source_state", None),
        limit=getattr(args, "limit", 20),
    )
    return dispatch_module(query_args)


def _file(args: argparse.Namespace) -> tuple[dict[str, object], int]:
    query_args = argparse.Namespace(
        project_root=Path(args.project_root),
        file_command=args.file_command,
        path=args.path,
        module=args.module,
        contracts=args.contracts,
        blocks=args.blocks,
    )
    return dispatch_file(query_args)


def _workflow(args: argparse.Namespace) -> tuple[dict[str, object], int]:
    project_root = Path(args.project_root).resolve()
    task_dir = Path(args.task_dir)
    try:
        if args.workflow_command == "sync":
            payload = sync_task(
                project_root,
                task_dir,
                create_branch=args.create_branch,
                register_if_missing=args.register_if_missing,
                summary=args.summary,
                branch_name=args.branch_name,
                inherit_branch_from_parent=args.inherit_branch_from_parent,
            )
        elif args.workflow_command == "backfill":
            payload = backfill_task(
                project_root,
                task_dir,
                scope=args.scope,
                summary=args.summary,
            )
        elif args.workflow_command == "finalize":
            payload = finalize_task(
                project_root,
                task_dir,
                base_branch=args.base_branch,
                commit_message=args.commit_message,
            )
        else:
            payload = run_publish_flow(
                project_root,
                task_dir,
                action=args.action,
                unit_id=args.unit_id,
                purpose=args.purpose,
                base_branch=args.base_branch,
                head_branch=args.head_branch,
                from_ref=args.from_ref,
                host=args.host,
                publication_type=args.publication_type,
                url=args.url,
                merge_commit=args.merge_commit,
                cleanup=args.cleanup,
                remote_name=args.remote_name,
                status=args.status,
                create_publication=args.create_publication,
                sync_from_host=args.sync_from_host,
                title=args.title,
                body=args.body,
                summary=args.summary,
            )
    except Exception as error:  # noqa: BLE001
        payload = {
            "ok": False,
            "outcome": "failed",
            "task_id": None,
            "task_dir": str(task_dir),
            "branch": None,
            "branch_action": "failed",
            "results": [
                {
                    "key": "workflow",
                    "status": "error",
                    "detail": str(error),
                    "path": None,
                }
            ],
        }
    return payload, 0 if payload["ok"] else 2


def _borrowings(args: argparse.Namespace) -> tuple[dict[str, object], int]:
    project_root = Path(args.project_root).resolve()
    skill_root = SCRIPT_DIR.parent.resolve()
    try:
        if args.borrowings_command == "status":
            payload = read_status(skill_root, project_root, source=args.source, checkout=args.checkout)
        elif args.borrowings_command == "refresh-plan":
            payload = build_refresh_plan(skill_root, project_root, source=args.source, checkout=args.checkout)
        else:
            payload = apply_refresh(
                skill_root,
                project_root,
                source=args.source,
                checkout=args.checkout,
                plan_fingerprint=args.plan_fingerprint,
                assume_yes=args.yes,
            )
    except Exception as error:  # noqa: BLE001
        payload = {
            "ok": False,
            "command": f"borrowings {args.borrowings_command}",
            "project_root": str(project_root),
            "source": args.source,
            "results": [{"key": "borrowings", "status": "error", "detail": str(error), "path": None}],
        }
    return payload, 0 if payload["ok"] else 2


def _run_legacy_install_cli(argv: list[str]) -> int:
    return legacy_install_main(argv, script_path=Path(__file__).resolve())


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--mode" in argv:
        return _run_legacy_install_cli(argv)

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "doctor":
        payload, exit_code = _doctor(args)
        if args.json:
            _render_json(payload)
        else:
            _render_doctor_text(payload)
        return exit_code

    if args.command == "install":
        payload, exit_code = _install(args, json_mode=args.json)
        if args.json:
            _render_json(payload)
        else:
            print_install_text_report(payload)
        return exit_code

    if args.command == "task":
        payload, exit_code = _task(args)
        if args.json:
            _render_json(payload)
        else:
            _render_query_text(payload)
        return exit_code

    if args.command == "module":
        payload, exit_code = _module(args)
        if args.json:
            _render_json(payload)
        else:
            _render_module_query_text(payload, with_sections=set(args.with_sections))
        return exit_code

    if args.command == "file":
        payload, exit_code = _file(args)
        if args.json:
            _render_json(payload)
        else:
            _render_module_query_text(payload, show_contracts=args.contracts, show_blocks=args.blocks)
        return exit_code

    if args.command == "workflow":
        payload, exit_code = _workflow(args)
        if args.json:
            _render_json(payload)
        else:
            print_workflow_text_report(payload)
        return exit_code

    payload, exit_code = _borrowings(args)
    if args.json:
        _render_json(payload)
    else:
        _render_borrowings_text(payload)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
