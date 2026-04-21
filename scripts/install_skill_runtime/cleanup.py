"""Cleanup planning and confirmation for install/upgrade governance."""

from __future__ import annotations

import shutil
from pathlib import Path
from shlex import quote

from .environment import (
    PROFILE_TO_BLOCK,
    detect_existing_system,
    detect_managed_block_state,
    summarize_existing_system,
    validate_source,
    validate_target,
)
from .models import (
    CleanupCandidate,
    CleanupPlan,
    FINGERPRINT_PLACEHOLDER,
    FOREIGN_SYSTEM_INDICATORS,
    MIGRATION_NOTE_NAME,
    SKILL_NAME,
    StepResult,
    cleanup_scope_fingerprint,
    has_errors,
)


def _path_kind(path: Path) -> str:
    if path.is_symlink():
        return "symlink"
    if path.is_dir():
        return "directory"
    return "file"


def _absolute_path(path: Path) -> str:
    return str(path.absolute())


def _is_regular_cleanup_file(path: Path) -> bool:
    return path.exists() and not path.is_symlink() and path.is_file()


def _safe_candidate(path: Path, reason: str) -> CleanupCandidate:
    return CleanupCandidate(path=_absolute_path(path), category="safe_delete", reason=reason, kind=_path_kind(path))


def _keep_candidate(path: Path, reason: str) -> CleanupCandidate:
    return CleanupCandidate(path=_absolute_path(path), category="keep", reason=reason, kind=_path_kind(path))


def _manual_candidate(path: Path, reason: str) -> CleanupCandidate:
    return CleanupCandidate(path=_absolute_path(path), category="manual_review", reason=reason, kind=_path_kind(path))


def _append_unique(store: dict[str, CleanupCandidate], candidate: CleanupCandidate) -> None:
    store.setdefault(candidate.path, candidate)


def _expand_delete_scope(path: Path) -> list[Path]:
    if not path.exists() and not path.is_symlink():
        raise FileNotFoundError(f"Объект cleanup отсутствует: {path}")
    if path.is_symlink() or path.is_file():
        return [path]
    if not path.is_dir():
        raise RuntimeError(f"Неподдерживаемый тип cleanup-цели: {path}")
    scope = [path]
    for child in sorted(path.iterdir(), key=lambda item: str(item)):
        scope.extend(_expand_delete_scope(child))
    return scope


def _build_confirm_template(
    *,
    script_path: Path,
    project_root: Path,
    source_root_arg: str | None,
    profile: str,
    existing_system_mode: str,
    output_format: str,
    command_prefix: tuple[str, ...] | None = None,
) -> str:
    if command_prefix is not None:
        parts = [
            *command_prefix,
            "--project-root",
            str(project_root.resolve()),
            "--profile",
            profile,
            "--existing-system-mode",
            existing_system_mode,
            "--confirm-fingerprint",
            FINGERPRINT_PLACEHOLDER,
            "--yes",
        ]
        if source_root_arg:
            parts.extend(["--source-root", str(Path(source_root_arg).resolve())])
        if output_format == "json":
            parts.append("--json")
        return " ".join(quote(part) for part in parts)

    parts = [
        "python3",
        str(script_path.resolve()),
        "--project-root",
        str(project_root.resolve()),
        "--mode",
        "migrate-cleanup-confirm",
        "--profile",
        profile,
        "--existing-system-mode",
        existing_system_mode,
        "--confirm-fingerprint",
        FINGERPRINT_PLACEHOLDER,
        "--yes",
    ]
    if source_root_arg:
        parts.extend(["--source-root", str(Path(source_root_arg).resolve())])
    if output_format == "json":
        parts.extend(["--format", "json"])
    return " ".join(quote(part) for part in parts)


