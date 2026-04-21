"""Registry synchronization and task-context preflight helpers."""

from __future__ import annotations

from pathlib import Path

from .git_ops import branch_exists, current_git_branch, dirty_paths, infer_base_branch, run_git
from .models import (
    DELIVERY_ROW_PLACEHOLDER,
    DELIVERY_STATUS_PRIORITY,
    PLACEHOLDER_BRANCH_VALUES,
    TASK_SUMMARY_FIELD,
    DeliveryUnit,
    DeliveryUnitVersion,
    default_branch_name,
    delivery_unit_index,
    extract_delivery_branch_index,
    normalize_delivery_status,
    normalize_table_value,
    sanitize_registry_summary,
)
from .task_markdown import (
    count_task_field_occurrences,
    derive_goal_summary_from_lines,
    derive_goal_summary_from_task,
    parse_delivery_units,
    parse_task_fields,
    read_task_fields,
    task_summary_from_fields,
)


def task_file_is_dirty(project_root: Path, task_file_relative: str) -> bool:
    normalized_target = task_file_relative.replace("\\", "/").rstrip("/")
    return any(path.replace("\\", "/").rstrip("/") == normalized_target for path in dirty_paths(project_root))


def task_file_history_depth(project_root: Path, ref_name: str, task_file_relative: str) -> int:
    completed = run_git(project_root, "rev-list", "--count", ref_name, "--", task_file_relative, check=False)
    if completed.returncode != 0:
        return 0
    return int((completed.stdout or "0").strip() or "0")


def parse_task_file_freshness(output: str, fallback_ref: str, history_depth: int) -> tuple[int, int, int, str]:
    payload = output.strip()
    if not payload:
        return (0, 0, history_depth, fallback_ref)
    timestamp_text, _, commit_id = payload.partition("\x00")
    timestamp = int(timestamp_text or "0")
    return (1, timestamp, history_depth, commit_id or fallback_ref)


def current_task_file_freshness(
    project_root: Path,
    task_file: Path,
    task_file_relative: str,
) -> tuple[int, int, int, str]:
    active_branch = current_git_branch(project_root) or "HEAD"
    history_depth = task_file_history_depth(project_root, active_branch, task_file_relative)
    if task_file_is_dirty(project_root, task_file_relative):
        return (2, task_file.stat().st_mtime_ns, history_depth, f"WORKTREE:{active_branch}")
    completed = run_git(
        project_root,
        "log",
        "-1",
        "--format=%ct%x00%H",
        active_branch,
        "--",
        task_file_relative,
        check=False,
    )
    if completed.returncode == 0:
        parsed = parse_task_file_freshness(completed.stdout, active_branch, history_depth)
        if parsed[0] != 0:
            return parsed
    completed = run_git(project_root, "log", "-1", "--format=%ct%x00%H", active_branch, check=False)
    return parse_task_file_freshness(completed.stdout, active_branch, history_depth)


def ref_task_file_freshness(project_root: Path, ref_name: str, task_file_relative: str) -> tuple[int, int, int, str]:
    history_depth = task_file_history_depth(project_root, ref_name, task_file_relative)
    completed = run_git(
        project_root,
        "log",
        "-1",
        "--format=%ct%x00%H",
        ref_name,
        "--",
        task_file_relative,
        check=False,
    )
    if completed.returncode == 0:
        parsed = parse_task_file_freshness(completed.stdout, ref_name, history_depth)
        if parsed[0] != 0:
            return parsed
    completed = run_git(project_root, "log", "-1", "--format=%ct%x00%H", ref_name, check=False)
    return parse_task_file_freshness(completed.stdout, ref_name, history_depth)


def delivery_unit_merge_key(version: DeliveryUnitVersion) -> tuple[int, tuple[int, int, int, str], int, int, int, int]:
    unit = version.unit
    return (
        DELIVERY_STATUS_PRIORITY.get(normalize_delivery_status(unit.status), -1),
        version.freshness_rank,
        int(unit.merge_commit != DELIVERY_ROW_PLACEHOLDER),
        int(unit.url != DELIVERY_ROW_PLACEHOLDER),
        int(unit.cleanup not in {"не требуется", DELIVERY_ROW_PLACEHOLDER}),
        sum(
            int(value not in {DELIVERY_ROW_PLACEHOLDER, "none", "не требуется"})
            for value in (
                unit.purpose,
                unit.head,
                unit.base,
                unit.host,
                unit.publication_type,
                unit.url,
                unit.merge_commit,
                unit.cleanup,
            )
        ),
    )


