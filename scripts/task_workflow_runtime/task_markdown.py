"""task.md parsing and rendering helpers."""

from __future__ import annotations

from pathlib import Path

from .models import (
    DELIVERY_INTRO_LINES,
    DELIVERY_ROW_PLACEHOLDER,
    DELIVERY_SECTION_TITLE,
    DELIVERY_TABLE_HEADER,
    DELIVERY_TABLE_SEPARATOR,
    TASK_SUMMARY_FIELD,
    TABLE_ROW_RE,
    DeliveryUnit,
    delivery_unit_index,
    format_table_value,
    normalize_table_value,
    sanitize_registry_summary,
)


def split_markdown_row(line: str) -> list[str] | None:
    """Split a Markdown table row into individual cells.

    Args:
        line: Raw line from a Markdown table.

    Returns:
        List of cell strings, or None if not a table row.
    """
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    return [part.strip() for part in stripped.strip("|").split("|")]


def find_section_bounds(lines: list[str], title: str) -> tuple[int, int] | None:
    """Find the start and end line indices of a Markdown section.

    Args:
        lines: Document lines.
        title: Section heading to search for.

    Returns:
        Tuple of (start_index, end_index), or None if not found.
    """
    for start_index, line in enumerate(lines):
        if line.strip() != title:
            continue
        end_index = len(lines)
        for candidate in range(start_index + 1, len(lines)):
            if lines[candidate].startswith("## "):
                end_index = candidate
                break
        return start_index, end_index
    return None


def _parse_delivery_units(
    lines: list[str],
    *,
    collect_errors: bool,
) -> tuple[list[DeliveryUnit], list[str]]:
    bounds = find_section_bounds(lines, DELIVERY_SECTION_TITLE)
    if bounds is None:
        return [], []
    start_index, end_index = bounds
    units: list[DeliveryUnit] = []
    errors: list[str] = []
    for index in range(start_index, end_index):
        line = lines[index]
        cells = split_markdown_row(line)
        if not cells:
            continue
        if cells[0] == "Unit ID" or cells[0].startswith("---------"):
            continue
        if len(cells) != 10:
            message = f"Строка {index + 1}: ожидалось 10 колонок delivery unit, получено {len(cells)}."
            if collect_errors:
                errors.append(message)
            continue
        if normalize_table_value(cells[0]) == DELIVERY_ROW_PLACEHOLDER:
            continue
        try:
            units.append(DeliveryUnit.from_cells(cells))
        except ValueError as error:
            if not collect_errors:
                raise
            errors.append(f"Строка {index + 1}: {error}")
    return units, errors


def parse_delivery_units(lines: list[str]) -> list[DeliveryUnit]:
    """Parse delivery units from task markdown lines.

    Args:
        lines: Document lines.

    Returns:
        List of parsed DeliveryUnit objects.
    """
    units, _ = _parse_delivery_units(lines, collect_errors=False)
    return units


def parse_delivery_units_safe(lines: list[str]) -> tuple[list[DeliveryUnit], list[str]]:
    """Parse delivery units, collecting parse errors instead of raising.

    Args:
        lines: Document lines.

    Returns:
        Tuple of parsed units and collected error messages.
    """
    return _parse_delivery_units(lines, collect_errors=True)


def render_delivery_units_section(units: list[DeliveryUnit]) -> list[str]:
    """Render delivery units as a Markdown section.

    Args:
        units: List of delivery units to render.

    Returns:
        List of Markdown lines.
    """
    rendered = [
        DELIVERY_SECTION_TITLE,
        "",
        *DELIVERY_INTRO_LINES,
        "",
        DELIVERY_TABLE_HEADER,
        DELIVERY_TABLE_SEPARATOR,
    ]
    if not units:
        rendered.append(
            "| `—` | — | `—` | `—` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |"
        )
        return rendered
    for unit in sorted(units, key=lambda item: delivery_unit_index(item.unit_id)):
        rendered.append("| " + " | ".join(unit.to_cells()) + " |")
    return rendered


