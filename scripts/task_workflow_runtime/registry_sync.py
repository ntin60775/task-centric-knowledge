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


## @brief Check if a task file has uncommitted changes.
#  @param project_root Absolute path to the project root.
#  @param task_file_relative Relative path to the task file.
#  @return True if the file appears in dirty paths.
def task_file_is_dirty(project_root: Path, task_file_relative: str) -> bool:
    normalized_target = task_file_relative.replace("\\", "/").rstrip("/")
    return any(path.replace("\\", "/").rstrip("/") == normalized_target for path in dirty_paths(project_root))


## @brief Count commits touching a task file on a given ref.
#  @param project_root Absolute path to the project root.
#  @param ref_name Git ref to inspect.
#  @param task_file_relative Relative path to the task file.
#  @return Commit count, or 0 on error.
def task_file_history_depth(project_root: Path, ref_name: str, task_file_relative: str) -> int:
    completed = run_git(project_root, "rev-list", "--count", ref_name, "--", task_file_relative, check=False)
    if completed.returncode != 0:
        return 0
    return int((completed.stdout or "0").strip() or "0")


## @brief Parse git log output into a freshness tuple.
#  @param output Raw stdout from git log.
#  @param fallback_ref Ref name to use when output is empty.
#  @param history_depth Precomputed history depth.
#  @return Tuple of (source_flag, timestamp, history_depth, commit_id).
def parse_task_file_freshness(output: str, fallback_ref: str, history_depth: int) -> tuple[int, int, int, str]:
    payload = output.strip()
    if not payload:
        return (0, 0, history_depth, fallback_ref)
    timestamp_text, _, commit_id = payload.partition("\x00")
    timestamp = int(timestamp_text or "0")
    return (1, timestamp, history_depth, commit_id or fallback_ref)


## @brief Compute freshness for a task file on the current branch.
#  @param project_root Absolute path to the project root.
#  @param task_file Absolute path to the task file.
#  @param task_file_relative Relative path to the task file.
#  @return Freshness tuple.
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


## @brief Compute freshness for a task file on a named ref.
#  @param project_root Absolute path to the project root.
#  @param ref_name Git ref to inspect.
#  @param task_file_relative Relative path to the task file.
#  @return Freshness tuple.
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


## @brief Build a sort key for merging delivery unit versions.
#  @param version Delivery unit version to rank.
#  @return Composite sort key tuple.
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


## @brief Pick the best non-placeholder value across delivery unit versions.
#  @param versions List of delivery unit versions.
#  @param field_name Attribute name to inspect.
#  @param placeholders Set of placeholder values to skip.
#  @return Best available value.
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


## @brief Merge multiple delivery unit versions into a single DeliveryUnit.
#  @param versions List of versions to merge.
#  @return Merged DeliveryUnit.
#  @exception ValueError If the versions list is empty.
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


## @brief Find branches related to a task's publish contour.
#  @param project_root Absolute path to the project root.
#  @param task_dir Absolute path to the task directory.
#  @param fields Parsed task fields.
#  @return Sorted list of related branch names.
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


## @brief Read task file contents from a git ref.
#  @param project_root Absolute path to the project root.
#  @param ref_name Git ref to read from.
#  @param task_file_relative Relative path to the task file.
#  @return File lines, or None if the ref does not contain the file.
def read_task_lines_from_ref(project_root: Path, ref_name: str, task_file_relative: str) -> list[str] | None:
    completed = run_git(project_root, "show", f"{ref_name}:{task_file_relative}", check=False)
    if completed.returncode != 0:
        return None
    return completed.stdout.splitlines()


## @brief Check if a path exists in the current HEAD.
#  @param project_root Absolute path to the project root.
#  @param relative_path Path relative to project root.
#  @return True if the path exists in HEAD.
def path_exists_in_head(project_root: Path, relative_path: str) -> bool:
    return read_task_lines_from_ref(project_root, "HEAD", relative_path) is not None