def preferred_delivery_value(
    versions: list[DeliveryUnitVersion],
    field_name: str,
    *,
    placeholders: set[str],
) -> str:
    for version in versions:
        unit = version.unit
        value = getattr(unit, field_name)
        if value not in placeholders:
            return value
    return getattr(versions[0].unit, field_name)


def merge_delivery_unit_versions(versions: list[DeliveryUnitVersion]) -> DeliveryUnit:
    if not versions:
        raise ValueError("Нельзя объединить пустой список delivery units.")
    ordered_versions = sorted(versions, key=delivery_unit_merge_key, reverse=True)
    best = ordered_versions[0].unit
    return DeliveryUnit(
        unit_id=best.unit_id,
        purpose=preferred_delivery_value(ordered_versions, "purpose", placeholders={DELIVERY_ROW_PLACEHOLDER}),
        head=preferred_delivery_value(ordered_versions, "head", placeholders={DELIVERY_ROW_PLACEHOLDER}),
        base=preferred_delivery_value(ordered_versions, "base", placeholders={DELIVERY_ROW_PLACEHOLDER}),
        host=preferred_delivery_value(ordered_versions, "host", placeholders={DELIVERY_ROW_PLACEHOLDER, "none"}),
        publication_type=preferred_delivery_value(
            ordered_versions,
            "publication_type",
            placeholders={DELIVERY_ROW_PLACEHOLDER, "none"},
        ),
        status=best.status,
        url=preferred_delivery_value(ordered_versions, "url", placeholders={DELIVERY_ROW_PLACEHOLDER}),
        merge_commit=preferred_delivery_value(
            ordered_versions,
            "merge_commit",
            placeholders={DELIVERY_ROW_PLACEHOLDER},
        ),
        cleanup=preferred_delivery_value(
            ordered_versions,
            "cleanup",
            placeholders={DELIVERY_ROW_PLACEHOLDER, "не требуется"},
        ),
    )


def related_publish_refs(project_root: Path, task_dir: Path, fields: dict[str, str]) -> list[str]:
    task_id = fields.get("ID задачи", "").strip()
    short_name = fields.get("Краткое имя", "").strip()
    refs: set[str] = set()
    all_branches = run_git(project_root, "for-each-ref", "--format=%(refname:short)", "refs/heads").stdout.splitlines()
    for branch_name in all_branches:
        if extract_delivery_branch_index(task_id, branch_name) is not None:
            refs.add(branch_name)
    recorded_branch = fields.get("Ветка", "").strip()
    if recorded_branch and recorded_branch not in PLACEHOLDER_BRANCH_VALUES and branch_exists(project_root, recorded_branch):
        refs.add(recorded_branch)
    if task_id and short_name:
        default_task_branch = default_branch_name(task_id, short_name)
        if branch_exists(project_root, default_task_branch):
            refs.add(default_task_branch)
    active_branch = current_git_branch(project_root)
    refs.discard(active_branch)
    return sorted(refs)


def read_task_lines_from_ref(project_root: Path, ref_name: str, task_file_relative: str) -> list[str] | None:
    completed = run_git(project_root, "show", f"{ref_name}:{task_file_relative}", check=False)
    if completed.returncode != 0:
        return None
    return completed.stdout.splitlines()


def path_exists_in_head(project_root: Path, relative_path: str) -> bool:
    return read_task_lines_from_ref(project_root, "HEAD", relative_path) is not None


def collect_delivery_units(
    project_root: Path,
    task_dir: Path,
    fields: dict[str, str],
    current_lines: list[str],
) -> list[DeliveryUnit]:
    task_file_relative = (task_dir / "task.md").relative_to(project_root).as_posix()
    units_by_id: dict[str, list[DeliveryUnitVersion]] = {}
    current_freshness = current_task_file_freshness(project_root, task_dir / "task.md", task_file_relative)
    for unit in parse_delivery_units(current_lines):
        units_by_id.setdefault(unit.unit_id, []).append(
            DeliveryUnitVersion(unit=unit, freshness_rank=current_freshness)
        )
    for ref_name in related_publish_refs(project_root, task_dir, fields):
        ref_lines = read_task_lines_from_ref(project_root, ref_name, task_file_relative)
        if ref_lines is None:
            continue
        ref_freshness = ref_task_file_freshness(project_root, ref_name, task_file_relative)
        for unit in parse_delivery_units(ref_lines):
            units_by_id.setdefault(unit.unit_id, []).append(
                DeliveryUnitVersion(unit=unit, freshness_rank=ref_freshness)
            )
    return sorted(
        (merge_delivery_unit_versions(unit_versions) for unit_versions in units_by_id.values()),
        key=lambda item: delivery_unit_index(item.unit_id),
    )


