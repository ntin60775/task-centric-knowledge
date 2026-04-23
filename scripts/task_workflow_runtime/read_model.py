"""Read-only task projections for operator reporting."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
import re

from .git_ops import current_git_branch, dirty_paths
from .models import (
    DELIVERY_ROW_PLACEHOLDER,
    FINAL_TASK_STATUSES,
    PLACEHOLDER_BRANCH_VALUES,
    VALID_CLEANUP_VALUES,
    VALID_HOSTS,
    VALID_PUBLICATION_TYPES,
    VALID_TASK_STATUSES,
    DeliveryUnit,
    default_branch_name,
    normalize_delivery_status,
    normalize_table_value,
    sanitize_registry_summary,
)
from .task_markdown import (
    derive_goal_summary_from_lines,
    find_section_bounds,
    parse_delivery_units_safe,
    reference_mode_warning,
    read_task_fields,
    split_markdown_row,
    task_summary_from_fields,
)


BEGIN_MARKER = "⟦⟦BEGIN_TASK_KNOWLEDGE_SYSTEM#KB01⟧⟧"
END_MARKER = "⟦⟦END_TASK_KNOWLEDGE_SYSTEM#KB01⟧⟧"
TASKS_ROOT = Path("knowledge/tasks")
REGISTRY_RELATIVE = TASKS_ROOT / "registry.md"
OPEN_DELIVERY_STATUSES = {"local", "draft", "review"}
CLOSED_DELIVERY_STATUSES = {"merged", "closed"}
UNCHECKED_STEP_RE = re.compile(r"^\s*-\s*\[\s\]\s*(?P<step>.+?)\s*$")
REGISTRY_ROW_RE = re.compile(
    r"^\|\s*`(?P<task_id>[^`]+)`\s*\|\s*`(?P<parent_id>[^`]+)`\s*\|\s*`(?P<status>[^`]+)`\s*\|\s*"
    r"`(?P<priority>[^`]+)`\s*\|\s*`(?P<branch>[^`]+)`\s*\|\s*`(?P<directory>[^`]+)`\s*\|\s*"
    r"(?P<summary>.*?)\s*\|$"
)
UPGRADE_STATE_RELATIVE = Path("knowledge/operations/task-centric-knowledge-upgrade.md")


@dataclass
class WarningItem:
    code: str
    severity: str
    detail: str
    path: str | None = None


@dataclass
class TaskSummary:
    task_id: str
    short_name: str
    human_description: str
    path: str


@dataclass
class TaskPreview:
    summary: TaskSummary
    status: str
    priority: str
    branch: str
    current_stage: str | None = None


@dataclass
class TaskSnapshot:
    summary: TaskSummary
    parent_id: str
    status: str
    priority: str
    branch: str
    goal: str | None
    current_stage: str | None
    next_step: str | None
    blockers: list[str]
    manual_remainder: list[str]
    files: dict[str, str]
    subtasks: list[TaskPreview]
    delivery_units: list[DeliveryUnit]
    verify_automated: list[str]
    verify_manual: list[str]
    warnings: list[WarningItem]
    registry_summary: str | None = None
    registry_branch: str | None = None

    def preview(self) -> TaskPreview:
        return TaskPreview(
            summary=self.summary,
            status=self.status,
            priority=self.priority,
            branch=self.branch,
            current_stage=self.current_stage,
        )


@dataclass
class CurrentTaskResolution:
    state: str
    reason: str
    task: TaskSnapshot | None
    candidates: list[TaskPreview] = field(default_factory=list)
    warnings: list[WarningItem] = field(default_factory=list)


@dataclass
class StatusSnapshot:
    project_root: str
    active_branch: str
    knowledge_health: dict[str, object]
    upgrade_governance: dict[str, object]
    current_task: CurrentTaskResolution
    task_counters: dict[str, int]
    high_priority_open: list[TaskPreview]
    review_tasks: list[TaskPreview]
    open_delivery_units: list[dict[str, str]]
    warnings: list[WarningItem]


def warning_to_dict(item: WarningItem) -> dict[str, str | None]:
    return asdict(item)


def task_preview_to_dict(item: TaskPreview) -> dict[str, object]:
    return asdict(item)


def task_snapshot_to_dict(item: TaskSnapshot) -> dict[str, object]:
    return {
        "summary": asdict(item.summary),
        "parent_id": item.parent_id,
        "status": item.status,
        "priority": item.priority,
        "branch": item.branch,
        "goal": item.goal,
        "current_stage": item.current_stage,
        "next_step": item.next_step,
        "blockers": item.blockers,
        "manual_remainder": item.manual_remainder,
        "files": item.files,
        "subtasks": [task_preview_to_dict(subtask) for subtask in item.subtasks],
        "delivery_units": [asdict(unit) for unit in item.delivery_units],
        "verify": {
            "automated": item.verify_automated,
            "manual": item.verify_manual,
        },
        "warnings": [warning_to_dict(warning) for warning in item.warnings],
        "registry_summary": item.registry_summary,
        "registry_branch": item.registry_branch,
    }


def current_task_resolution_to_dict(item: CurrentTaskResolution) -> dict[str, object]:
    return {
        "state": item.state,
        "reason": item.reason,
        "task": task_snapshot_to_dict(item.task) if item.task else None,
        "candidates": [task_preview_to_dict(candidate) for candidate in item.candidates],
        "warnings": [warning_to_dict(warning) for warning in item.warnings],
    }


def status_snapshot_to_dict(item: StatusSnapshot) -> dict[str, object]:
    return {
        "project_root": item.project_root,
        "active_branch": item.active_branch,
        "knowledge_health": item.knowledge_health,
        "upgrade_governance": item.upgrade_governance,
        "current_task": current_task_resolution_to_dict(item.current_task),
        "task_counters": item.task_counters,
        "high_priority_open": [task_preview_to_dict(candidate) for candidate in item.high_priority_open],
        "review_tasks": [task_preview_to_dict(candidate) for candidate in item.review_tasks],
        "open_delivery_units": item.open_delivery_units,
        "warnings": [warning_to_dict(warning) for warning in item.warnings],
    }


def relative_path(project_root: Path, path: Path) -> str:
    return path.relative_to(project_root).as_posix()


def detect_managed_block_state(project_root: Path) -> str:
    agents_path = project_root / "AGENTS.md"
    if not agents_path.exists():
        return "absent"
    text = agents_path.read_text(encoding="utf-8")
    begin_count = text.count(BEGIN_MARKER)
    end_count = text.count(END_MARKER)
    if begin_count == 0 and end_count == 0:
        return "absent"
    if begin_count == 1 and end_count == 1 and text.index(BEGIN_MARKER) < text.index(END_MARKER):
        return "managed"
    return "invalid"


def _table_rows(lines: list[str], title: str, headers: tuple[str, ...]) -> list[tuple[str, ...]]:
    in_section = False
    header_seen = False
    rows: list[tuple[str, ...]] = []
    for line in lines:
        stripped = line.strip()
        if stripped == title:
            in_section = True
            header_seen = False
            continue
        if in_section and stripped.startswith("## "):
            break
        if not in_section:
            continue
        cells = split_markdown_row(line)
        if not cells:
            continue
        normalized = tuple(cell.strip().strip("`") for cell in cells)
        if normalized == headers:
            header_seen = True
            continue
        if not header_seen:
            continue
        if all(set(cell) <= {"-"} for cell in normalized):
            continue
        if len(normalized) != len(headers):
            continue
        rows.append(normalized)
    return rows


def upgrade_state_summary(project_root: Path) -> dict[str, object]:
    state_path = project_root / UPGRADE_STATE_RELATIVE
    if not state_path.exists():
        from install_skill_runtime.environment import detect_existing_system

        classification = detect_existing_system(project_root).classification
        compatibility_epoch = "legacy-v1" if classification == "compatible" else "module-core-v1"
        upgrade_status = "legacy-compatible" if compatibility_epoch == "legacy-v1" else "fully-upgraded"
        execution_rollout = "legacy" if compatibility_epoch == "legacy-v1" else "single-writer"
        return {
            "state_path": str(state_path),
            "state_exists": False,
            "compatibility_epoch": compatibility_epoch,
            "upgrade_status": upgrade_status,
            "execution_rollout": execution_rollout,
            "legacy_pending_count": 0,
            "reference_manual_count": 0,
        }

    lines = state_path.read_text(encoding="utf-8").splitlines()
    passport = {
        field: value
        for field, value in _table_rows(lines, "## Паспорт", ("Поле", "Значение"))
    }
    pending_count = 0
    reference_count = 0
    legacy_rows = _table_rows(
        lines,
        "## Исторические задачи",
        ("TASK-ID", "Класс", "Статус совместимости", "Путь к заметке миграции", "Решение"),
    )
    if not legacy_rows:
        legacy_rows = _table_rows(
            lines,
            "## Legacy tasks",
            ("TASK-ID", "Класс", "Статус backfill", "Migration note", "Решение"),
        )
    for _, _, backfill_status, _, _ in legacy_rows:
        if backfill_status == "pending":
            pending_count += 1
        elif backfill_status == "manual-reference":
            reference_count += 1
    return {
        "state_path": str(state_path),
        "state_exists": True,
        "compatibility_epoch": passport.get("Эпоха совместимости", "module-core-v1"),
        "upgrade_status": passport.get("Статус перехода", passport.get("Статус upgrade", "fully-upgraded")),
        "execution_rollout": passport.get("Контур исполнения", passport.get("Execution rollout", "single-writer")),
        "legacy_pending_count": pending_count,
        "reference_manual_count": reference_count,
    }


def parse_registry_rows(registry_path: Path) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    if not registry_path.exists():
        return rows
    for line in registry_path.read_text(encoding="utf-8").splitlines():
        match = REGISTRY_ROW_RE.match(line.strip())
        if not match:
            continue
        payload = {
            "task_id": match.group("task_id").strip(),
            "parent_id": match.group("parent_id").strip(),
            "status": match.group("status").strip(),
            "priority": match.group("priority").strip(),
            "branch": match.group("branch").strip(),
            "directory": match.group("directory").strip(),
            "summary": sanitize_registry_summary(match.group("summary")),
        }
        rows[payload["task_id"]] = payload
    return rows


def section_lines(lines: list[str], title: str) -> list[str]:
    bounds = find_section_bounds(lines, title)
    if bounds is None:
        return []
    start_index, end_index = bounds
    return lines[start_index + 1 : end_index]


def subsection_lines(lines: list[str], parent_title: str, title: str) -> list[str]:
    bounds = find_section_bounds(lines, parent_title)
    if bounds is None:
        return []
    start_index, end_index = bounds
    for index in range(start_index + 1, end_index):
        if lines[index].strip() != title:
            continue
        subsection_end = end_index
        for candidate in range(index + 1, end_index):
            if lines[candidate].startswith("### "):
                subsection_end = candidate
                break
        return lines[index + 1 : subsection_end]
    return []


def first_paragraph(lines: list[str]) -> str | None:
    paragraph: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if paragraph:
                break
            continue
        if stripped.startswith("```"):
            continue
        if stripped.startswith("- "):
            return stripped[2:].strip()
        paragraph.append(stripped)
    if not paragraph:
        return None
    return " ".join(paragraph).strip()


def block_text(lines: list[str]) -> str | None:
    content = "\n".join(line.rstrip() for line in lines).strip()
    return content or None


def block_list(lines: list[str]) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current:
                items.append(" ".join(current).strip())
                current = []
            continue
        if stripped.startswith("- "):
            if current:
                items.append(" ".join(current).strip())
            current = [stripped[2:].strip()]
            continue
        if current:
            current.append(stripped)
    if current:
        items.append(" ".join(current).strip())
    if items:
        return items
    text = first_paragraph(lines)
    return [text] if text else []


def task_file_directories(project_root: Path) -> list[Path]:
    tasks_root = project_root / TASKS_ROOT
    if not tasks_root.exists():
        return []
    result: list[Path] = []
    for task_file in tasks_root.rglob("task.md"):
        relative = task_file.relative_to(tasks_root)
        if "_templates" in relative.parts:
            continue
        result.append(task_file.parent)
    return sorted(result)


def next_step_from_plan(plan_file: Path) -> str | None:
    if not plan_file.exists():
        return None
    lines = plan_file.read_text(encoding="utf-8").splitlines()
    for line in section_lines(lines, "## Шаги"):
        match = UNCHECKED_STEP_RE.match(line)
        if match:
            return match.group("step").strip()
    return None


def task_files_map(project_root: Path, task_dir: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for relative in ("task.md", "plan.md", "sdd.md", "artifacts/verification-matrix.md"):
        path = task_dir / relative
        if path.exists():
            files[relative] = relative_path(project_root, path)
    return files


def task_requires_sdd(fields: dict[str, str]) -> bool:
    return normalize_table_value(fields.get("Требуется SDD", "")) == "да"


def legacy_upgrade_entries(project_root: Path) -> dict[str, dict[str, str]]:
    state_path = project_root / UPGRADE_STATE_RELATIVE
    if not state_path.exists():
        return {}
    lines = state_path.read_text(encoding="utf-8").splitlines()
    legacy_rows = _table_rows(
        lines,
        "## Исторические задачи",
        ("TASK-ID", "Класс", "Статус совместимости", "Путь к заметке миграции", "Решение"),
    )
    if not legacy_rows:
        legacy_rows = _table_rows(
            lines,
            "## Legacy tasks",
            ("TASK-ID", "Класс", "Статус backfill", "Migration note", "Решение"),
        )
    entries: dict[str, dict[str, str]] = {}
    for task_id, task_class, backfill_status, migration_note, decision in legacy_rows:
        entries[task_id] = {
            "task_class": task_class,
            "backfill_status": backfill_status,
            "migration_note": migration_note,
            "decision": decision,
        }
    return entries


def note_only_legacy_backfill(task_dir: Path, entry: dict[str, str] | None) -> bool:
    if entry is None:
        return False
    if entry.get("task_class") != "closed historical" or entry.get("backfill_status") != "note-only":
        return False
    return (task_dir / "artifacts/migration/task-centric-knowledge-upgrade.md").exists()


def validate_delivery_units(task: TaskSnapshot, *, project_root: Path, has_parse_errors: bool = False) -> None:
    for unit in task.delivery_units:
        try:
            normalize_delivery_status(unit.status)
        except ValueError:
            task.warnings.append(
                WarningItem(
                    code="noncanonical_delivery_status",
                    severity="warning",
                    detail=f"Delivery unit {unit.unit_id} использует неканонический статус `{unit.status}`.",
                    path=task.summary.path,
                )
            )
        if unit.host not in VALID_HOSTS:
            task.warnings.append(
                WarningItem(
                    code="noncanonical_delivery_host",
                    severity="warning",
                    detail=f"Delivery unit {unit.unit_id} использует неканонический host `{unit.host}`.",
                    path=task.summary.path,
                )
            )
        if unit.publication_type not in VALID_PUBLICATION_TYPES:
            task.warnings.append(
                WarningItem(
                    code="noncanonical_publication_type",
                    severity="warning",
                    detail=(
                        f"Delivery unit {unit.unit_id} использует "
                        f"неканонический тип публикации `{unit.publication_type}`."
                    ),
                    path=task.summary.path,
                )
            )
        if unit.cleanup not in VALID_CLEANUP_VALUES:
            task.warnings.append(
                WarningItem(
                    code="noncanonical_cleanup_value",
                    severity="warning",
                    detail=f"Delivery unit {unit.unit_id} использует неканонический Cleanup `{unit.cleanup}`.",
                    path=task.summary.path,
                )
            )
    if task.status in FINAL_TASK_STATUSES and (
        has_parse_errors or any(unit.status not in CLOSED_DELIVERY_STATUSES for unit in task.delivery_units)
    ):
        task.warnings.append(
            WarningItem(
                code="final_task_with_open_delivery_units",
                severity="warning",
                detail="Финальный статус задачи конфликтует с незакрытыми или некорректными delivery units.",
                path=task.summary.path,
            )
        )


def build_task_snapshot(
    project_root: Path,
    task_dir: Path,
    registry_rows: dict[str, dict[str, str]],
    upgrade_entries: dict[str, dict[str, str]],
) -> TaskSnapshot:
    task_file = task_dir / "task.md"
    lines, fields = read_task_fields(task_file)
    warnings: list[WarningItem] = []
    summary = task_summary_from_fields(fields)
    if not summary:
        summary = derive_goal_summary_from_lines(lines)
        if summary:
            warnings.append(
                WarningItem(
                    code="summary_fallback_goal",
                    severity="warning",
                    detail="Вместо `Человекочитаемого описания` использован fallback из раздела `Цель`.",
                    path=relative_path(project_root, task_file),
                )
            )
    if not summary:
        summary = DELIVERY_ROW_PLACEHOLDER
        warnings.append(
            WarningItem(
                code="summary_missing",
                severity="warning",
                detail="Не удалось восстановить каноническую summary задачи.",
                path=relative_path(project_root, task_file),
            )
        )
    task_id = fields.get("ID задачи", "").strip()
    short_name = fields.get("Краткое имя", "").strip()
    status = fields.get("Статус", "").strip()
    priority = fields.get("Приоритет", "").strip()
    branch = fields.get("Ветка", "").strip()
    delivery_units, delivery_parse_errors = parse_delivery_units_safe(lines)
    snapshot = TaskSnapshot(
        summary=TaskSummary(
            task_id=task_id,
            short_name=short_name,
            human_description=summary,
            path=relative_path(project_root, task_dir),
        ),
        parent_id=fields.get("Parent ID", "—").strip() or "—",
        status=status,
        priority=priority,
        branch=branch,
        goal=block_text(section_lines(lines, "## Цель")),
        current_stage=first_paragraph(section_lines(lines, "## Текущий этап")),
        next_step=next_step_from_plan(task_dir / "plan.md"),
        blockers=[],
        manual_remainder=block_list(subsection_lines(lines, "## Стратегия проверки", "### Остаётся на ручную проверку")),
        files=task_files_map(project_root, task_dir),
        subtasks=[],
        delivery_units=delivery_units,
        verify_automated=block_list(subsection_lines(lines, "## Стратегия проверки", "### Покрывается кодом или тестами")),
        verify_manual=block_list(subsection_lines(lines, "## Стратегия проверки", "### Остаётся на ручную проверку")),
        warnings=warnings,
    )
    legacy_entry = upgrade_entries.get(task_id)
    if task_requires_sdd(fields):
        if "sdd.md" not in snapshot.files:
            snapshot.warnings.append(
                WarningItem(
                    code="sdd_file_missing",
                    severity="warning",
                    detail="В task passport указано `Требуется SDD = да`, но файл `sdd.md` отсутствует.",
                    path=relative_path(project_root, task_dir / "sdd.md"),
                )
            )
        if (
            "artifacts/verification-matrix.md" not in snapshot.files
            and not note_only_legacy_backfill(task_dir, legacy_entry)
        ):
            snapshot.warnings.append(
                WarningItem(
                    code="verification_matrix_missing",
                    severity="warning",
                    detail=(
                        "Для задачи с обязательным `SDD` отсутствует "
                        "`artifacts/verification-matrix.md`."
                    ),
                    path=relative_path(project_root, task_dir / "artifacts/verification-matrix.md"),
                )
            )
    for error_detail in delivery_parse_errors:
        snapshot.warnings.append(
            WarningItem(
                code="delivery_unit_parse_error",
                severity="warning",
                detail=f"Некорректная строка delivery unit: {error_detail}",
                path=snapshot.summary.path,
            )
        )
    if status not in VALID_TASK_STATUSES:
        snapshot.warnings.append(
            WarningItem(
                code="noncanonical_task_status",
                severity="warning",
                detail=f"Задача использует неканонический статус `{status}`.",
                path=snapshot.summary.path,
            )
        )
    invalid_reference_mode = reference_mode_warning(fields)
    if invalid_reference_mode is not None:
        snapshot.warnings.append(
            WarningItem(
                code="reference_mode_invalid",
                severity="warning",
                detail=f"Поле `Справочный режим` использует неканоническое значение `{invalid_reference_mode}`.",
                path=snapshot.summary.path,
            )
        )
    if status in {"заблокирована", "ждёт пользователя"} and snapshot.current_stage:
        snapshot.blockers.append(snapshot.current_stage)
    registry_row = registry_rows.get(task_id)
    if registry_row is None:
        snapshot.warnings.append(
            WarningItem(
                code="registry_row_missing",
                severity="warning",
                detail=f"Для {task_id} отсутствует строка в `knowledge/tasks/registry.md`.",
                path=snapshot.summary.path,
            )
        )
    else:
        snapshot.registry_summary = registry_row["summary"]
        snapshot.registry_branch = registry_row["branch"]
        if sanitize_registry_summary(snapshot.summary.human_description) != registry_row["summary"]:
            snapshot.warnings.append(
                WarningItem(
                    code="summary_drift",
                    severity="warning",
                    detail="Summary в `registry.md` расходится с каноническим `task.md`.",
                    path=snapshot.summary.path,
                )
            )
        if normalize_table_value(registry_row["branch"]) != normalize_table_value(branch):
            snapshot.warnings.append(
                WarningItem(
                    code="branch_drift",
                    severity="warning",
                    detail="Поле `Ветка` в `task.md` расходится с кэшем `registry.md`.",
                    path=snapshot.summary.path,
                )
            )
    if not snapshot.next_step and status not in FINAL_TASK_STATUSES:
        snapshot.warnings.append(
            WarningItem(
                code="next_step_missing",
                severity="warning",
                detail="В `plan.md` не найден следующий незавершённый шаг.",
                path=snapshot.summary.path,
            )
        )
    validate_delivery_units(snapshot, project_root=project_root, has_parse_errors=bool(delivery_parse_errors))
    return snapshot


def path_belongs_to_task(path: str, task_relative: str) -> bool:
    normalized_task = task_relative.rstrip("/")
    if path == normalized_task:
        return True
    if path.startswith(normalized_task + "/"):
        return True
    return normalized_task.startswith(path + "/")


def dirty_task_candidates(project_root: Path, snapshots: list[TaskSnapshot]) -> list[TaskSnapshot]:
    dirty = dirty_paths(project_root)
    owned_tasks: list[TaskSnapshot] = []
    for path in dirty:
        normalized = path.replace("\\", "/").rstrip("/")
        if not normalized:
            continue
        if normalized == REGISTRY_RELATIVE.as_posix():
            continue
        matches = [
            snapshot
            for snapshot in snapshots
            if path_belongs_to_task(normalized, snapshot.summary.path)
        ]
        if not matches:
            continue
        owner = max(matches, key=lambda snapshot: len(snapshot.summary.path))
        if owner not in owned_tasks:
            owned_tasks.append(owner)
    return owned_tasks


def branch_match_score(snapshot: TaskSnapshot, active_branch: str) -> int:
    for unit in snapshot.delivery_units:
        if unit.head == active_branch:
            return 3
    if snapshot.branch not in PLACEHOLDER_BRANCH_VALUES and snapshot.branch == active_branch:
        return 2
    if snapshot.summary.task_id and snapshot.summary.short_name:
        default_branch = default_branch_name(snapshot.summary.task_id, snapshot.summary.short_name)
        if default_branch == active_branch:
            return 1
    return 0


def is_task_descendant(candidate: TaskSnapshot, parent: TaskSnapshot) -> bool:
    parent_path = parent.summary.path.rstrip("/")
    candidate_path = candidate.summary.path.rstrip("/")
    return candidate_path.startswith(parent_path + "/subtasks/")


def inherited_branch_parent_candidate(candidates: list[TaskSnapshot]) -> TaskSnapshot | None:
    possible_parents = [
        candidate
        for candidate in candidates
        if all(item == candidate or is_task_descendant(item, candidate) for item in candidates)
    ]
    if len(possible_parents) != 1:
        return None
    return possible_parents[0]


def prefer_non_final_candidates(candidates: list[TaskSnapshot]) -> list[TaskSnapshot]:
    active_candidates = [candidate for candidate in candidates if candidate.status not in FINAL_TASK_STATUSES]
    return active_candidates or candidates


def dedupe_warnings(items: list[WarningItem]) -> list[WarningItem]:
    seen: set[tuple[str, str, str | None]] = set()
    result: list[WarningItem] = []
    for item in items:
        key = (item.code, item.detail, item.path)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def discover_tasks(project_root: Path) -> dict[str, TaskSnapshot]:
    registry_rows = parse_registry_rows(project_root / REGISTRY_RELATIVE)
    upgrade_entries = legacy_upgrade_entries(project_root)
    snapshots: dict[str, TaskSnapshot] = {}
    for task_dir in task_file_directories(project_root):
        snapshot = build_task_snapshot(project_root, task_dir, registry_rows, upgrade_entries)
        snapshots[snapshot.summary.path] = snapshot
    for snapshot in snapshots.values():
        task_dir = project_root / snapshot.summary.path
        subtasks_dir = task_dir / "subtasks"
        if not subtasks_dir.exists():
            continue
        children: list[TaskPreview] = []
        for child_task_file in sorted(subtasks_dir.glob("*/task.md")):
            child_dir = child_task_file.parent
            child_relative = relative_path(project_root, child_dir)
            child = next(
                (candidate for candidate in snapshots.values() if candidate.summary.path == child_relative),
                None,
            )
            if child is not None:
                children.append(child.preview())
        snapshot.subtasks = children
    snapshots_by_id: dict[str, list[TaskSnapshot]] = {}
    for snapshot in snapshots.values():
        snapshots_by_id.setdefault(snapshot.summary.task_id, []).append(snapshot)
    for task_id, items in snapshots_by_id.items():
        if not task_id or len(items) < 2:
            continue
        duplicate_paths = ", ".join(sorted(item.summary.path for item in items))
        for item in items:
            item.warnings.append(
                WarningItem(
                    code="duplicate_task_id",
                    severity="warning",
                    detail=f"ID задачи `{task_id}` встречается в нескольких карточках: {duplicate_paths}.",
                    path=item.summary.path,
                )
            )
    return snapshots


def knowledge_health(project_root: Path, tasks: dict[str, TaskSnapshot]) -> tuple[dict[str, object], list[WarningItem]]:
    warnings: list[WarningItem] = []
    knowledge_path = project_root / "knowledge"
    registry_path = project_root / REGISTRY_RELATIVE
    managed_state = detect_managed_block_state(project_root)
    health = {
        "knowledge_exists": knowledge_path.exists(),
        "registry_exists": registry_path.exists(),
        "managed_block_state": managed_state,
        "task_count": len(tasks),
    }
    if not knowledge_path.exists():
        warnings.append(
            WarningItem(
                code="knowledge_missing",
                severity="warning",
                detail="В проекте отсутствует каталог `knowledge/`.",
                path=str(knowledge_path),
            )
        )
    if not registry_path.exists():
        warnings.append(
            WarningItem(
                code="registry_missing",
                severity="warning",
                detail="В проекте отсутствует `knowledge/tasks/registry.md`.",
                path=str(registry_path),
            )
        )
    if managed_state == "invalid":
        warnings.append(
            WarningItem(
                code="managed_block_invalid",
                severity="warning",
                detail="Managed-блок knowledge-системы в `AGENTS.md` неконсистентен.",
                path=str(project_root / "AGENTS.md"),
            )
        )
    return health, warnings


def resolve_current_task(project_root: Path, tasks: dict[str, TaskSnapshot]) -> CurrentTaskResolution:
    active_branch = current_git_branch(project_root)
    if not tasks:
        warning = WarningItem(
            code="current_task_unresolved",
            severity="warning",
            detail="Активная задача не определена: task-контур пуст.",
        )
        return CurrentTaskResolution("unresolved", "no_tasks", None, warnings=[warning])

    scored = [(branch_match_score(snapshot, active_branch), snapshot) for snapshot in tasks.values()]
    best_score = max(score for score, _ in scored)
    if best_score > 0:
        branch_candidates = prefer_non_final_candidates(
            [snapshot for score, snapshot in scored if score == best_score]
        )
        if len(branch_candidates) == 1:
            task = branch_candidates[0]
            return CurrentTaskResolution(
                "resolved",
                "branch",
                task,
                warnings=dedupe_warnings(task.warnings),
            )
        dirty_candidates = [
            candidate
            for candidate in dirty_task_candidates(project_root, branch_candidates)
            if candidate in branch_candidates
        ]
        if len(dirty_candidates) == 1:
            task = dirty_candidates[0]
            return CurrentTaskResolution(
                "resolved",
                "branch+dirty",
                task,
                warnings=dedupe_warnings(task.warnings),
            )
        if len(dirty_candidates) > 1:
            warning = WarningItem(
                code="current_task_ambiguous",
                severity="warning",
                detail=f"Активная задача неоднозначна для ветки `{active_branch}`: несколько task scope содержат изменения.",
            )
            return CurrentTaskResolution(
                "ambiguous",
                "branch_tie",
                None,
                candidates=[candidate.preview() for candidate in dirty_candidates],
                warnings=dedupe_warnings([warning, *[item for candidate in dirty_candidates for item in candidate.warnings]]),
            )
        inherited_parent = inherited_branch_parent_candidate(branch_candidates)
        if inherited_parent is not None:
            return CurrentTaskResolution(
                "resolved",
                "branch_parent",
                inherited_parent,
                warnings=dedupe_warnings(inherited_parent.warnings),
            )
        warning = WarningItem(
            code="current_task_ambiguous",
            severity="warning",
            detail=f"Активная задача неоднозначна для ветки `{active_branch}`.",
        )
        return CurrentTaskResolution(
            "ambiguous",
            "branch_tie",
            None,
            candidates=[candidate.preview() for candidate in branch_candidates],
            warnings=dedupe_warnings([warning, *[item for candidate in branch_candidates for item in candidate.warnings]]),
        )

    dirty_candidates = dirty_task_candidates(project_root, list(tasks.values()))
    if len(dirty_candidates) == 1:
        task = dirty_candidates[0]
        return CurrentTaskResolution(
            "resolved",
            "dirty",
            task,
            warnings=dedupe_warnings(task.warnings),
        )
    if len(dirty_candidates) > 1:
        warning = WarningItem(
            code="current_task_ambiguous",
            severity="warning",
            detail="Активная задача неоднозначна: несколько задач совпали по task-scoped diff.",
        )
        return CurrentTaskResolution(
            "ambiguous",
            "dirty_tie",
            None,
            candidates=[candidate.preview() for candidate in dirty_candidates],
            warnings=dedupe_warnings([warning, *[item for candidate in dirty_candidates for item in candidate.warnings]]),
        )
    warning = WarningItem(
        code="current_task_unresolved",
        severity="warning",
        detail="Активная задача не определена: нет branch-match и нет единственного task-scoped diff.",
    )
    return CurrentTaskResolution("unresolved", "no_match", None, warnings=[warning])


def sorted_task_counters(tasks: dict[str, TaskSnapshot]) -> dict[str, int]:
    counter = Counter(snapshot.status for snapshot in tasks.values())
    ordered: dict[str, int] = {}
    for status in sorted(counter, key=lambda value: (value not in VALID_TASK_STATUSES, value)):
        ordered[status] = counter[status]
    return ordered


def open_delivery_units(tasks: dict[str, TaskSnapshot]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for snapshot in tasks.values():
        for unit in snapshot.delivery_units:
            if unit.status not in OPEN_DELIVERY_STATUSES:
                continue
            rows.append(
                {
                    "task_id": snapshot.summary.task_id,
                    "short_name": snapshot.summary.short_name,
                    "human_description": snapshot.summary.human_description,
                    "task_status": snapshot.status,
                    "unit_id": unit.unit_id,
                    "host": unit.host,
                    "status": unit.status,
                    "url": unit.url,
                }
            )
    return sorted(rows, key=lambda item: (item["task_id"], item["unit_id"]))


def build_status_snapshot(project_root: Path) -> StatusSnapshot:
    project_root = project_root.resolve()
    tasks = discover_tasks(project_root)
    health, health_warnings = knowledge_health(project_root, tasks)
    upgrade_governance = upgrade_state_summary(project_root)
    current_task = resolve_current_task(project_root, tasks)
    high_priority_open = [
        snapshot.preview()
        for snapshot in tasks.values()
        if snapshot.priority == "высокий" and snapshot.status not in FINAL_TASK_STATUSES
    ]
    review_tasks = [snapshot.preview() for snapshot in tasks.values() if snapshot.status == "на проверке"]
    warnings = dedupe_warnings(
        [
            *health_warnings,
            *(
                [
                    WarningItem(
                        code="legacy_backfill_pending",
                        severity="warning",
                        detail=(
                            "Repo upgrade-state ещё содержит pending legacy-задачи; "
                            "controlled compatibility-backfill не завершён."
                        ),
                        path=upgrade_governance["state_path"],
                    )
                ]
                if upgrade_governance["legacy_pending_count"] > 0
                else []
            ),
            *(
                [
                    WarningItem(
                        code="reference_backfill_manual",
                        severity="warning",
                        detail="Repo upgrade-state содержит reference-задачи, оставленные на manual-reference решении.",
                        path=upgrade_governance["state_path"],
                    )
                ]
                if upgrade_governance["reference_manual_count"] > 0
                else []
            ),
            *(
                [
                    WarningItem(
                        code="execution_rollout_partial",
                        severity="warning",
                        detail=(
                            "Контур исполнения ещё не доведён до single-writer; "
                            "репозиторий находится в dual-readiness состоянии."
                        ),
                        path=upgrade_governance["state_path"],
                    )
                ]
                if upgrade_governance["upgrade_status"] != "legacy-compatible"
                and upgrade_governance["execution_rollout"] != "single-writer"
                else []
            ),
            *[warning for snapshot in tasks.values() for warning in snapshot.warnings],
            *current_task.warnings,
        ]
    )
    return StatusSnapshot(
        project_root=str(project_root),
        active_branch=current_git_branch(project_root),
        knowledge_health=health,
        upgrade_governance=upgrade_governance,
        current_task=current_task,
        task_counters=sorted_task_counters(tasks),
        high_priority_open=sorted(high_priority_open, key=lambda item: item.summary.task_id),
        review_tasks=sorted(review_tasks, key=lambda item: item.summary.task_id),
        open_delivery_units=open_delivery_units(tasks),
        warnings=warnings,
    )


def current_task_snapshot(project_root: Path) -> CurrentTaskResolution:
    project_root = project_root.resolve()
    tasks = discover_tasks(project_root)
    return resolve_current_task(project_root, tasks)


def matching_task_snapshots(project_root: Path, task_id: str) -> list[TaskSnapshot]:
    project_root = project_root.resolve()
    tasks = discover_tasks(project_root)
    return sorted(
        [snapshot for snapshot in tasks.values() if snapshot.summary.task_id == task_id],
        key=lambda item: item.summary.path,
    )


def exact_task_snapshot(project_root: Path, task_id: str) -> TaskSnapshot | None:
    matches = matching_task_snapshots(project_root, task_id)
    if len(matches) == 1:
        return matches[0]
    return None