def upsert_delivery_units_section(lines: list[str], units: list[DeliveryUnit]) -> list[str]:
    """Insert or replace the delivery units section in task lines.

    Args:
        lines: Document lines.
        units: Delivery units to insert.

    Returns:
        Updated document lines.
    """
    rendered = render_delivery_units_section(units)
    bounds = find_section_bounds(lines, DELIVERY_SECTION_TITLE)
    if bounds is None:
        insert_at = next(
            (index for index, line in enumerate(lines) if line.strip() == "## Текущий этап"),
            len(lines),
        )
        prefix = lines[:insert_at]
        suffix = lines[insert_at:]
        if prefix and prefix[-1] != "":
            prefix = prefix + [""]
        updated = prefix + rendered
        if suffix and updated[-1] != "":
            updated.append("")
        return updated + suffix
    start_index, end_index = bounds
    updated = lines[:start_index] + rendered
    if end_index < len(lines) and updated and updated[-1] != "" and lines[end_index] != "":
        updated.append("")
    updated.extend(lines[end_index:])
    return updated


def replace_section_body(lines: list[str], title: str, body_lines: list[str]) -> None:
    """Replace the body of a Markdown section.

    Args:
        lines: Mutable document lines.
        title: Section heading.
        body_lines: New body lines for the section.
    """
    bounds = find_section_bounds(lines, title)
    if bounds is None:
        if lines and lines[-1] != "":
            lines.append("")
        lines.append(title)
        lines.append("")
        lines.extend(body_lines)
        return
    start_index, end_index = bounds
    replacement = [title, ""]
    replacement.extend(body_lines)
    lines[start_index:end_index] = replacement


def replace_task_field(lines: list[str], field: str, value: str) -> None:
    """Replace the value of a task table field.

    Args:
        lines: Mutable document lines.
        field: Field name to replace.
        value: New field value.

    Raises:
        ValueError: If the field is not found.
    """
    replacement = f"| {field} | {format_table_value(value)} |"
    for index, line in enumerate(lines):
        match = TABLE_ROW_RE.match(line)
        if match and match.group("field").strip() == field:
            lines[index] = replacement
            return
    raise ValueError(f"В task.md не найдено поле {field!r}.")


def upsert_task_field(lines: list[str], field: str, value: str, *, after_field: str) -> None:
    """Upsert a task table field after a reference field.

    Args:
        lines: Mutable document lines.
        field: Field name to upsert.
        value: Field value.
        after_field: Name of the field to insert after.

    Raises:
        ValueError: If the reference field is not found.
    """
    replacement = f"| {field} | {format_table_value(value)} |"
    insert_index: int | None = None
    existing_indexes: list[int] = []
    for index, line in enumerate(lines):
        match = TABLE_ROW_RE.match(line)
        if not match:
            continue
        current_field = match.group("field").strip()
        if current_field == field:
            existing_indexes.append(index)
            continue
        if current_field == after_field:
            insert_index = index + 1
    if existing_indexes:
        first_index = existing_indexes[0]
        lines[first_index] = replacement
        for duplicate_index in reversed(existing_indexes[1:]):
            del lines[duplicate_index]
        return
    if insert_index is not None:
        lines.insert(insert_index, replacement)
        return
    raise ValueError(f"В task.md не найдено поле {after_field!r} для вставки {field!r}.")


def read_task_fields(task_file: Path) -> tuple[list[str], dict[str, str]]:
    """Read a task file and parse its fields.

    Args:
        task_file: Path to task.md.

    Returns:
        Tuple of document lines and parsed fields dictionary.
    """
    lines = task_file.read_text(encoding="utf-8").splitlines()
    return lines, parse_task_fields(lines)


def parse_task_fields(lines: list[str]) -> dict[str, str]:
    """Parse task field table rows from document lines.

    Args:
        lines: Document lines.

    Returns:
        Dictionary of field names to normalized values.
    """
    fields: dict[str, str] = {}
    for line in lines:
        match = TABLE_ROW_RE.match(line)
        if not match:
            continue
        field_name = match.group("field").strip()
        if field_name in fields:
            continue
        fields[field_name] = normalize_table_value(match.group("value"))
    return fields


def update_task_file(
    task_file: Path,
    branch_name: str,
    *,
    today: str,
    summary: str | None = None,
    status: str | None = None,
    current_stage: str | None = None,
) -> dict[str, str]:
    """Update core task file fields.

    Args:
        task_file: Path to task.md.
        branch_name: Branch name to record.
        today: Today's date string.
        summary: Optional summary to set.
        status: Optional status to set.
        current_stage: Optional current stage text.

    Returns:
        Updated fields dictionary.
    """
    lines, fields = read_task_fields(task_file)
    if summary:
        upsert_task_field(lines, TASK_SUMMARY_FIELD, summary, after_field="Краткое имя")
    if status:
        replace_task_field(lines, "Статус", status)
    if current_stage is not None:
        replace_section_body(lines, "## Текущий этап", [current_stage])
    replace_task_field(lines, "Ветка", branch_name)
    replace_task_field(lines, "Дата обновления", today)
    task_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if summary:
        fields[TASK_SUMMARY_FIELD] = summary
    if status:
        fields["Статус"] = status
    fields["Ветка"] = branch_name
    fields["Дата обновления"] = today
    return fields