def find_delivery_unit(units: list[DeliveryUnit], unit_id: str | None) -> DeliveryUnit:
    if unit_id:
        normalized_id = normalize_table_value(unit_id)
        for unit in units:
            if unit.unit_id == normalized_id or unit.unit_id == unit_id:
                return unit
        from .models import normalize_unit_id  # local import to avoid unused at module load

        normalized_id = normalize_unit_id(unit_id)
        for unit in units:
            if unit.unit_id == normalized_id:
                return unit
        raise ValueError(f"В publish-блоке не найден delivery unit {normalized_id}.")
    if len(units) == 1:
        return units[0]
    raise ValueError("Нужно явно указать `--unit-id`, потому что delivery unit неоднозначен.")


def replace_delivery_unit(units: list[DeliveryUnit], updated_unit: DeliveryUnit) -> list[DeliveryUnit]:
    replaced = False
    result: list[DeliveryUnit] = []
    for unit in units:
        if unit.unit_id == updated_unit.unit_id:
            result.append(updated_unit)
            replaced = True
            continue
        result.append(unit)
    if not replaced:
        result.append(updated_unit)
    return sorted(result, key=lambda item: delivery_unit_index(item.unit_id))


def tracked_goal_summary(project_root: Path, task_dir: Path) -> str | None:
    task_file_relative = (task_dir / "task.md").relative_to(project_root).as_posix()
    tracked_lines = read_task_lines_from_ref(project_root, "HEAD", task_file_relative)
    if tracked_lines is None:
        return None
    return derive_goal_summary_from_lines(tracked_lines)


def commit_history_for_path(project_root: Path, relative_path: str, *, ref_name: str = "HEAD") -> list[str]:
    return run_git(project_root, "log", ref_name, "--format=%H", "--", relative_path).stdout.splitlines()


def commit_introducing_goal_summary(
    project_root: Path,
    task_dir: Path,
    goal_summary: str,
    *,
    ref_name: str = "HEAD",
) -> str | None:
    task_file_relative = (task_dir / "task.md").relative_to(project_root).as_posix()
    matching_commit: str | None = None
    for commit_id in commit_history_for_path(project_root, task_file_relative, ref_name=ref_name):
        lines = read_task_lines_from_ref(project_root, commit_id, task_file_relative)
        if lines is None:
            continue
        if derive_goal_summary_from_lines(lines) == goal_summary:
            matching_commit = commit_id
            continue
        if matching_commit is not None:
            return matching_commit
    return matching_commit


def registry_summary_from_lines(lines: list[str], task_id: str) -> tuple[str | None, bool]:
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("| `"):
            continue
        parts = [part.strip() for part in stripped.strip("|").split("|")]
        if len(parts) != 7:
            continue
        row_task_id = normalize_table_value(parts[0])
        if row_task_id != task_id:
            continue
        return parts[6].strip(), True
    return None, False


def commit_introducing_registry_summary(
    project_root: Path,
    task_id: str,
    summary: str,
    *,
    ref_name: str = "HEAD",
) -> str | None:
    registry_relative = "knowledge/tasks/registry.md"
    matching_commit: str | None = None
    for commit_id in commit_history_for_path(project_root, registry_relative, ref_name=ref_name):
        lines = read_task_lines_from_ref(project_root, commit_id, registry_relative)
        if lines is None:
            continue
        registry_summary, row_exists = registry_summary_from_lines(lines, task_id)
        if row_exists and registry_summary == summary:
            matching_commit = commit_id
            continue
        if matching_commit is not None:
            return matching_commit
    return matching_commit


def commit_is_ancestor(project_root: Path, ancestor: str, descendant: str) -> bool:
    completed = run_git(project_root, "merge-base", "--is-ancestor", ancestor, descendant, check=False)
    return completed.returncode == 0


