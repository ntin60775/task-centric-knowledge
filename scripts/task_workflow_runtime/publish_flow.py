"""Publish-flow orchestration."""

from __future__ import annotations

from dataclasses import asdict
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
    project_root = project_root.resolve()
    task_dir = (project_root / task_dir).resolve() if not task_dir.is_absolute() else task_dir.resolve()
    task_file = task_dir / "task.md"
    if not task_file.exists():
        raise ValueError(f"Не найден task.md по пути {task_file}.")

    lines, fields = read_task_fields(task_file)
    delivery_units = collect_delivery_units(project_root, task_dir, fields, lines)
    task_id = fields.get("ID задачи", "").strip()
    short_name = fields.get("Краткое имя", "").strip()
    if not task_id or not short_name:
        raise ValueError("В task.md должны быть заполнены поля `ID задачи` и `Краткое имя`.")

    selected_base_branch: str | None = None
    selected_head_branch_for_preflight: str | None = None
    start_ref_for_preflight: str | None = None
    current_unit_for_preflight: DeliveryUnit | None = None
    if action == "start":
        selected_base_branch = base_branch or infer_base_branch(project_root)
        normalized_unit_id = normalize_unit_id(unit_id) if unit_id else next_delivery_unit_id(project_root, task_id, delivery_units)
        selected_head_branch_for_preflight = head_branch or default_delivery_branch_name(
            task_id,
            normalized_unit_id,
            short_name,
        )
        start_ref_for_preflight = start_preflight_branch_context(
            project_root,
            target_branch=selected_head_branch_for_preflight,
            base_branch=selected_base_branch,
            from_ref=from_ref,
        )
    else:
        current_unit_for_preflight = find_delivery_unit(delivery_units, unit_id)

    resolved_summary = preflight_registry_summary(
        project_root,
        task_dir,
        register_if_missing=False,
        summary=summary,
        ref_name=publish_preflight_ref_name(
            project_root,
            action=action,
            target_branch=selected_head_branch_for_preflight,
            start_ref=start_ref_for_preflight,
            current_unit=current_unit_for_preflight,
        ),
        allow_untracked_fallback=True,
    )
    publication_summary = resolved_summary
    if create_publication and body is None and current_unit_for_preflight is not None:
        publication_ref_name = publication_body_ref_name(project_root, current_unit_for_preflight)
        if publication_ref_name is not None:
            publication_summary = preflight_registry_summary(
                project_root,
                task_dir,
                register_if_missing=False,
                summary=summary,
                ref_name=publication_ref_name,
            )
    effective_summary = publication_summary if create_publication else resolved_summary

    results: list[StepResult] = []
    today_value = today or date.today().isoformat()
    branch_action = "recorded"

    if action == "start":
        if unit_id:
            normalized_unit_id = normalize_unit_id(unit_id)
            existing_unit = next((item for item in delivery_units if item.unit_id == normalized_unit_id), None)
        else:
            normalized_unit_id = next_delivery_unit_id(project_root, task_id, delivery_units)
            existing_unit = None
        if existing_unit is None and not purpose:
            raise ValueError("Для нового delivery unit нужно указать `--purpose`.")
        assert selected_base_branch is not None
        selected_head_branch = selected_head_branch_for_preflight or head_branch or default_delivery_branch_name(
            task_id,
            normalized_unit_id,
            short_name,
        )
        branch_action = ensure_delivery_branch(
            project_root,
            target_branch=selected_head_branch,
            base_branch=selected_base_branch,
            from_ref=from_ref,
        )
        current_unit = existing_unit or create_delivery_unit(
            unit_id=normalized_unit_id,
            purpose=purpose or "",
            head_branch=selected_head_branch,
            base_branch=selected_base_branch,
        )
        validate_transition(action, current_unit.status, "local")
        updated_unit = DeliveryUnit(
            unit_id=current_unit.unit_id,
            purpose=sanitize_delivery_text(purpose or current_unit.purpose, allow_placeholder=False),
            head=selected_head_branch,
            base=selected_base_branch,
            host="none",
            publication_type="none",
            status="local",
            url=DELIVERY_ROW_PLACEHOLDER,
            merge_commit=DELIVERY_ROW_PLACEHOLDER,
            cleanup="не требуется",
        )
        delivery_units = replace_delivery_unit(delivery_units, updated_unit)
        branch_name = selected_head_branch
    else:
        current_unit = current_unit_for_preflight
        assert current_unit is not None
        if create_publication:
            branch_name = branch_for_task_context(project_root, task_dir, fields, current_unit)
        snapshot = resolve_publish_snapshot(
            project_root,
            task_dir,
            fields,
            current_unit,
            action=action,
            requested_host=host,
            requested_publication_type=publication_type,
            requested_status=status,
            url=url,
            merge_commit=merge_commit,
            remote_name=remote_name,
            create_publication=create_publication,
            sync_from_host=sync_from_host,
            title=title,
            body=body,
            summary=effective_summary,
        )
        if not create_publication:
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
            branch_name = branch_for_task_context(project_root, task_dir, fields, branch_context_unit)
        validate_transition(action, current_unit.status, snapshot.status)
        if action == "publish" and snapshot.url == DELIVERY_ROW_PLACEHOLDER:
            raise ValueError(
                "Для `publish` нужен URL публикации или сетевой adapter через `--create-publication`."
            )
        if action == "merge" and snapshot.merge_commit == DELIVERY_ROW_PLACEHOLDER:
            raise ValueError("Для `merge` нужен `--merge-commit` или успешный `--sync-from-host`.")
        if action == "close" and merge_commit:
            raise ValueError("Для `close` нельзя передавать `--merge-commit`.")
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
            merge_commit=DELIVERY_ROW_PLACEHOLDER if action == "close" else snapshot.merge_commit,
            cleanup=normalize_cleanup_value(cleanup, default=default_cleanup),
        )
        delivery_units = replace_delivery_unit(delivery_units, updated_unit)

    updated_fields = update_task_file_with_delivery_units(
        task_file,
        branch_name,
        delivery_units,
        today=today_value,
        summary=effective_summary,
    )
    registry_inserted, registry_path = update_registry(
        project_root,
        task_dir,
        updated_fields,
        branch_name=branch_name,
        register_if_missing=False,
        summary=effective_summary,
    )

    results.append(
        StepResult(
            "publish_block",
            "ok",
            f"Контур публикации синхронизирован: action={action}, unit={updated_unit.unit_id}, status={updated_unit.status}",
            str(task_file),
        )
    )
    if action == "start":
        results.append(
            StepResult(
                "git_branch",
                "ok",
                f"Delivery-ветка синхронизирована: action={branch_action}, branch={branch_name}",
            )
        )
    if create_publication or sync_from_host:
        results.append(
            StepResult(
                "host_adapter",
                "ok",
                f"Host adapter использован: host={updated_unit.host}, type={updated_unit.publication_type}",
            )
        )
    registry_detail = "Строка в registry.md обновлена"
    if registry_inserted:
        registry_detail = "Строка в registry.md создана"
    results.append(StepResult("registry", "ok", registry_detail, registry_path))

    return {
        "ok": True,
        "task_id": updated_fields.get("ID задачи"),
        "task_dir": str(task_dir),
        "action": action,
        "branch": branch_name,
        "branch_action": branch_action,
        "unit_id": updated_unit.unit_id,
        "delivery_status": updated_unit.status,
        "host": updated_unit.host,
        "publication_type": updated_unit.publication_type,
        "url": updated_unit.url,
        "merge_commit": updated_unit.merge_commit,
        "cleanup": updated_unit.cleanup,
        "results": [asdict(item) for item in results],
    }