## @brief Collect and merge delivery units from current and related refs.
#  @param project_root Absolute path to the project root.
#  @param task_dir Absolute path to the task directory.
#  @param fields Parsed task fields.
#  @param current_lines Current task file lines.
#  @return Sorted list of merged DeliveryUnit objects.
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


## @brief Find a delivery unit by ID, raising on mismatch or ambiguity.
#  @param units List of delivery units.
#  @param unit_id Target unit ID, or None for single-unit auto-select.
#  @return Matching DeliveryUnit.
#  @exception ValueError If the unit is not found or selection is ambiguous.
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


## @brief Replace or append a delivery unit in a list.
#  @param units List of delivery units.
#  @param updated_unit Unit to insert or replace.
#  @return New list with the updated unit.
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


## @brief Read the goal summary from HEAD for a given task.
#  @param project_root Absolute path to the project root.
#  @param task_dir Absolute path to the task directory.
#  @return Goal summary string, or None.
def tracked_goal_summary(project_root: Path, task_dir: Path) -> str | None:
    task_file_relative = (task_dir / "task.md").relative_to(project_root).as_posix()
    tracked_lines = read_task_lines_from_ref(project_root, "HEAD", task_file_relative)
    if tracked_lines is None:
        return None
    return derive_goal_summary_from_lines(tracked_lines)


## @brief List commit hashes touching a path on a given ref.
#  @param project_root Absolute path to the project root.
#  @param relative_path Path relative to project root.
#  @param ref_name Git ref to inspect.
#  @return List of commit hashes.
def commit_history_for_path(project_root: Path, relative_path: str, *, ref_name: str = "HEAD") -> list[str]:
    return run_git(project_root, "log", ref_name, "--format=%H", "--", relative_path).stdout.splitlines()


## @brief Find the commit that introduced a specific goal summary.
#  @param project_root Absolute path to the project root.
#  @param task_dir Absolute path to the task directory.
#  @param goal_summary Goal summary text to match.
#  @param ref_name Git ref to search.
#  @return Commit hash, or None if not found.
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


## @brief Extract a task's summary from registry markdown lines.
#  @param lines Registry document lines.
#  @param task_id Task ID to search for.
#  @return Tuple of (summary string, row_found flag).
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


## @brief Find the commit that introduced a specific registry summary.
#  @param project_root Absolute path to the project root.
#  @param task_id Task ID to search for.
#  @param summary Summary text to match.
#  @param ref_name Git ref to search.
#  @return Commit hash, or None if not found.
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


## @brief Check if one commit is an ancestor of another.
#  @param project_root Absolute path to the project root.
#  @param ancestor Potential ancestor commit.
#  @param descendant Potential descendant commit.
#  @return True if ancestor precedes descendant.
def commit_is_ancestor(project_root: Path, ancestor: str, descendant: str) -> bool:
    completed = run_git(project_root, "merge-base", "--is-ancestor", ancestor, descendant, check=False)
    return completed.returncode == 0


## @brief Sanitize a legacy registry summary value.
#  @param value Raw summary value.
#  @return Sanitized string, or None if empty or placeholder.
def legacy_registry_summary_candidate(value: str | None) -> str | None:
    sanitized = sanitize_registry_summary(value or "")
    if not sanitized or sanitized == DELIVERY_ROW_PLACEHOLDER:
        return None
    return sanitized


## @brief Determine if a goal summary should override the registry summary.
#  @param project_root Absolute path to the project root.
#  @param task_dir Absolute path to the task directory.
#  @param task_id Task ID.
#  @param goal_summary Current goal summary.
#  @param existing_summary Existing registry summary.
#  @param ref_name Git ref to inspect, or None for HEAD.
#  @return True if the goal summary should take precedence.
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


## @brief Resolve the preferred registry summary from multiple sources.
#  @param fields Parsed task fields.
#  @param goal_summary Goal-derived summary.
#  @param summary Explicitly passed summary.
#  @param existing_summary Existing registry summary.
#  @param prefer_goal_over_existing Whether to prefer goal over existing.
#  @param ignore_task_summary Whether to ignore the task summary field.
#  @return Best available summary string, or None.
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