def legacy_registry_summary_candidate(value: str | None) -> str | None:
    sanitized = sanitize_registry_summary(value or "")
    if not sanitized or sanitized == DELIVERY_ROW_PLACEHOLDER:
        return None
    return sanitized


def legacy_goal_summary_overrides_registry(
    project_root: Path,
    task_dir: Path,
    *,
    task_id: str,
    goal_summary: str | None,
    existing_summary: str | None,
    ref_name: str | None = None,
) -> bool:
    sanitized_existing = legacy_registry_summary_candidate(existing_summary)
    if not goal_summary or not sanitized_existing or goal_summary == sanitized_existing:
        return False
    history_ref_name = ref_name or "HEAD"
    if ref_name is None:
        current_head_goal_summary = tracked_goal_summary(project_root, task_dir)
        if current_head_goal_summary not in (None, goal_summary):
            return True
    goal_commit = commit_introducing_goal_summary(
        project_root,
        task_dir,
        goal_summary,
        ref_name=history_ref_name,
    )
    if goal_commit is None:
        return False
    registry_commit = commit_introducing_registry_summary(
        project_root,
        task_id,
        sanitized_existing,
        ref_name=history_ref_name,
    )
    if registry_commit is None:
        return True
    if goal_commit == registry_commit:
        return False
    return commit_is_ancestor(project_root, registry_commit, goal_commit)


def preferred_registry_summary(
    fields: dict[str, str],
    *,
    goal_summary: str | None,
    summary: str | None,
    existing_summary: str | None = None,
    prefer_goal_over_existing: bool = False,
    ignore_task_summary: bool = False,
) -> str | None:
    explicit_task_summary = task_summary_from_fields(fields)
    if explicit_task_summary and not ignore_task_summary:
        return explicit_task_summary

    explicit_summary = legacy_registry_summary_candidate(summary)
    if explicit_summary:
        return explicit_summary

    existing_registry_summary = legacy_registry_summary_candidate(existing_summary)
    if prefer_goal_over_existing and goal_summary:
        return goal_summary
    if existing_registry_summary:
        return existing_registry_summary

    return goal_summary


def read_registry_lines(
    project_root: Path,
    *,
    ref_name: str | None = None,
    allow_untracked_fallback: bool = False,
) -> list[str]:
    registry_relative = "knowledge/tasks/registry.md"
    registry_path = project_root / registry_relative
    if ref_name is None:
        if not registry_path.exists():
            raise ValueError("Не найден knowledge/tasks/registry.md.")
        return registry_path.read_text(encoding="utf-8").splitlines()
    completed = run_git(project_root, "show", f"{ref_name}:{registry_relative}", check=False)
    if completed.returncode != 0:
        if (
            allow_untracked_fallback
            and registry_path.exists()
            and not path_exists_in_head(project_root, registry_relative)
        ):
            return registry_path.read_text(encoding="utf-8").splitlines()
        raise ValueError(f"Не найден knowledge/tasks/registry.md в `{ref_name}`.")
    return completed.stdout.splitlines()


def read_existing_registry_summary(
    project_root: Path,
    task_id: str,
    *,
    ref_name: str | None = None,
    allow_untracked_fallback: bool = False,
) -> tuple[str | None, bool]:
    lines = read_registry_lines(
        project_root,
        ref_name=ref_name,
        allow_untracked_fallback=allow_untracked_fallback,
    )
    return registry_summary_from_lines(lines, task_id)


def read_task_context(
    project_root: Path,
    task_dir: Path,
    *,
    ref_name: str | None = None,
    allow_untracked_fallback: bool = False,
) -> tuple[list[str], dict[str, str], str | None]:
    task_file = task_dir / "task.md"
    if ref_name is None:
        lines, fields = read_task_fields(task_file)
    else:
        task_file_relative = task_file.relative_to(project_root).as_posix()
        lines = read_task_lines_from_ref(project_root, ref_name, task_file_relative)
        if lines is None:
            if (
                allow_untracked_fallback
                and task_file.exists()
                and not path_exists_in_head(project_root, task_file_relative)
            ):
                lines, fields = read_task_fields(task_file)
                return lines, fields, derive_goal_summary_from_lines(lines)
            raise ValueError(f"Не найден {task_file_relative} в `{ref_name}`.")
        fields = parse_task_fields(lines)
    return lines, fields, derive_goal_summary_from_lines(lines)


