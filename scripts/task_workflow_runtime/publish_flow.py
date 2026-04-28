"""Publish-flow orchestration."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

from .forge import resolve_forge_adapter
from .git_ops import (
    branch_exists,
    current_git_branch,
    detect_host_kind,
    ensure_delivery_branch,
    infer_base_branch,
    normalize_publication_type,
    remote_url,
    run_git,
)
from .models import (
    DELIVERY_ROW_PLACEHOLDER,
    PLACEHOLDER_BRANCH_VALUES,
    DeliveryUnit,
    PublicationSnapshot,
    StepResult,
    default_branch_name,
    default_delivery_branch_name,
    extract_delivery_branch_index,
    normalize_cleanup_value,
    normalize_delivery_status,
    normalize_unit_id,
    sanitize_delivery_text,
)
from .path_safety import resolve_task_dir_inside_project
from .registry_sync import (
    collect_delivery_units,
    find_delivery_unit,
    find_parent_branch,
    preflight_registry_summary,
    publication_body_ref_name,
    publish_preflight_ref_name,
    replace_delivery_unit,
    update_registry,
)
from .task_markdown import derive_summary_from_task, read_task_fields, update_task_file_with_delivery_units


PUBLISH_FLOW_TRANSITIONS = {
    "start": {
        "planned": {"local"},
        "local": {"local"},
    },
    "publish": {
        "local": {"draft"},
        "draft": {"review"},
    },
    "sync": {
        "planned": {"planned", "local"},
        "local": {"local", "draft", "closed"},
        "draft": {"draft", "review", "closed"},
        "review": {"review", "merged", "closed"},
        "merged": {"merged"},
        "closed": {"closed"},
    },
    "merge": {
        "review": {"merged"},
    },
    "close": {
        "local": {"closed"},
        "draft": {"closed"},
        "review": {"closed"},
    },
}



@dataclass(frozen=True)
class PublishOptions:
    action: str
    unit_id: str | None
    purpose: str | None
    base_branch: str | None
    head_branch: str | None
    from_ref: str | None
    host: str | None
    publication_type: str | None
    url: str | None
    merge_commit: str | None
    cleanup: str | None
    remote_name: str
    status: str | None
    create_publication: bool
    sync_from_host: bool
    title: str | None
    body: str | None
    summary: str | None
    today: str | None


@dataclass(frozen=True)
class PublishContext:
    project_root: Path
    task_dir: Path
    task_file: Path
    lines: list[str]
    fields: dict[str, str]
    delivery_units: list[DeliveryUnit]
    task_id: str
    short_name: str


@dataclass(frozen=True)
class PublishPreflight:
    selected_base_branch: str | None
    selected_head_branch: str | None
    start_ref: str | None
    current_unit: DeliveryUnit | None
    resolved_summary: str | None
    publication_summary: str | None
    effective_summary: str | None


@dataclass(frozen=True)
class PublishActionResult:
    delivery_units: list[DeliveryUnit]
    updated_unit: DeliveryUnit
    branch_name: str
    branch_action: str


def validate_transition(action: str, current_status: str, target_status: str) -> None:
    current = normalize_delivery_status(current_status)
    target = normalize_delivery_status(target_status)
    allowed_targets = PUBLISH_FLOW_TRANSITIONS[action].get(current, set())
    if target not in allowed_targets:
        raise ValueError(
            f"Недопустимый переход для `{action}`: {current} -> {target}. "
            f"Разрешены: {', '.join(sorted(allowed_targets)) or 'нет'}."
        )


def next_delivery_unit_id(project_root: Path, task_id: str, units: list[DeliveryUnit]) -> str:
    known_indexes = {int(unit.unit_id.split("-", 1)[1]) for unit in units}
    branches = run_git(project_root, "for-each-ref", "--format=%(refname:short)", "refs/heads").stdout.splitlines()
    for branch_name in branches:
        branch_index = extract_delivery_branch_index(task_id, branch_name)
        if branch_index is not None:
            known_indexes.add(branch_index)
    next_index = max(known_indexes, default=0) + 1
    return f"DU-{next_index:02d}"


def default_publication_title(fields: dict[str, str], purpose: str) -> str:
    task_id = fields.get("ID задачи", "").strip()
    return f"{task_id}: {purpose}"


def default_publication_body(
    fields: dict[str, str],
    purpose: str,
    task_dir: Path,
    *,
    summary: str | None = None,
) -> str:
    task_id = fields.get("ID задачи", "").strip()
    summary_value = summary or derive_summary_from_task(task_dir / "task.md") or "Публикация delivery unit."
    return (
        f"Task: {task_id}\n"
        f"Purpose: {purpose}\n"
        f"Summary: {summary_value}\n"
    )


def create_delivery_unit(
    *,
    unit_id: str,
    purpose: str,
    head_branch: str,
    base_branch: str,
) -> DeliveryUnit:
    return DeliveryUnit(
        unit_id=normalize_unit_id(unit_id),
        purpose=sanitize_delivery_text(purpose, allow_placeholder=False),
        head=head_branch,
        base=base_branch,
        host="none",
        publication_type="none",
        status="planned",
        url=DELIVERY_ROW_PLACEHOLDER,
        merge_commit=DELIVERY_ROW_PLACEHOLDER,
        cleanup="не требуется",
    )


def resolve_requested_host(
    project_root: Path,
    *,
    requested_host: str | None,
    url: str | None,
    remote_name: str,
) -> str:
    if requested_host and requested_host != "auto":
        return detect_host_kind(requested_host)
    url_host = detect_host_kind(url)
    if url_host != "none":
        return url_host
    return detect_host_kind(remote_url(project_root, remote_name))


def resolve_explicit_snapshot(
    current_unit: DeliveryUnit,
    *,
    host_kind: str,
    publication_type: str,
    target_status: str,
    url: str | None,
    merge_commit: str | None,
) -> PublicationSnapshot:
    resolved_url = url or current_unit.url or DELIVERY_ROW_PLACEHOLDER
    resolved_merge_commit = merge_commit or current_unit.merge_commit or DELIVERY_ROW_PLACEHOLDER
    return PublicationSnapshot(
        host=host_kind,
        publication_type=publication_type,
        status=target_status,
        url=resolved_url,
        head=current_unit.head,
        base=current_unit.base,
        merge_commit=resolved_merge_commit,
    )


def existing_publication_reference(current_unit: DeliveryUnit, url: str | None) -> str:
    for candidate in (url, current_unit.url, current_unit.head):
        resolved = (candidate or "").strip()
        if resolved and resolved != DELIVERY_ROW_PLACEHOLDER:
            return resolved
    raise ValueError("Для перехода существующей draft-публикации в review нужен URL или head-ветка.")


def resolve_publish_snapshot(
    project_root: Path,
    task_dir: Path,
    fields: dict[str, str],
    current_unit: DeliveryUnit,
    *,
    action: str,
    requested_host: str | None,
    requested_publication_type: str | None,
    requested_status: str | None,
    url: str | None,
    merge_commit: str | None,
    remote_name: str,
    create_publication: bool,
    sync_from_host: bool,
    title: str | None,
    body: str | None,
    summary: str | None,
) -> PublicationSnapshot:
    if create_publication and sync_from_host:
        raise ValueError("Нельзя одновременно использовать `--create-publication` и `--sync-from-host`.")

    host_kind = resolve_requested_host(
        project_root,
        requested_host=requested_host,
        url=url or current_unit.url,
        remote_name=remote_name,
    )
    publication_type = normalize_publication_type(requested_publication_type, host_kind)

    if action == "publish":
        if requested_status:
            target_status = normalize_delivery_status(requested_status)
        elif current_unit.status == "local":
            target_status = "draft"
        elif current_unit.status == "draft":
            target_status = "review"
        else:
            raise ValueError(
                "Для `publish` helper может только открыть draft-публикацию или перевести draft в review."
            )
    elif action == "merge":
        target_status = "merged"
    elif action == "close":
        target_status = "closed"
    else:
        target_status = normalize_delivery_status(requested_status or current_unit.status)

    if create_publication:
        if action != "publish":
            raise ValueError("`--create-publication` допустим только вместе с действием `publish`.")
        adapter = resolve_forge_adapter(project_root, host_kind, remote_name, url or current_unit.url)
        if current_unit.status == "draft" and target_status == "review":
            return adapter.update_publication(
                project_root,
                reference=existing_publication_reference(current_unit, url),
                head_branch=current_unit.head,
                base_branch=current_unit.base,
            )
        return adapter.create_publication(
            project_root,
            head_branch=current_unit.head,
            base_branch=current_unit.base,
            title=title or default_publication_title(fields, current_unit.purpose),
            body=body or default_publication_body(fields, current_unit.purpose, task_dir, summary=summary),
            draft=target_status == "draft",
        )

    if sync_from_host:
        adapter = resolve_forge_adapter(project_root, host_kind, remote_name, url or current_unit.url)
        return adapter.read_publication(
            project_root,
            reference=url or current_unit.url,
            head_branch=current_unit.head,
            base_branch=current_unit.base,
        )

    return resolve_explicit_snapshot(
        current_unit,
        host_kind=host_kind,
        publication_type=publication_type,
        target_status=target_status,
        url=url,
        merge_commit=merge_commit,
    )


def start_preflight_branch_context(
    project_root: Path,
    *,
    target_branch: str,
    base_branch: str,
    from_ref: str | None,
) -> str | None:
    if branch_exists(project_root, target_branch):
        return target_branch
    from .git_ops import resolve_delivery_start_ref

    return resolve_delivery_start_ref(project_root, base_branch=base_branch, from_ref=from_ref)


def related_task_context_branches(task_dir: Path, fields: dict[str, str], delivery_unit: DeliveryUnit) -> set[str]:
    branches = {
        delivery_unit.head,
        delivery_unit.base,
    }
    recorded_branch = fields.get("Ветка", "").strip()
    if recorded_branch:
        branches.add(recorded_branch)
    task_id = fields.get("ID задачи", "").strip()
    short_name = fields.get("Краткое имя", "").strip()
    if task_id and short_name:
        branches.add(default_branch_name(task_id, short_name))
    try:
        branches.add(find_parent_branch(task_dir))
    except ValueError:
        pass
    return {
        branch_name
        for branch_name in branches
        if branch_name and branch_name not in PLACEHOLDER_BRANCH_VALUES and branch_name != DELIVERY_ROW_PLACEHOLDER
    }


def branch_for_task_context(
    project_root: Path,
    task_dir: Path,
    fields: dict[str, str],
    delivery_unit: DeliveryUnit,
) -> str:
    active_branch = current_git_branch(project_root)
    allowed_branches = related_task_context_branches(task_dir, fields, delivery_unit)
    if active_branch:
        if active_branch in allowed_branches:
            return active_branch
        allowed_text = ", ".join(sorted(allowed_branches)) or "нет"
        raise ValueError(
            "Текущая checkout-ветка не относится к контексту этой задачи; helper остановлен. "
            f"Текущая ветка: `{active_branch}`. Ожидалось одно из: {allowed_text}."
        )
    if delivery_unit.head != DELIVERY_ROW_PLACEHOLDER:
        return delivery_unit.head
    recorded_branch = fields.get("Ветка", "").strip()
    if recorded_branch and recorded_branch not in PLACEHOLDER_BRANCH_VALUES:
        return recorded_branch
    return DELIVERY_ROW_PLACEHOLDER


def _resolve_task_dir(project_root: Path, task_dir: Path) -> Path:
    return resolve_task_dir_inside_project(project_root, task_dir)


def _load_publish_context(project_root: Path, task_dir: Path) -> PublishContext:
    project_root = project_root.resolve()
    task_dir = _resolve_task_dir(project_root, task_dir)
    task_file = task_dir / "task.md"
    if not task_file.exists():
        raise ValueError(f"Не найден task.md по пути {task_file}.")

    lines, fields = read_task_fields(task_file)
    delivery_units = collect_delivery_units(project_root, task_dir, fields, lines)
    task_id = fields.get("ID задачи", "").strip()
    short_name = fields.get("Краткое имя", "").strip()
    if not task_id or not short_name:
        raise ValueError("В task.md должны быть заполнены поля `ID задачи` и `Краткое имя`.")
    return PublishContext(
        project_root=project_root,
        task_dir=task_dir,
        task_file=task_file,
        lines=lines,
        fields=fields,
        delivery_units=delivery_units,
        task_id=task_id,
        short_name=short_name,
    )


def _resolve_start_preflight(ctx: PublishContext, options: PublishOptions) -> tuple[str, str, str | None]:
    selected_base_branch = options.base_branch or infer_base_branch(ctx.project_root)
    normalized_unit_id = normalize_unit_id(options.unit_id) if options.unit_id else next_delivery_unit_id(
        ctx.project_root,
        ctx.task_id,
        ctx.delivery_units,
    )
    selected_head_branch = options.head_branch or default_delivery_branch_name(
        ctx.task_id,
        normalized_unit_id,
        ctx.short_name,
    )
    start_ref = start_preflight_branch_context(
        ctx.project_root,
        target_branch=selected_head_branch,
        base_branch=selected_base_branch,
        from_ref=options.from_ref,
    )
    return selected_base_branch, selected_head_branch, start_ref


def _resolve_publish_preflight(ctx: PublishContext, options: PublishOptions) -> PublishPreflight:
    selected_base_branch: str | None = None
    selected_head_branch: str | None = None
    start_ref: str | None = None
    current_unit: DeliveryUnit | None = None

    if options.action == "start":
        selected_base_branch, selected_head_branch, start_ref = _resolve_start_preflight(ctx, options)
    else:
        current_unit = find_delivery_unit(ctx.delivery_units, options.unit_id)

    resolved_summary = preflight_registry_summary(
        ctx.project_root,
        ctx.task_dir,
        register_if_missing=False,
        summary=options.summary,
        ref_name=publish_preflight_ref_name(
            ctx.project_root,
            action=options.action,
            target_branch=selected_head_branch,
            start_ref=start_ref,
            current_unit=current_unit,
        ),
        allow_untracked_fallback=True,
    )
    publication_summary = _resolve_publication_summary(ctx, options, current_unit, resolved_summary)
    effective_summary = publication_summary if options.create_publication else resolved_summary
    return PublishPreflight(
        selected_base_branch=selected_base_branch,
        selected_head_branch=selected_head_branch,
        start_ref=start_ref,
        current_unit=current_unit,
        resolved_summary=resolved_summary,
        publication_summary=publication_summary,
        effective_summary=effective_summary,
    )


def _resolve_publication_summary(
    ctx: PublishContext,
    options: PublishOptions,
    current_unit: DeliveryUnit | None,
    resolved_summary: str | None,
) -> str | None:
    if not options.create_publication or options.body is not None or current_unit is None:
        return resolved_summary
    publication_ref_name = publication_body_ref_name(ctx.project_root, current_unit)
    if publication_ref_name is None:
        return resolved_summary
    return preflight_registry_summary(
        ctx.project_root,
        ctx.task_dir,
        register_if_missing=False,
        summary=options.summary,
        ref_name=publication_ref_name,
    )


def _apply_start_publish_action(ctx: PublishContext, options: PublishOptions, preflight: PublishPreflight) -> PublishActionResult:
    normalized_unit_id = normalize_unit_id(options.unit_id) if options.unit_id else next_delivery_unit_id(
        ctx.project_root,
        ctx.task_id,
        ctx.delivery_units,
    )
    existing_unit = next((item for item in ctx.delivery_units if item.unit_id == normalized_unit_id), None)
    if existing_unit is None and not options.purpose:
        raise ValueError("Для нового delivery unit нужно указать `--purpose`.")
    if preflight.selected_base_branch is None:
        raise ValueError("Для `start` не удалось определить base-ветку.")

    selected_head_branch = preflight.selected_head_branch or options.head_branch or default_delivery_branch_name(
        ctx.task_id,
        normalized_unit_id,
        ctx.short_name,
    )
    branch_action = ensure_delivery_branch(
        ctx.project_root,
        target_branch=selected_head_branch,
        base_branch=preflight.selected_base_branch,
        from_ref=options.from_ref,
    )
    current_unit = existing_unit or create_delivery_unit(
        unit_id=normalized_unit_id,
        purpose=options.purpose or "",
        head_branch=selected_head_branch,
        base_branch=preflight.selected_base_branch,
    )
    validate_transition(options.action, current_unit.status, "local")
    updated_unit = DeliveryUnit(
        unit_id=current_unit.unit_id,
        purpose=sanitize_delivery_text(options.purpose or current_unit.purpose, allow_placeholder=False),
        head=selected_head_branch,
        base=preflight.selected_base_branch,
        host="none",
        publication_type="none",
        status="local",
        url=DELIVERY_ROW_PLACEHOLDER,
        merge_commit=DELIVERY_ROW_PLACEHOLDER,
        cleanup="не требуется",
    )
    return PublishActionResult(
        delivery_units=replace_delivery_unit(ctx.delivery_units, updated_unit),
        updated_unit=updated_unit,
        branch_name=selected_head_branch,
        branch_action=branch_action,
    )


def _branch_name_for_snapshot(
    ctx: PublishContext,
    options: PublishOptions,
    current_unit: DeliveryUnit,
    snapshot: PublicationSnapshot,
) -> str:
    if options.create_publication:
        return branch_for_task_context(ctx.project_root, ctx.task_dir, ctx.fields, current_unit)
    branch_context_unit = DeliveryUnit(
        unit_id=current_unit.unit_id,
        purpose=current_unit.purpose,
        head=snapshot.head or current_unit.head,
        base=snapshot.base or current_unit.base,
        host=snapshot.host,
        publication_type=snapshot.publication_type,
        status=snapshot.status,
        url=snapshot.url,
        merge_commit=snapshot.merge_commit,
        cleanup=current_unit.cleanup,
    )
    return branch_for_task_context(ctx.project_root, ctx.task_dir, ctx.fields, branch_context_unit)


def _validate_existing_publish_action(options: PublishOptions, current_unit: DeliveryUnit, snapshot: PublicationSnapshot) -> None:
    validate_transition(options.action, current_unit.status, snapshot.status)
    if options.action == "publish" and snapshot.url == DELIVERY_ROW_PLACEHOLDER:
        raise ValueError("Для `publish` нужен URL публикации или сетевой adapter через `--create-publication`.")
    if options.action == "merge" and snapshot.merge_commit == DELIVERY_ROW_PLACEHOLDER:
        raise ValueError("Для `merge` нужен `--merge-commit` или успешный `--sync-from-host`.")
    if options.action == "close" and options.merge_commit:
        raise ValueError("Для `close` нельзя передавать `--merge-commit`.")


def _apply_existing_publish_action(ctx: PublishContext, options: PublishOptions, preflight: PublishPreflight) -> PublishActionResult:
    current_unit = preflight.current_unit
    if current_unit is None:
        raise ValueError("Для publish-flow действия нужен существующий delivery unit.")

    branch_name: str | None = None
    if options.create_publication:
        branch_name = branch_for_task_context(ctx.project_root, ctx.task_dir, ctx.fields, current_unit)

    snapshot = resolve_publish_snapshot(
        ctx.project_root,
        ctx.task_dir,
        ctx.fields,
        current_unit,
        action=options.action,
        requested_host=options.host,
        requested_publication_type=options.publication_type,
        requested_status=options.status,
        url=options.url,
        merge_commit=options.merge_commit,
        remote_name=options.remote_name,
        create_publication=options.create_publication,
        sync_from_host=options.sync_from_host,
        title=options.title,
        body=options.body,
        summary=preflight.effective_summary,
    )
    if branch_name is None:
        branch_name = _branch_name_for_snapshot(ctx, options, current_unit, snapshot)
    _validate_existing_publish_action(options, current_unit, snapshot)

    default_cleanup = current_unit.cleanup
    if snapshot.status in {"merged", "closed"} and default_cleanup == "не требуется":
        default_cleanup = "ожидается"
    updated_unit = DeliveryUnit(
        unit_id=current_unit.unit_id,
        purpose=current_unit.purpose,
        head=snapshot.head or current_unit.head,
        base=snapshot.base or current_unit.base,
        host=snapshot.host,
        publication_type=snapshot.publication_type,
        status=snapshot.status,
        url=snapshot.url,
        merge_commit=DELIVERY_ROW_PLACEHOLDER if options.action == "close" else snapshot.merge_commit,
        cleanup=normalize_cleanup_value(options.cleanup, default=default_cleanup),
    )
    return PublishActionResult(
        delivery_units=replace_delivery_unit(ctx.delivery_units, updated_unit),
        updated_unit=updated_unit,
        branch_name=branch_name,
        branch_action="recorded",
    )


def _apply_publish_action(ctx: PublishContext, options: PublishOptions, preflight: PublishPreflight) -> PublishActionResult:
    if options.action == "start":
        return _apply_start_publish_action(ctx, options, preflight)
    return _apply_existing_publish_action(ctx, options, preflight)


def _persist_publish_action(
    ctx: PublishContext,
    options: PublishOptions,
    action_result: PublishActionResult,
    effective_summary: str | None,
) -> tuple[dict[str, str], bool, str]:
    updated_fields = update_task_file_with_delivery_units(
        ctx.task_file,
        action_result.branch_name,
        action_result.delivery_units,
        today=options.today or date.today().isoformat(),
        summary=effective_summary,
    )
    registry_inserted, registry_path = update_registry(
        ctx.project_root,
        ctx.task_dir,
        updated_fields,
        branch_name=action_result.branch_name,
        register_if_missing=False,
        summary=effective_summary,
    )
    return updated_fields, registry_inserted, registry_path


def _publish_results(
    ctx: PublishContext,
    options: PublishOptions,
    action_result: PublishActionResult,
    registry_inserted: bool,
    registry_path: str,
) -> list[StepResult]:
    updated_unit = action_result.updated_unit
    results = [
        StepResult(
            "publish_block",
            "ok",
            f"Контур публикации синхронизирован: action={options.action}, unit={updated_unit.unit_id}, status={updated_unit.status}",
            str(ctx.task_file),
        )
    ]
    if options.action == "start":
        results.append(
            StepResult(
                "git_branch",
                "ok",
                f"Delivery-ветка синхронизирована: action={action_result.branch_action}, branch={action_result.branch_name}",
            )
        )
    if options.create_publication or options.sync_from_host:
        results.append(
            StepResult(
                "host_adapter",
                "ok",
                f"Host adapter использован: host={updated_unit.host}, type={updated_unit.publication_type}",
            )
        )
    registry_detail = "Строка в registry.md создана" if registry_inserted else "Строка в registry.md обновлена"
    results.append(StepResult("registry", "ok", registry_detail, registry_path))
    return results


def _publish_payload(
    ctx: PublishContext,
    options: PublishOptions,
    action_result: PublishActionResult,
    updated_fields: dict[str, str],
    results: list[StepResult],
) -> dict[str, object]:
    updated_unit = action_result.updated_unit
    return {
        "ok": True,
        "task_id": updated_fields.get("ID задачи"),
        "task_dir": str(ctx.task_dir),
        "action": options.action,
        "branch": action_result.branch_name,
        "branch_action": action_result.branch_action,
        "unit_id": updated_unit.unit_id,
        "delivery_status": updated_unit.status,
        "host": updated_unit.host,
        "publication_type": updated_unit.publication_type,
        "url": updated_unit.url,
        "merge_commit": updated_unit.merge_commit,
        "cleanup": updated_unit.cleanup,
        "results": [asdict(item) for item in results],
    }


def run_publish_flow(
    project_root: Path,
    task_dir: Path,
    *,
    action: str,
    unit_id: str | None,
    purpose: str | None,
    base_branch: str | None,
    head_branch: str | None,
    from_ref: str | None,
    host: str | None,
    publication_type: str | None,
    url: str | None,
    merge_commit: str | None,
    cleanup: str | None,
    remote_name: str,
    status: str | None,
    create_publication: bool,
    sync_from_host: bool,
    title: str | None,
    body: str | None,
    summary: str | None = None,
    today: str | None = None,
) -> dict[str, object]:
    options = PublishOptions(
        action=action,
        unit_id=unit_id,
        purpose=purpose,
        base_branch=base_branch,
        head_branch=head_branch,
        from_ref=from_ref,
        host=host,
        publication_type=publication_type,
        url=url,
        merge_commit=merge_commit,
        cleanup=cleanup,
        remote_name=remote_name,
        status=status,
        create_publication=create_publication,
        sync_from_host=sync_from_host,
        title=title,
        body=body,
        summary=summary,
        today=today,
    )
    ctx = _load_publish_context(project_root, task_dir)
    preflight = _resolve_publish_preflight(ctx, options)
    action_result = _apply_publish_action(ctx, options, preflight)
    updated_fields, registry_inserted, registry_path = _persist_publish_action(
        ctx,
        options,
        action_result,
        preflight.effective_summary,
    )
    results = _publish_results(ctx, options, action_result, registry_inserted, registry_path)
    return _publish_payload(ctx, options, action_result, updated_fields, results)
