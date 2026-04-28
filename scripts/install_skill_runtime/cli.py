"""CLI facade for install skill runtime."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .cleanup import migrate_cleanup_confirm, migrate_cleanup_plan
from .doctor import doctor_deps
from .environment import check, install, resolve_source, verify_project
from .models import VALID_MODES


def print_text_report(payload: dict[str, object]) -> None:
    print(f"skill={payload['skill']}")
    if "mode" in payload:
        print(f"mode={payload['mode']}")
    print(f"project_root={payload['project_root']}")
    print(f"profile={payload['profile']}")
    print(f"existing_system_classification={payload['existing_system_classification']}")
    for key in (
        "compatibility_epoch",
        "upgrade_status",
        "execution_rollout",
        "legacy_pending_count",
        "reference_manual_count",
    ):
        if key in payload:
            print(f"{key}={payload[key]}")
    print(f"ok={payload['ok']}")
    for item in payload["results"]:
        suffix = f" path={item['path']}" if item.get("path") else ""
        print(f"- [{item['status']}] {item['key']}: {item['detail']}{suffix}")
    for dependency in payload.get("dependencies", []):
        suffix = f" path={dependency['path']}" if dependency.get("path") else ""
        print(
            f"* dep name={dependency['name']} class={dependency['dependency_class']} "
            f"status={dependency['status']} layer={dependency['blocking_layer']}{suffix}"
        )
        print(f"  detail={dependency['detail']}")
        print(f"  hint={dependency['hint']}")
    if "targets" in payload:
        print(f"TARGET_COUNT={payload['target_count']}")
        print(f"COUNT={payload['count']}")
        print(f"SCOPE_LOCKED={payload['scope_locked']}")
        print(f"PLAN_FINGERPRINT={payload['plan_fingerprint']}")
        print(f"CONFIRM_COMMAND={payload['confirm_command']}")
        for key in ("safe_delete", "keep", "manual_review"):
            print(f"{key.upper()}={len(payload.get(key, []))}")
            for item in payload.get(key, []):
                count_suffix = f" item_count={item['item_count']}" if "item_count" in item else ""
                print(f"  - {item['path']} kind={item['kind']}{count_suffix}")
                print(f"    reason={item['reason']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Deploy or refresh the task-centric knowledge system in a target project.",
        allow_abbrev=False,
    )
    parser.add_argument("--project-root", required=True, help="Абсолютный путь к корню целевого проекта.")
    parser.add_argument("--source-root", help="Путь к исходному skill. По умолчанию — текущий каталог skill.")
    parser.add_argument("--mode", choices=VALID_MODES, default="check", help="Режим работы install/governance helper-а.")
    parser.add_argument("--profile", choices=("generic", "1c"), default="generic", help="Профиль managed-блока для AGENTS.md.")
    parser.add_argument("--force", action="store_true", help="Перезаписать обновляемые managed-файлы knowledge/ шаблонами из дистрибутива, но не project data вроде registry.md.")
    parser.add_argument(
        "--existing-system-mode",
        choices=("abort", "adopt", "migrate"),
        default="abort",
        help="Как вести себя при обнаружении существующей системы хранения: abort, adopt или migrate.",
    )
    parser.add_argument("--confirm-fingerprint", help="Fingerprint ранее показанного cleanup-plan для `migrate-cleanup-confirm`.")
    parser.add_argument("--yes", action="store_true", help="Явно подтвердить применение cleanup-plan.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Формат вывода.")
    return parser


def dispatch(args: argparse.Namespace, *, script_path: Path) -> dict[str, object]:
    project_root = Path(args.project_root).resolve()
    source_root = resolve_source(args.source_root)
    if args.mode == "install":
        return install(project_root, source_root, args.profile, force=args.force, existing_system_mode=args.existing_system_mode)
    if args.mode == "doctor-deps":
        return doctor_deps(project_root, source_root, args.profile)
    if args.mode == "verify-project":
        return verify_project(project_root, source_root, args.profile, force=args.force)
    if args.mode == "migrate-cleanup-plan":
        return migrate_cleanup_plan(
            project_root,
            source_root=source_root,
            profile=args.profile,
            existing_system_mode=args.existing_system_mode,
            script_path=script_path,
            source_root_arg=args.source_root,
            output_format=args.format,
        )
    if args.mode == "migrate-cleanup-confirm":
        return migrate_cleanup_confirm(
            project_root,
            source_root=source_root,
            profile=args.profile,
            existing_system_mode=args.existing_system_mode,
            script_path=script_path,
            source_root_arg=args.source_root,
            output_format=args.format,
            confirm_fingerprint=args.confirm_fingerprint,
            assume_yes=args.yes,
        )
    return check(project_root, source_root, args.profile)


def main(argv: list[str] | None = None, *, script_path: Path | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    payload = dispatch(args, script_path=script_path or Path(__file__).resolve())
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_text_report(payload)
    return 0 if payload["ok"] else 2