def find_parent_branch(task_dir: Path, *, project_root: Path | None = None) -> str:
    if task_dir.parent.name != "subtasks":
        raise ValueError("Нельзя наследовать ветку: задача не находится внутри каталога subtasks/.")
    parent_task_file = task_dir.parent.parent / "task.md"
    if not parent_task_file.exists():
        raise ValueError("Нельзя наследовать ветку: у родительской задачи отсутствует task.md.")
    _, parent_fields = read_task_fields(parent_task_file)
    parent_branch = parent_fields.get("Ветка", "").strip()
    if project_root is not None:
        parent_task_id = parent_fields.get("ID задачи", "").strip()
        parent_short_name = parent_fields.get("Краткое имя", "").strip()
        if parent_task_id and parent_short_name:
            default_parent_branch = default_branch_name(parent_task_id, parent_short_name)
            if branch_exists(project_root, default_parent_branch):
                parent_task_relative = parent_task_file.relative_to(project_root).as_posix()
                ref_lines = read_task_lines_from_ref(project_root, default_parent_branch, parent_task_relative)
                ref_branch = ""
                if ref_lines is not None:
                    ref_fields = parse_task_fields(ref_lines)
                    ref_branch = ref_fields.get("Ветка", "").strip()
                if parent_branch not in PLACEHOLDER_BRANCH_VALUES:
                    inferred_base_branch = infer_base_branch(project_root)
                    if (
                        ref_branch not in PLACEHOLDER_BRANCH_VALUES
                        and parent_branch == inferred_base_branch
                        and ref_branch != parent_branch
                        and not commit_is_ancestor(project_root, default_parent_branch, "HEAD")
                    ):
                        return ref_branch
                    return parent_branch
                if ref_branch not in PLACEHOLDER_BRANCH_VALUES:
                    return ref_branch
                return default_parent_branch
    if parent_branch in PLACEHOLDER_BRANCH_VALUES:
        raise ValueError("Нельзя наследовать ветку: у родительской задачи ветка ещё не зафиксирована.")
    return parent_branch


def preflight_registry_summary(
    project_root: Path,
    task_dir: Path,
    *,
    register_if_missing: bool,
    summary: str | None,
    ref_name: str | None = None,
    allow_untracked_fallback: bool = False,
) -> str:
    lines, fields, goal_summary = read_task_context(
        project_root,
        task_dir,
        ref_name=ref_name,
        allow_untracked_fallback=allow_untracked_fallback,
    )
    task_id = fields.get("ID задачи", "").strip()
    existing_summary, row_exists = read_existing_registry_summary(
        project_root,
        task_id,
        ref_name=ref_name,
        allow_untracked_fallback=allow_untracked_fallback,
    )
    if not row_exists and not register_if_missing:
        raise ValueError(f"В knowledge/tasks/registry.md не найдена строка для {task_id}.")
    prefer_goal_over_existing = legacy_goal_summary_overrides_registry(
        project_root,
        task_dir,
        task_id=task_id,
        goal_summary=goal_summary,
        existing_summary=existing_summary,
        ref_name=ref_name,
    )
    explicit_summary = legacy_registry_summary_candidate(summary)
    ignore_task_summary = count_task_field_occurrences(lines, TASK_SUMMARY_FIELD) > 1 and bool(explicit_summary)
    resolved_summary = preferred_registry_summary(
        fields,
        goal_summary=goal_summary,
        summary=summary,
        existing_summary=existing_summary,
        prefer_goal_over_existing=prefer_goal_over_existing,
        ignore_task_summary=ignore_task_summary,
    )
    if not resolved_summary:
        raise ValueError(
            "Для строки registry.md нужно заполнить `Человекочитаемое описание` в task.md, "
            "передать `--summary` или заполнить секцию `Цель`."
        )
    return resolved_summary


def sync_preflight_ref_name(
    project_root: Path,
    *,
    create_branch: bool,
    target_branch: str,
) -> str | None:
    active_branch = current_git_branch(project_root)
    if create_branch and active_branch != target_branch and branch_exists(project_root, target_branch):
        return target_branch
    return None


