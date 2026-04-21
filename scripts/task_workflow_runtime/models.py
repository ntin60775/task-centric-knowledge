"""Domain values and common helpers for task workflow runtime."""

from __future__ import annotations

import re
from dataclasses import dataclass


PLACEHOLDER_BRANCH_VALUES = {"", "—", "не создана"}
TASK_SUMMARY_FIELD = "Человекочитаемое описание"
TABLE_ROW_RE = re.compile(r"^\|\s*(?P<field>[^|]+?)\s*\|\s*(?P<value>.*?)\s*\|$")
DELIVERY_SECTION_TITLE = "## Контур публикации"
DELIVERY_TABLE_HEADER = (
    "| Unit ID | Назначение | Head | Base | Host | Тип публикации | "
    "Статус | URL | Merge commit | Cleanup |"
)
DELIVERY_TABLE_SEPARATOR = "|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|"
DELIVERY_INTRO_LINES = (
    "Delivery unit описывает конкретную поставку через ветку и публикацию.",
    "В одном `task.md` допускается `0..N` delivery units.",
)
DELIVERY_ROW_PLACEHOLDER = "—"
VALID_HOSTS = {"none", "github", "gitlab", "generic"}
VALID_PUBLICATION_TYPES = {"none", "pr", "mr"}
VALID_DELIVERY_STATUSES = {"planned", "local", "draft", "review", "merged", "closed"}
VALID_CLEANUP_VALUES = {"не требуется", "ожидается", "выполнено"}
VALID_TASK_STATUSES = {
    "черновик",
    "готова к работе",
    "в работе",
    "на проверке",
    "ждёт пользователя",
    "заблокирована",
    "завершена",
    "отменена",
}
FINAL_TASK_STATUSES = {"завершена", "отменена"}
DELIVERY_STATUS_PRIORITY = {
    "planned": 0,
    "local": 1,
    "draft": 2,
    "review": 3,
    "closed": 4,
    "merged": 5,
}
UNIT_ID_RE = re.compile(r"^(?:DU-)?0*(?P<number>\d+)$", re.IGNORECASE)
MERGE_REQUEST_URL_RE = re.compile(r"/(?:-?/)?merge_requests/(?P<number>\d+)(?:/|$)")


@dataclass
class StepResult:
    key: str
    status: str
    detail: str
    path: str | None = None


@dataclass
class DeliveryUnit:
    unit_id: str
    purpose: str
    head: str
    base: str
    host: str
    publication_type: str
    status: str
    url: str
    merge_commit: str
    cleanup: str

    @classmethod
    def from_cells(cls, cells: list[str]) -> "DeliveryUnit":
        if len(cells) != 10:
            raise ValueError(f"Ожидалось 10 колонок delivery unit, получено {len(cells)}.")
        normalized_cells = [normalize_table_value(cell) for cell in cells]
        return cls(
            unit_id=normalize_unit_id(normalized_cells[0]),
            purpose=normalize_delivery_text(normalized_cells[1]),
            head=normalize_delivery_text(normalized_cells[2]),
            base=normalize_delivery_text(normalized_cells[3]),
            host=normalize_delivery_text(normalized_cells[4]),
            publication_type=normalize_delivery_text(normalized_cells[5]),
            status=normalize_delivery_text(normalized_cells[6]),
            url=normalize_delivery_text(normalized_cells[7]),
            merge_commit=normalize_delivery_text(normalized_cells[8]),
            cleanup=normalize_delivery_text(normalized_cells[9]),
        )

    def to_cells(self) -> list[str]:
        return [
            format_table_value(self.unit_id),
            sanitize_delivery_text(self.purpose, allow_placeholder=False),
            format_table_value(self.head),
            format_table_value(self.base),
            format_table_value(self.host),
            format_table_value(self.publication_type),
            format_table_value(self.status),
            format_table_value(self.url),
            format_table_value(self.merge_commit),
            format_table_value(self.cleanup),
        ]


@dataclass
class DeliveryUnitVersion:
    unit: DeliveryUnit
    freshness_rank: tuple[int, int, int, str]


@dataclass
class PublicationSnapshot:
    host: str
    publication_type: str
    status: str
    url: str
    head: str
    base: str
    merge_commit: str


def normalize_table_value(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`") and len(value) >= 2:
        return value[1:-1]
    return value


def format_table_value(value: str) -> str:
    return f"`{value}`"


def normalize_delivery_text(value: str) -> str:
    normalized = normalize_table_value(value)
    return normalized or DELIVERY_ROW_PLACEHOLDER


def sanitize_delivery_text(value: str, *, allow_placeholder: bool = True) -> str:
    sanitized = value.replace("\n", " ").replace("|", "/").strip()
    if not sanitized and allow_placeholder:
        return DELIVERY_ROW_PLACEHOLDER
    return sanitized


def sanitize_registry_summary(value: str) -> str:
    return value.replace("\n", " ").replace("|", "/").strip()


def normalize_unit_id(unit_id: str) -> str:
    match = UNIT_ID_RE.fullmatch(unit_id.strip())
    if not match:
        raise ValueError(f"Некорректный Unit ID: {unit_id!r}. Ожидался формат `DU-01`.")
    return f"DU-{int(match.group('number')):02d}"


def delivery_unit_index(unit_id: str) -> int:
    return int(normalize_unit_id(unit_id).split("-", 1)[1])


def normalize_branch_token(value: str) -> str:
    token = re.sub(r"[^a-z0-9]+", "-", value.lower())
    token = re.sub(r"-{2,}", "-", token).strip("-")
    return token


def default_branch_name(task_id: str, short_name: str) -> str:
    return f"task/{normalize_branch_token(task_id)}-{normalize_branch_token(short_name)}"


def default_delivery_branch_name(task_id: str, unit_id: str, short_name: str) -> str:
    return (
        f"du/{normalize_branch_token(task_id)}-u{delivery_unit_index(unit_id):02d}-"
        f"{normalize_branch_token(short_name)}"
    )


def extract_delivery_branch_index(task_id: str, branch_name: str) -> int | None:
    pattern = re.compile(rf"^du/{re.escape(normalize_branch_token(task_id))}-u(?P<number>\d+)(?:-|$)")
    match = pattern.match(branch_name.strip())
    if not match:
        return None
    return int(match.group("number"))


def normalize_delivery_status(status: str) -> str:
    normalized = status.strip().lower()
    if normalized not in VALID_DELIVERY_STATUSES:
        raise ValueError(
            f"Некорректный статус delivery unit: {status!r}. "
            "Допустимы `planned`, `local`, `draft`, `review`, `merged`, `closed`."
        )
    return normalized


def normalize_cleanup_value(cleanup: str | None, *, default: str) -> str:
    value = (cleanup or default).strip()
    if value not in VALID_CLEANUP_VALUES:
        raise ValueError(
            f"Некорректное значение Cleanup: {value!r}. "
            "Допустимы `не требуется`, `ожидается`, `выполнено`."
        )
    return value