def update_task_file_with_delivery_units(
    task_file: Path,
    branch_name: str,
    delivery_units: list[DeliveryUnit],
    *,
    today: str,
    summary: str | None = None,
    status: str | None = None,
    current_stage: str | None = None,
) -> dict[str, str]:
    """Update task file fields and the delivery units section.

    Args:
        task_file: Path to task.md.
        branch_name: Branch name to record.
        delivery_units: Delivery units to render.
        today: Today's date string.
        summary: Optional summary to set.
        status: Optional status to set.
        current_stage: Optional current stage text.

    Returns:
        Updated fields dictionary.
    """
    lines, fields = read_task_fields(task_file)
    if summary:
        upsert_task_field(lines, TASK_SUMMARY_FIELD, summary, after_field="Краткое имя")
    if status:
        replace_task_field(lines, "Статус", status)
    if current_stage is not None:
        replace_section_body(lines, "## Текущий этап", [current_stage])
    replace_task_field(lines, "Ветка", branch_name)
    replace_task_field(lines, "Дата обновления", today)
    updated_lines = upsert_delivery_units_section(lines, delivery_units)
    task_file.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
    if summary:
        fields[TASK_SUMMARY_FIELD] = summary
    if status:
        fields["Статус"] = status
    fields["Ветка"] = branch_name
    fields["Дата обновления"] = today
    return fields


def task_summary_from_fields(fields: dict[str, str]) -> str | None:
    """Extract the canonical task summary from parsed fields.

    Args:
        fields: Parsed task fields dictionary.

    Returns:
        Summary string, or None if missing or placeholder.
    """
    summary = sanitize_registry_summary(fields.get(TASK_SUMMARY_FIELD, ""))
    if not summary or summary == DELIVERY_ROW_PLACEHOLDER:
        return None
    return summary


def reference_mode_warning(fields: dict[str, str], *, field_name: str = "Справочный режим") -> str | None:
    """Warn if the reference mode field contains an invalid value.

    Args:
        fields: Parsed task fields dictionary.
        field_name: Name of the reference mode field.

    Returns:
        The invalid value, or None if acceptable.
    """
    value = fields.get(field_name, "нет").strip()
    if value in {"", "нет", "reference"}:
        return None
    return value


def derive_goal_summary_from_task(task_file: Path) -> str | None:
    """Derive a summary from the goal section of a task file.

    Args:
        task_file: Path to task.md.

    Returns:
        First non-empty goal line, or None.
    """
    lines = task_file.read_text(encoding="utf-8").splitlines()
    return derive_goal_summary_from_lines(lines)


def derive_goal_summary_from_lines(lines: list[str]) -> str | None:
    """Derive a summary from the goal section of task lines.

    Args:
        lines: Document lines.

    Returns:
        First non-empty goal line, or None.
    """
    in_goal = False
    for line in lines:
        if line.startswith("## ") and line != "## Цель":
            if in_goal:
                break
        if line == "## Цель":
            in_goal = True
            continue
        if not in_goal:
            continue
        stripped = line.strip()
        if stripped:
            return sanitize_registry_summary(stripped)
    return None


def count_task_field_occurrences(lines: list[str], field: str) -> int:
    """Count how many times a field appears in task lines.

    Args:
        lines: Document lines.
        field: Field name to count.

    Returns:
        Occurrence count.
    """
    count = 0
    for line in lines:
        match = TABLE_ROW_RE.match(line)
        if match and match.group("field").strip() == field:
            count += 1
    return count


def derive_summary_from_task(task_file: Path) -> str | None:
    """Derive a task summary from fields or the goal section.

    Args:
        task_file: Path to task.md.

    Returns:
        Best available summary string, or None.
    """
    _, fields = read_task_fields(task_file)
    return task_summary_from_fields(fields) or derive_goal_summary_from_task(task_file)