def build_cleanup_plan(
    project_root: Path,
    *,
    source_root: Path,
    profile: str,
    existing_system_mode: str,
    script_path: Path,
    source_root_arg: str | None,
    output_format: str,
    command_prefix: tuple[str, ...] | None = None,
) -> tuple[CleanupPlan, list[StepResult], str]:
    results: list[StepResult] = []
    source_results = validate_source(source_root)
    results.extend(source_results)
    results.extend(validate_target(project_root))
    existing_report = detect_existing_system(project_root)
    results.extend(summarize_existing_system(existing_report))
    results.append(StepResult("profile", "ok", f"Выбран профиль {profile}", profile))
    if has_errors(results):
        return CleanupPlan(), results, existing_report.classification

    safe_delete: dict[str, CleanupCandidate] = {}
    keep: dict[str, CleanupCandidate] = {}
    manual_review: dict[str, CleanupCandidate] = {}

    migration_note = project_root / "knowledge" / MIGRATION_NOTE_NAME
    if migration_note.exists() or migration_note.is_symlink():
        if not _is_regular_cleanup_file(migration_note):
            _append_unique(
                manual_review,
                _manual_candidate(
                    migration_note,
                    "Allowlist v1 удаляет migration note только как обычный файл; неожиданный тип объекта требует ручной проверки.",
                ),
            )
        elif existing_report.classification in {"clean", "compatible"}:
            _append_unique(
                safe_delete,
                _safe_candidate(
                    migration_note,
                    "Миграционная заметка больше не требуется: classification уже совместима с knowledge-системой.",
                ),
            )
        else:
            _append_unique(
                keep,
                _keep_candidate(
                    migration_note,
                    f"Миграционная заметка сохраняется, пока classification = {existing_report.classification}.",
                ),
            )

    agents_path = project_root / "AGENTS.md"
    agents_state = "absent"
    if agents_path.exists():
        agents_state = detect_managed_block_state(agents_path.read_text(encoding="utf-8"))
        _append_unique(keep, _keep_candidate(agents_path, "Рабочий `AGENTS.md` относится к project data и не удаляется cleanup-контуром."))

    for profile_name in PROFILE_TO_BLOCK:
        snippet_path = project_root / f"AGENTS.task-centric-knowledge.{profile_name}.md"
        if not snippet_path.exists() and not snippet_path.is_symlink():
            continue
        if not _is_regular_cleanup_file(snippet_path):
            _append_unique(
                manual_review,
                _manual_candidate(
                    snippet_path,
                    "Allowlist v1 удаляет installer-generated snippet только как обычный файл; неожиданный тип объекта требует ручной проверки.",
                ),
            )
        elif agents_path.exists() and agents_state == "managed":
            _append_unique(
                safe_delete,
                _safe_candidate(
                    snippet_path,
                    "Installer-generated snippet стал избыточным после materialized managed-блока в `AGENTS.md`.",
                ),
            )
        else:
            _append_unique(
                keep,
                _keep_candidate(
                    snippet_path,
                    "Snippet сохраняется, пока managed-блок не materialized в `AGENTS.md`.",
                ),
            )

    registry_path = project_root / "knowledge" / "tasks" / "registry.md"
    if registry_path.exists():
        _append_unique(keep, _keep_candidate(registry_path, "`registry.md` является project data и не участвует в auto-delete cleanup."))

    managed_files = [project_root / relative for relative in existing_report.managed_present]
    for managed_path in sorted(managed_files, key=lambda item: str(item)):
        if managed_path.exists():
            _append_unique(
                keep,
                _keep_candidate(managed_path, "Managed-файл knowledge-системы остаётся частью активного project data."),
            )

    tasks_root = project_root / "knowledge" / "tasks"
    if tasks_root.exists():
        for task_dir in sorted(tasks_root.glob("TASK-*"), key=lambda item: str(item)):
            if task_dir.is_dir():
                _append_unique(
                    keep,
                    _keep_candidate(task_dir, "Каталог задачи относится к project data и не может удаляться governance-cleanup."),
                )

    for indicator in FOREIGN_SYSTEM_INDICATORS:
        indicator_path = project_root / indicator
        if indicator_path.exists():
            _append_unique(
                manual_review,
                _manual_candidate(
                    indicator_path,
                    "Сторонний или legacy-контур требует ручной миграционной оценки и не входит в auto-delete v1.",
                ),
            )

    plan = CleanupPlan()
    plan.safe_delete = sorted(safe_delete.values(), key=lambda item: item.path)
    plan.keep = sorted(keep.values(), key=lambda item: item.path)
    plan.manual_review = sorted(manual_review.values(), key=lambda item: item.path)
    if not plan.safe_delete:
        results.append(
            StepResult(
                "cleanup_plan",
                "warning",
                "Безопасных installer-generated артефактов для удаления не найдено; cleanup confirm недоступен.",
            )
        )
        return plan, results, existing_report.classification

    expanded_scope: list[str] = []
    for index, candidate in enumerate(plan.safe_delete):
        scope = tuple(_absolute_path(item) for item in _expand_delete_scope(Path(candidate.path)))
        plan.safe_delete[index] = CleanupCandidate(
            path=candidate.path,
            category=candidate.category,
            reason=candidate.reason,
            kind=candidate.kind,
            item_count=len(scope),
        )
        expanded_scope.extend(scope)

    plan.targets = tuple(candidate.path for candidate in plan.safe_delete)
    plan.target_count = len(plan.targets)
    plan.count = len(expanded_scope)
    plan.expanded_scope = tuple(sorted(expanded_scope))
    plan.confirm_template = _build_confirm_template(
        script_path=script_path,
        project_root=project_root,
        source_root_arg=source_root_arg,
        profile=profile,
        existing_system_mode=existing_system_mode,
        output_format=output_format,
        command_prefix=command_prefix,
    )
    plan.plan_fingerprint = cleanup_scope_fingerprint(
        targets=plan.targets,
        expanded_scope=plan.expanded_scope,
        target_count=plan.target_count,
        count=plan.count,
        confirm_template=plan.confirm_template,
    )
    plan.confirm_command = plan.confirm_template.replace(FINGERPRINT_PLACEHOLDER, plan.plan_fingerprint)
    plan.scope_locked = True
    results.append(
        StepResult(
            "cleanup_plan",
            "ok",
            f"Сформирован cleanup-plan: TARGET_COUNT={plan.target_count}, COUNT={plan.count}, manual_review={len(plan.manual_review)}.",
        )
    )
    return plan, results, existing_report.classification