## @brief Read registry markdown lines from disk or a git ref.
#  @param project_root Absolute path to the project root.
#  @param ref_name Git ref to read from, or None for working tree.
#  @param allow_untracked_fallback Allow falling back to working tree if ref lacks the file.
#  @return Registry document lines.
#  @exception ValueError If the registry file is not found.
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


## @brief Read the existing registry summary for a task ID.
#  @param project_root Absolute path to the project root.
#  @param task_id Task ID to look up.
#  @param ref_name Git ref to read from, or None for working tree.
#  @param allow_untracked_fallback Allow falling back to working tree.
#  @return Tuple of (summary string, row_found flag).
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


## @brief Read task file contents and fields from disk or a git ref.
#  @param project_root Absolute path to the project root.
#  @param task_dir Absolute path to the task directory.
#  @param ref_name Git ref to read from, or None for working tree.
#  @param allow_untracked_fallback Allow falling back to working tree.
#  @return Tuple of (lines, fields, goal_summary).
#  @exception ValueError If the task file is not found.
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


## @brief Inherit the branch name from a parent task.
#  @param task_dir Absolute path to the subtask directory.
#  @param project_root Absolute path to the project root, or None.
#  @return Inherited branch name.
#  @exception ValueError If the task is not a subtask or parent branch is unset.
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


## @brief Compute the registry summary during preflight.
#  @param project_root Absolute path to the project root.
#  @param task_dir Absolute path to the task directory.
#  @param register_if_missing Whether to allow creating a new registry row.
#  @param summary Explicitly passed summary.
#  @param ref_name Git ref to read from, or None for working tree.
#  @param allow_untracked_fallback Allow falling back to working tree.
#  @return Resolved summary string.
#  @exception ValueError If no summary can be resolved.
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


## @brief Determine the target ref for a sync preflight.
#  @param project_root Absolute path to the project root.
#  @param create_branch Whether a new branch should be created.
#  @param target_branch Name of the target branch.
#  @return Target ref name, or None if no preflight is needed.
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


## @brief Determine the target ref for a publish preflight.
#  @param project_root Absolute path to the project root.
#  @param action Publish action name.
#  @param target_branch Explicit target branch, or None.
#  @param start_ref Starting ref, or None.
#  @param current_unit Current delivery unit, or None.
#  @return Target ref name, or None if no preflight is needed.
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


## @brief Determine the ref to use for the publication body.
#  @param project_root Absolute path to the project root.
#  @param current_unit Current delivery unit.
#  @return Branch name to use, or None for the current branch.
def publication_body_ref_name(project_root: Path, current_unit: DeliveryUnit) -> str | None:
    if current_git_branch(project_root) == current_unit.head:
        return None
    if current_unit.head != DELIVERY_ROW_PLACEHOLDER and branch_exists(project_root, current_unit.head):
        return current_unit.head
    return None


## @brief Format a single registry table row.
#  @param task_id Task ID.
#  @param parent_id Parent task ID.
#  @param status Task status.
#  @param priority Task priority.
#  @param branch_name Branch name.
#  @param task_dir_relative Relative task directory path.
#  @param summary Human-readable summary.
#  @return Formatted Markdown table row.
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


## @brief Update or append a task row in the registry.
#  @param project_root Absolute path to the project root.
#  @param task_dir Absolute path to the task directory.
#  @param fields Parsed task fields.
#  @param branch_name Branch name to record.
#  @param register_if_missing Whether to append a new row if missing.
#  @param summary Explicitly passed summary.
#  @return Tuple of (was_new_row, registry_path).
#  @exception ValueError If registry is missing or summary cannot be resolved.
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


## @brief Verify that all dirty paths are within the task scope or registry.
#  @param project_root Absolute path to the project root.
#  @param task_dir Absolute path to the task directory.
#  @return True if all dirty paths are task-scoped.
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
