"""Shared legacy upgrade/backfill state for task-centric knowledge."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .task_markdown import read_task_fields, split_markdown_row


UPGRADE_STATE_RELATIVE = Path("knowledge/operations/task-centric-knowledge-upgrade.md")
MIGRATION_NOTE_RELATIVE = Path("artifacts/migration/task-centric-knowledge-upgrade.md")
PASSPORT_SECTION = "## Паспорт"
LEGACY_TASKS_SECTION = "## Исторические задачи"
PASSPORT_FIELDS = (
    "Система",
    "Эпоха совместимости",
    "Статус перехода",
    "Контур исполнения",
    "Последняя задача перехода",
    "Дата обновления",
)
LEGACY_TASK_HEADERS = ("TASK-ID", "Класс", "Статус совместимости", "Путь к заметке миграции", "Решение")
LEGACY_TASKS_SECTION_ALIASES = (LEGACY_TASKS_SECTION, "## Legacy tasks")
LEGACY_TASK_HEADERS_ALIASES = (
    LEGACY_TASK_HEADERS,
    ("TASK-ID", "Класс", "Статус backfill", "Migration note", "Решение"),
)
VALID_EPOCHS = {"legacy-v1", "module-core-v1"}
VALID_UPGRADE_STATUSES = {"legacy-compatible", "partially-upgraded", "fully-upgraded"}
VALID_EXECUTION_ROLLOUTS = {"legacy", "dual-readiness", "single-writer"}
VALID_TASK_CLASSES = {"active", "closed historical", "reference"}
VALID_BACKFILL_STATUSES = {"pending", "note-only", "compatibility-backfilled", "manual-reference"}
REFERENCE_FIELD = "Справочный режим"
REFERENCE_ENABLED = "reference"


@dataclass(frozen=True)
class LegacyTaskEntry:
    task_id: str
    task_class: str
    backfill_status: str
    migration_note: str
    decision: str


@dataclass(frozen=True)
class RepoUpgradeState:
    path: Path
    system: str
    compatibility_epoch: str
    upgrade_status: str
    execution_rollout: str
    last_upgrade_task: str
    updated_at: str
    entries: tuple[LegacyTaskEntry, ...]


def repo_upgrade_state_path(project_root: Path) -> Path:
    return project_root / UPGRADE_STATE_RELATIVE


def task_migration_note_path(task_dir: Path) -> Path:
    return task_dir / MIGRATION_NOTE_RELATIVE


def relative_task_migration_note(project_root: Path, task_dir: Path) -> str:
    return task_migration_note_path(task_dir).relative_to(project_root).as_posix()


def today_iso() -> str:
    return date.today().isoformat()


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


def _table_rows_with_aliases(
    lines: list[str],
    titles: tuple[str, ...],
    headers_variants: tuple[tuple[str, ...], ...],
) -> list[tuple[str, ...]]:
    for title in titles:
        for headers in headers_variants:
            rows = _table_rows(lines, title, headers)
            if rows:
                return rows
    return []


def classify_task_fields(fields: dict[str, str]) -> str:
    reference_mode = fields.get(REFERENCE_FIELD, "нет").strip()
    if reference_mode == REFERENCE_ENABLED:
        return "reference"
    if fields.get("Статус", "").strip() in {"завершена", "отменена"}:
        return "closed historical"
    return "active"


def _default_backfill_status(task_class: str) -> str:
    if task_class == "reference":
        return "manual-reference"
    return "pending"


def _default_decision(task_class: str, status: str) -> str:
    if status == "manual-reference":
        return "Справочная задача исключена из автоматического `compatibility-backfill` и требует только ручного решения."
    if task_class == "closed historical":
        return "Требуется сценарий `note-only compatibility-backfill` без переписывания исторического описания задачи."
    return "Требуется сценарий `controlled compatibility-backfill` для рабочей задачи."


def _normalize_entry(task_id: str, task_class: str, existing: LegacyTaskEntry | None) -> LegacyTaskEntry:
    if existing is None:
        status = _default_backfill_status(task_class)
        return LegacyTaskEntry(
            task_id=task_id,
            task_class=task_class,
            backfill_status=status,
            migration_note="—",
            decision=_default_decision(task_class, status),
        )
    backfill_status = existing.backfill_status
    if task_class == "reference":
        backfill_status = "manual-reference"
    elif task_class == "active" and backfill_status not in {"pending", "compatibility-backfilled"}:
        backfill_status = "pending"
    elif task_class == "closed historical" and backfill_status not in {
        "pending",
        "note-only",
        "compatibility-backfilled",
    }:
        backfill_status = "pending"
    elif backfill_status not in VALID_BACKFILL_STATUSES or backfill_status == "manual-reference":
        backfill_status = "pending"
    decision = existing.decision.strip() or _default_decision(task_class, backfill_status)
    return LegacyTaskEntry(
        task_id=task_id,
        task_class=task_class,
        backfill_status=backfill_status,
        migration_note=existing.migration_note.strip() or "—",
        decision=decision,
    )


def derive_overall_status(entries: list[LegacyTaskEntry], epoch: str) -> tuple[str, str]:
    if epoch == "legacy-v1":
        return "legacy-compatible", "legacy"
    pending_count = sum(1 for entry in entries if entry.backfill_status == "pending")
    execution_rollout = "single-writer" if pending_count == 0 else "dual-readiness"
    upgrade_status = "fully-upgraded" if pending_count == 0 else "partially-upgraded"
    return upgrade_status, execution_rollout


def _task_dirs(project_root: Path) -> list[Path]:
    tasks_root = project_root / "knowledge/tasks"
    if not tasks_root.exists():
        return []
    result: list[Path] = []
    for task_file in tasks_root.rglob("task.md"):
        relative = task_file.relative_to(tasks_root)
        if "_templates" in relative.parts:
            continue
        result.append(task_file.parent)
    return sorted(result)


def build_repo_upgrade_state(
    project_root: Path,
    *,
    epoch: str,
    last_upgrade_task: str,
    today: str | None = None,
    existing: RepoUpgradeState | None = None,
) -> RepoUpgradeState:
    existing_entries = {entry.task_id: entry for entry in existing.entries} if existing else {}
    entries: list[LegacyTaskEntry] = []
    for task_dir in _task_dirs(project_root):
        _, fields = read_task_fields(task_dir / "task.md")
        task_id = fields.get("ID задачи", "").strip()
        if not task_id:
            continue
        task_class = classify_task_fields(fields)
        entries.append(_normalize_entry(task_id, task_class, existing_entries.get(task_id)))
    entries.sort(key=lambda item: item.task_id)
    upgrade_status, execution_rollout = derive_overall_status(entries, epoch)
    return RepoUpgradeState(
        path=repo_upgrade_state_path(project_root),
        system="task-centric-knowledge",
        compatibility_epoch=epoch,
        upgrade_status=upgrade_status,
        execution_rollout=execution_rollout,
        last_upgrade_task=last_upgrade_task,
        updated_at=today or today_iso(),
        entries=tuple(entries),
    )


def render_repo_upgrade_state(state: RepoUpgradeState) -> str:
    lines = [
        "# Состояние перехода task-centric-knowledge",
        "",
        "## Паспорт",
        "",
        "| Поле | Значение |",
        "|------|----------|",
        f"| Система | `{state.system}` |",
        f"| Эпоха совместимости | `{state.compatibility_epoch}` |",
        f"| Статус перехода | `{state.upgrade_status}` |",
        f"| Контур исполнения | `{state.execution_rollout}` |",
        f"| Последняя задача перехода | `{state.last_upgrade_task}` |",
        f"| Дата обновления | `{state.updated_at}` |",
        "",
        "## Исторические задачи",
        "",
        "| TASK-ID | Класс | Статус совместимости | Путь к заметке миграции | Решение |",
        "|---------|-------|----------------------|--------------------------|---------|",
    ]
    if not state.entries:
        lines.append("| `—` | `—` | `—` | `—` | Репозиторий ещё не содержит task-local карточек. |")
    else:
        for entry in state.entries:
            decision = entry.decision.replace("|", "/")
            lines.append(
                f"| `{entry.task_id}` | `{entry.task_class}` | `{entry.backfill_status}` | "
                f"`{entry.migration_note}` | {decision} |"
            )
    return "\n".join(lines) + "\n"


def write_repo_upgrade_state(state: RepoUpgradeState) -> None:
    state.path.parent.mkdir(parents=True, exist_ok=True)
    state.path.write_text(render_repo_upgrade_state(state), encoding="utf-8")


def parse_repo_upgrade_state(state_path: Path) -> RepoUpgradeState:
    lines = state_path.read_text(encoding="utf-8").splitlines()
    passport_rows = _table_rows(lines, PASSPORT_SECTION, ("Поле", "Значение"))
    passport = {field: value for field, value in passport_rows}

    def _passport_value(*aliases: str) -> str:
        for alias in aliases:
            if alias in passport:
                return passport[alias]
        raise ValueError(f"В состоянии перехода репозитория отсутствует поле {aliases[0]!r}.")

    _passport_value("Система")
    _passport_value("Эпоха совместимости")
    _passport_value("Статус перехода", "Статус upgrade")
    _passport_value("Контур исполнения", "Execution rollout")
    _passport_value("Последняя задача перехода")
    _passport_value("Дата обновления")

    epoch = passport["Эпоха совместимости"]
    upgrade_status = _passport_value("Статус перехода", "Статус upgrade")
    execution_rollout = _passport_value("Контур исполнения", "Execution rollout")
    if epoch not in VALID_EPOCHS:
        raise ValueError(f"Некорректная эпоха совместимости: {epoch!r}.")
    if upgrade_status not in VALID_UPGRADE_STATUSES:
        raise ValueError(f"Некорректный статус upgrade: {upgrade_status!r}.")
    if execution_rollout not in VALID_EXECUTION_ROLLOUTS:
        raise ValueError(f"Некорректный execution rollout: {execution_rollout!r}.")
    entries: list[LegacyTaskEntry] = []
    for task_id, task_class, backfill_status, migration_note, decision in _table_rows_with_aliases(
        lines,
        LEGACY_TASKS_SECTION_ALIASES,
        LEGACY_TASK_HEADERS_ALIASES,
    ):
        if task_id == "—":
            continue
        if task_class not in VALID_TASK_CLASSES:
            raise ValueError(f"Некорректный класс legacy-задачи: {task_class!r}.")
        if backfill_status not in VALID_BACKFILL_STATUSES:
            raise ValueError(f"Некорректный статус backfill: {backfill_status!r}.")
        entries.append(
            LegacyTaskEntry(
                task_id=task_id,
                task_class=task_class,
                backfill_status=backfill_status,
                migration_note=migration_note,
                decision=decision.strip(),
            )
        )
    return RepoUpgradeState(
        path=state_path,
        system=_passport_value("Система"),
        compatibility_epoch=epoch,
        upgrade_status=upgrade_status,
        execution_rollout=execution_rollout,
        last_upgrade_task=_passport_value("Последняя задача перехода"),
        updated_at=_passport_value("Дата обновления"),
        entries=tuple(entries),
    )


def load_repo_upgrade_state(project_root: Path) -> RepoUpgradeState | None:
    state_path = repo_upgrade_state_path(project_root)
    if not state_path.exists():
        return None
    return parse_repo_upgrade_state(state_path)


def ensure_repo_upgrade_state(
    project_root: Path,
    *,
    epoch: str,
    last_upgrade_task: str,
    today: str | None = None,
) -> RepoUpgradeState:
    existing = load_repo_upgrade_state(project_root)
    state = build_repo_upgrade_state(
        project_root,
        epoch=epoch,
        last_upgrade_task=last_upgrade_task,
        today=today,
        existing=existing,
    )
    write_repo_upgrade_state(state)
    return state


def update_entry_status(
    state: RepoUpgradeState,
    *,
    task_id: str,
    backfill_status: str,
    migration_note: str,
    decision: str,
    last_upgrade_task: str,
    today: str | None = None,
) -> RepoUpgradeState:
    entries: list[LegacyTaskEntry] = []
    found = False
    for entry in state.entries:
        if entry.task_id != task_id:
            entries.append(entry)
            continue
        entries.append(
            LegacyTaskEntry(
                task_id=entry.task_id,
                task_class=entry.task_class,
                backfill_status=backfill_status,
                migration_note=migration_note,
                decision=decision,
            )
        )
        found = True
    if not found:
        raise ValueError(f"В repo upgrade-state не найдена строка для {task_id}.")
    entries.sort(key=lambda item: item.task_id)
    upgrade_status, execution_rollout = derive_overall_status(entries, state.compatibility_epoch)
    return RepoUpgradeState(
        path=state.path,
        system=state.system,
        compatibility_epoch=state.compatibility_epoch,
        upgrade_status=upgrade_status,
        execution_rollout=execution_rollout,
        last_upgrade_task=last_upgrade_task,
        updated_at=today or today_iso(),
        entries=tuple(entries),
    )


def upgrade_state_summary(project_root: Path, *, existing_system_classification: str) -> dict[str, object]:
    state = load_repo_upgrade_state(project_root)
    if state is None:
        compatibility_epoch = "legacy-v1" if existing_system_classification == "compatible" else "module-core-v1"
        upgrade_status = "legacy-compatible" if compatibility_epoch == "legacy-v1" else "fully-upgraded"
        execution_rollout = "legacy" if compatibility_epoch == "legacy-v1" else "single-writer"
        return {
            "state_path": str(repo_upgrade_state_path(project_root)),
            "state_exists": False,
            "compatibility_epoch": compatibility_epoch,
            "upgrade_status": upgrade_status,
            "execution_rollout": execution_rollout,
            "legacy_pending_count": 0,
            "reference_manual_count": 0,
        }
    pending_count = sum(1 for entry in state.entries if entry.backfill_status == "pending")
    reference_count = sum(1 for entry in state.entries if entry.backfill_status == "manual-reference")
    return {
        "state_path": str(state.path),
        "state_exists": True,
        "compatibility_epoch": state.compatibility_epoch,
        "upgrade_status": state.upgrade_status,
        "execution_rollout": state.execution_rollout,
        "legacy_pending_count": pending_count,
        "reference_manual_count": reference_count,
    }


def write_task_migration_note(
    project_root: Path,
    task_dir: Path,
    *,
    epoch_before: str,
    epoch_after: str,
    task_class: str,
    updated_items: list[str],
    untouched_items: list[str],
    basis_task_id: str,
    today: str | None = None,
) -> str:
    note_path = task_migration_note_path(task_dir)
    note_path.parent.mkdir(parents=True, exist_ok=True)
    updated_lines = "\n".join(f"- {item}" for item in updated_items) or "- `не требуется`"
    untouched_lines = "\n".join(f"- {item}" for item in untouched_items) or "- `не требуется`"
    note_path.write_text(
        "\n".join(
            [
                "# Заметка миграции task-centric-knowledge",
                "",
                "## Паспорт",
                "",
                "| Поле | Значение |",
                "|------|----------|",
                f"| Эпоха до | `{epoch_before}` |",
                f"| Эпоха после | `{epoch_after}` |",
                f"| Класс legacy-задачи | `{task_class}` |",
                f"| Основание/задача | `{basis_task_id}` |",
                f"| Дата обновления | `{today or today_iso()}` |",
                "",
                "## Что обновлено",
                "",
                updated_lines,
                "",
                "## Что не трогалось",
                "",
                untouched_lines,
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return relative_task_migration_note(project_root, task_dir)


def task_class_from_task_file(task_file: Path) -> str:
    _, fields = read_task_fields(task_file)
    return classify_task_fields(fields)


def task_id_from_task_file(task_file: Path) -> str:
    _, fields = read_task_fields(task_file)
    task_id = fields.get("ID задачи", "").strip()
    if not task_id:
        raise ValueError(f"В {task_file} не найден `ID задачи`.")
    return task_id