def _delete_path(path: Path) -> None:
    if not path.exists() and not path.is_symlink():
        return
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    shutil.rmtree(path)


def migrate_cleanup_plan(
    project_root: Path,
    *,
    source_root: Path,
    profile: str,
    existing_system_mode: str,
    script_path: Path,
    source_root_arg: str | None,
    output_format: str,
    command_prefix: tuple[str, ...] | None = None,
) -> dict[str, object]:
    plan, results, classification = build_cleanup_plan(
        project_root,
        source_root=source_root,
        profile=profile,
        existing_system_mode=existing_system_mode,
        script_path=script_path,
        source_root_arg=source_root_arg,
        output_format=output_format,
        command_prefix=command_prefix,
    )
    payload = {
        "skill": SKILL_NAME,
        "mode": "migrate-cleanup-plan",
        "project_root": str(project_root),
        "profile": profile,
        "existing_system_classification": classification,
        "ok": not has_errors(results),
        "results": [item.to_payload() for item in results],
    }
    payload.update(plan.to_payload())
    return payload


def migrate_cleanup_confirm(
    project_root: Path,
    *,
    source_root: Path,
    profile: str,
    existing_system_mode: str,
    script_path: Path,
    source_root_arg: str | None,
    output_format: str,
    confirm_fingerprint: str | None,
    assume_yes: bool,
    command_prefix: tuple[str, ...] | None = None,
) -> dict[str, object]:
    plan, results, classification = build_cleanup_plan(
        project_root,
        source_root=source_root,
        profile=profile,
        existing_system_mode=existing_system_mode,
        script_path=script_path,
        source_root_arg=source_root_arg,
        output_format=output_format,
        command_prefix=command_prefix,
    )
    if confirm_fingerprint is None:
        results.append(StepResult("cleanup_confirm", "error", "Для confirm обязателен `--confirm-fingerprint`."))
    elif plan.plan_fingerprint == "—":
        results.append(StepResult("cleanup_confirm", "error", "Confirm недоступен: cleanup-plan не содержит безопасных целей удаления."))
    elif confirm_fingerprint != plan.plan_fingerprint:
        results.append(
            StepResult(
                "cleanup_confirm",
                "error",
                "Scope-lock нарушен: fingerprint confirm не совпадает с актуальным cleanup-plan. Сначала перезапустите `migrate-cleanup-plan`.",
            )
        )
    elif not assume_yes:
        results.append(StepResult("cleanup_confirm", "error", "Для confirm обязателен флаг `--yes`."))
    if has_errors(results):
        payload = {
            "skill": SKILL_NAME,
            "mode": "migrate-cleanup-confirm",
            "project_root": str(project_root),
            "profile": profile,
            "existing_system_classification": classification,
            "ok": False,
            "results": [item.to_payload() for item in results],
        }
        payload.update(plan.to_payload())
        return payload

    for candidate in sorted(plan.safe_delete, key=lambda item: (item.kind == "directory", item.path), reverse=True):
        _delete_path(Path(candidate.path))
    results.append(
        StepResult(
            "cleanup_confirm",
            "ok",
            f"Cleanup применён: TARGET_COUNT={plan.target_count}, COUNT={plan.count}.",
        )
    )
    payload = {
        "skill": SKILL_NAME,
        "mode": "migrate-cleanup-confirm",
        "project_root": str(project_root),
        "profile": profile,
        "existing_system_classification": classification,
        "ok": True,
        "results": [item.to_payload() for item in results],
    }
    payload.update(plan.to_payload())
    return payload
