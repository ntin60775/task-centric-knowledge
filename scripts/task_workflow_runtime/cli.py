"""CLI facade for task workflow runtime."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .models import StepResult
from .publish_flow import run_publish_flow
from .sync_flow import backfill_task, sync_task


def print_text_report(payload: dict[str, object]) -> None:
    print(f"ok={payload['ok']}")
    print(f"task_id={payload['task_id']}")
    print(f"task_dir={payload['task_dir']}")
    if "action" in payload:
        print(f"action={payload['action']}")
    print(f"branch={payload['branch']}")
    print(f"branch_action={payload['branch_action']}")
    if "remote_present" in payload:
        print(f"remote_present={payload['remote_present']}")
    if "scope" in payload:
        print(f"scope={payload['scope']}")
    if "task_class" in payload:
        print(f"task_class={payload['task_class']}")
    if "backfill_status" in payload:
        print(f"backfill_status={payload['backfill_status']}")
    if "unit_id" in payload:
        print(f"unit_id={payload['unit_id']}")
    if "delivery_status" in payload:
        print(f"delivery_status={payload['delivery_status']}")
    if "host" in payload:
        print(f"host={payload['host']}")
    if "publication_type" in payload:
        print(f"publication_type={payload['publication_type']}")
    if "url" in payload:
        print(f"url={payload['url']}")
    if "merge_commit" in payload:
        print(f"merge_commit={payload['merge_commit']}")
    if "cleanup" in payload:
        print(f"cleanup={payload['cleanup']}")
    for item in payload["results"]:
        suffix = f" path={item['path']}" if item.get("path") else ""
        print(f"- [{item['status']}] {item['key']}: {item['detail']}{suffix}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync task-centric knowledge files with the current Git task workflow.",
        allow_abbrev=False,
    )
    parser.add_argument("--project-root", required=True, help="Абсолютный путь к корню проекта.")
    parser.add_argument("--task-dir", required=True, help="Путь к каталогу задачи относительно project-root или абсолютный путь.")
    parser.add_argument("--create-branch", action="store_true", help="Создать или переключить task-ветку по правилам knowledge-системы.")
    parser.add_argument("--register-if-missing", action="store_true", help="Создать строку в registry.md, если она отсутствует.")
    parser.add_argument(
        "--summary",
        help="Legacy-fallback описание для registry.md, если в task.md ещё нет поля `Человекочитаемое описание`.",
    )
    parser.add_argument("--branch-name", help="Явно задать имя ветки вместо branch-паттерна по умолчанию.")
    parser.add_argument(
        "--inherit-branch-from-parent",
        action="store_true",
        help="Для подзадачи взять ветку родительской задачи вместо создания отдельной ветки.",
    )
    parser.add_argument(
        "--backfill-scope",
        choices=("compatibility",),
        help="Выполнить controlled compatibility-backfill вместо обычного sync.",
    )
    parser.add_argument(
        "--publish-action",
        choices=("start", "publish", "sync", "merge", "close"),
        help="Выполнить publish-helper действие вместо обычной sync-задачи.",
    )
    parser.add_argument("--unit-id", help="Delivery unit в формате `DU-01`.")
    parser.add_argument("--purpose", help="Назначение delivery unit для `start` или нового unit.")
    parser.add_argument("--base-branch", help="Целевая base-ветка для публикации и merge.")
    parser.add_argument("--head-branch", help="Явно задать head-ветку delivery unit.")
    parser.add_argument("--from-ref", help="Ref, от которого создавать новую delivery-ветку.")
    parser.add_argument("--host", help="Host публикации: `github`, `gitlab`, `generic`, `none` или `auto`.")
    parser.add_argument("--publication-type", help="Тип публикации: `pr`, `mr`, `none`.")
    parser.add_argument("--url", help="URL опубликованного PR/MR.")
    parser.add_argument("--merge-commit", help="Merge commit SHA или ID.")
    parser.add_argument("--cleanup", help="Состояние cleanup: `не требуется`, `ожидается`, `выполнено`.")
    parser.add_argument("--remote-name", default="origin", help="Имя git remote для auto-detect хостинга.")
    parser.add_argument("--status", help="Явно задать publish-статус delivery unit.")
    parser.add_argument(
        "--create-publication",
        action="store_true",
        help="Попробовать создать PR/MR через поддерживаемый host adapter.",
    )
    parser.add_argument(
        "--sync-from-host",
        action="store_true",
        help="Прочитать состояние существующего PR/MR через host adapter.",
    )
    parser.add_argument("--title", help="Заголовок публикации для `--create-publication`.")
    parser.add_argument("--body", help="Тело публикации для `--create-publication`.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Формат вывода.")
    args = parser.parse_args()

    project_root = Path(args.project_root)
    task_dir = Path(args.task_dir)
    try:
        if args.publish_action:
            payload = run_publish_flow(
                project_root,
                task_dir,
                action=args.publish_action,
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
        elif args.backfill_scope:
            payload = backfill_task(
                project_root,
                task_dir,
                scope=args.backfill_scope,
                summary=args.summary,
            )
        else:
            payload = sync_task(
                project_root,
                task_dir,
                create_branch=args.create_branch,
                register_if_missing=args.register_if_missing,
                summary=args.summary,
                branch_name=args.branch_name,
                inherit_branch_from_parent=args.inherit_branch_from_parent,
            )
    except Exception as error:  # noqa: BLE001
        payload = {
            "ok": False,
            "task_id": None,
            "task_dir": str(task_dir),
            "branch": None,
            "branch_action": "failed",
            "results": [asdict(StepResult("workflow", "error", str(error)))],
        }

    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_text_report(payload)
    return 0 if payload["ok"] else 2