def publish_preflight_ref_name(
    project_root: Path,
    *,
    action: str,
    target_branch: str | None,
    start_ref: str | None,
    current_unit: DeliveryUnit | None = None,
) -> str | None:
    if action == "start":
        if target_branch and branch_exists(project_root, target_branch):
            return target_branch
        return start_ref
    if current_unit and current_unit.head != DELIVERY_ROW_PLACEHOLDER and branch_exists(project_root, current_unit.head):
        active_branch = current_git_branch(project_root)
        if not active_branch or active_branch != current_unit.head:
            return current_unit.head
    return None


def publication_body_ref_name(project_root: Path, current_unit: DeliveryUnit) -> str | None:
    if current_git_branch(project_root) == current_unit.head:
        return None
    if current_unit.head != DELIVERY_ROW_PLACEHOLDER and branch_exists(project_root, current_unit.head):
        return current_unit.head
    return None


def format_registry_row(
    task_id: str,
    parent_id: str,
    status: str,
    priority: str,
    branch_name: str,
    task_dir_relative: str,
    summary: str,
) -> str:
    safe_summary = sanitize_registry_summary(summary) or DELIVERY_ROW_PLACEHOLDER
    return (
        f"| `{task_id}` | `{parent_id}` | `{status}` | `{priority}` | "
        f"`{branch_name}` | `{task_dir_relative}` | {safe_summary} |"
    )


def update_registry(
    project_root: Path,
    task_dir: Path,
    fields: dict[str, str],
    *,
    branch_name: str,
    register_if_missing: bool,
    summary: str | None,
) -> tuple[bool, str]:
    registry_path = project_root / "knowledge" / "tasks" / "registry.md"
    if not registry_path.exists():
        raise ValueError("Не найден knowledge/tasks/registry.md.")

    lines = registry_path.read_text(encoding="utf-8").splitlines()
    task_id = fields.get("ID задачи", "").strip()
    parent_id = fields.get("Parent ID", "—").strip() or "—"
    status = fields.get("Статус", "").strip()
    priority = fields.get("Приоритет", "").strip()
    task_dir_relative = task_dir.relative_to(project_root).as_posix().rstrip("/") + "/"
    task_file = task_dir / "task.md"

    existing_summary: str | None = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("| `"):
            continue
        parts = [part.strip() for part in stripped.strip("|").split("|")]
        if len(parts) != 7:
            continue
        row_task_id = normalize_table_value(parts[0])
        if row_task_id != task_id:
            continue
        existing_summary = parts[6].strip()
        new_summary = preferred_registry_summary(
            fields,
            goal_summary=derive_goal_summary_from_task(task_file),
            summary=summary,
            existing_summary=existing_summary,
        )
        if not new_summary:
            raise ValueError(
                "Для строки registry.md нужно заполнить `Человекочитаемое описание` в task.md, "
                "передать `--summary` или заполнить секцию `Цель`."
            )
        lines[index] = format_registry_row(
            task_id,
            parent_id,
            status,
            priority,
            branch_name,
            task_dir_relative,
            new_summary,
        )
        registry_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return False, str(registry_path)

    if not register_if_missing:
        raise ValueError(f"В knowledge/tasks/registry.md не найдена строка для {task_id}.")

    new_summary = preferred_registry_summary(
        fields,
        goal_summary=derive_goal_summary_from_task(task_file),
        summary=summary,
    )
    if not new_summary:
        raise ValueError(
            "Для новой строки registry.md нужно заполнить `Человекочитаемое описание` в task.md, "
            "передать `--summary` или заполнить секцию `Цель`."
        )

    lines.append(
        format_registry_row(
            task_id,
            parent_id,
            status,
            priority,
            branch_name,
            task_dir_relative,
            new_summary,
        )
    )
    registry_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True, str(registry_path)


def dirty_paths_are_task_scoped(project_root: Path, task_dir: Path) -> bool:
    task_dir_relative = task_dir.relative_to(project_root).as_posix().rstrip("/") + "/"
    registry_relative = "knowledge/tasks/registry.md"
    for path in dirty_paths(project_root):
        normalized = path.replace("\\", "/").rstrip("/")
        if normalized == registry_relative:
            continue
        if normalized and task_dir_relative.startswith(normalized + "/"):
            continue
        if normalized and registry_relative.startswith(normalized + "/"):
            continue
        if normalized.startswith(task_dir_relative.rstrip("/")):
            continue
        return False
    return True
