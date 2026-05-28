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
    """Результат одного шага workflow.

    Args:
        key: Идентификатор шага.
        status: Статус выполнения (`ok`, `error`, `skipped` и т.п.).
        detail: Человекочитаемое описание результата.
        path: Опциональный путь к затронутому файлу.
    """
    key: str
    status: str
    detail: str
    path: str | None = None


@dataclass
class DeliveryUnit:
    """Delivery unit — единица публикации задачи.

    Args:
        unit_id: Идентификатор unit (`DU-01`).
        purpose: Назначение публикации.
        head: Имя head-ветки.
        base: Имя base-ветки.
        host: Хост публикации (`github`, `gitlab`, `generic`, `none`).
        publication_type: Тип (`pr`, `mr`, `none`).
        status: Статус (`planned`, `local`, `draft`, `review`, `merged`, `closed`).
        url: URL опубликованного PR/MR.
        merge_commit: SHA merge commit.
        cleanup: Состояние cleanup (`не требуется`, `ожидается`, `выполнено`).
    """
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
    def from_cells(cls, cells: list[str]) -> DeliveryUnit:
        """Создать DeliveryUnit из списка ячеек таблицы.

        Args:
            cells: Список из 10 строк — колонки таблицы delivery unit.

        Returns:
            Экземпляр DeliveryUnit.

        Raises:
            ValueError: Если количество колонок не равно 10.
        """
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
        """Преобразовать DeliveryUnit в список ячеек таблицы.

        Returns:
            Список из 10 форматированных строк.
        """
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
    """Версия delivery unit с рангом свежести.

    Args:
        unit: Связанный DeliveryUnit.
        freshness_rank: Кортеж для сортировки по приоритету свежести.
    """
    unit: DeliveryUnit
    freshness_rank: tuple[int, int, int, str]


@dataclass
class PublicationSnapshot:
    """Снимок состояния публикации (PR/MR).

    Args:
        host: Хост публикации.
        publication_type: Тип публикации.
        status: Текущий статус.
        url: URL публикации.
        head: Head-ветка.
        base: Base-ветка.
        merge_commit: SHA merge commit.
    """
    host: str
    publication_type: str
    status: str
    url: str
    head: str
    base: str
    merge_commit: str


def normalize_table_value(value: str) -> str:
    """Нормализовать значение ячейки таблицы (убрать обратные кавычки).

    Args:
        value: Исходная строка из ячейки Markdown-таблицы.

    Returns:
        Строка без окружающих обратных кавычек или исходная строка.
    """
    value = value.strip()
    if value.startswith("`") and value.endswith("`") and len(value) >= 2:
        return value[1:-1]
    return value


def format_table_value(value: str) -> str:
    """Оформить значение в обратные кавычки для таблицы.

    Args:
        value: Исходная строка.

    Returns:
        Строка, обёрнутая в `...`.
    """
    return f"`{value}`"


def normalize_delivery_text(value: str) -> str:
    """Нормализовать текст delivery unit (заменить пустое на placeholder).

    Args:
        value: Исходная строка.

    Returns:
        Нормализованная строка или `—`.
    """
    normalized = normalize_table_value(value)
    return normalized or DELIVERY_ROW_PLACEHOLDER


def sanitize_delivery_text(value: str, *, allow_placeholder: bool = True) -> str:
    """Санитизировать текст для вставки в Markdown-таблицу.

    Заменяет переводы строк и вертикальные черты на безопасные символы.

    Args:
        value: Исходная строка.
        allow_placeholder: Разрешить замену пустой строки на `—`.

    Returns:
        Санитизированная строка.
    """
    sanitized = value.replace("\n", " ").replace("|", "/").strip()
    if not sanitized and allow_placeholder:
        return DELIVERY_ROW_PLACEHOLDER
    return sanitized


def sanitize_registry_summary(value: str) -> str:
    """Санитизировать сводку для registry.md.

    Args:
        value: Исходная строка.

    Returns:
        Строка без переводов строк и вертикальных черт.
    """
    return value.replace("\n", " ").replace("|", "/").strip()


def normalize_unit_id(unit_id: str) -> str:
    """Нормализовать идентификатор delivery unit.

    Приводит к каноническому виду `DU-NN`.

    Args:
        unit_id: Исходный идентификатор.

    Returns:
        Нормализованный идентификатор `DU-NN`.

    Raises:
        ValueError: Если формат не соответствует ожидаемому.
    """
    match = UNIT_ID_RE.fullmatch(unit_id.strip())
    if not match:
        raise ValueError(f"Некорректный Unit ID: {unit_id!r}. Ожидался формат `DU-01`.")
    return f"DU-{int(match.group('number')):02d}"


def delivery_unit_index(unit_id: str) -> int:
    """Извлечь числовой индекс из Unit ID.

    Args:
        unit_id: Идентификатор в формате `DU-NN`.

    Returns:
        Числовой индекс.
    """
    return int(normalize_unit_id(unit_id).split("-", 1)[1])


def normalize_branch_token(value: str) -> str:
    """Нормализовать строку в валидный токен для имени ветки.

    Заменяет недопустимые символы на дефисы, убирает дубликаты.

    Args:
        value: Исходная строка.

    Returns:
        Нормализованный токен в нижнем регистре.
    """
    token = re.sub(r"[^a-z0-9]+", "-", value.lower())
    token = re.sub(r"-{2,}", "-", token).strip("-")
    return token


def default_branch_name(task_id: str, short_name: str) -> str:
    """Сформировать имя task-ветки по умолчанию.

    Args:
        task_id: Идентификатор задачи.
        short_name: Краткое имя задачи.

    Returns:
        Имя ветки вида `task/<task-id>-<short-name>`.
    """
    return f"task/{normalize_branch_token(task_id)}-{normalize_branch_token(short_name)}"


def default_delivery_branch_name(task_id: str, unit_id: str, short_name: str) -> str:
    """Сформировать имя delivery-ветки по умолчанию.

    Args:
        task_id: Идентификатор задачи.
        unit_id: Идентификатор delivery unit.
        short_name: Краткое имя задачи.

    Returns:
        Имя ветки вида `du/<task-id>-uNN-<short-name>`.
    """
    return (
        f"du/{normalize_branch_token(task_id)}-u{delivery_unit_index(unit_id):02d}-"
        f"{normalize_branch_token(short_name)}"
    )


def extract_delivery_branch_index(task_id: str, branch_name: str) -> int | None:
    """Извлечь числовой индекс delivery unit из имени ветки.

    Args:
        task_id: Идентификатор задачи.
        branch_name: Имя ветки.

    Returns:
        Числовой индекс или `None`, если ветка не соответствует паттерну.
    """
    pattern = re.compile(rf"^du/{re.escape(normalize_branch_token(task_id))}-u(?P<number>\d+)(?:-|$)")
    match = pattern.match(branch_name.strip())
    if not match:
        return None
    return int(match.group("number"))


def normalize_delivery_status(status: str) -> str:
    """Нормализовать статус delivery unit.

    Проверяет допустимость и приводит к нижнему регистру.

    Args:
        status: Исходный статус.

    Returns:
        Нормализованный статус.

    Raises:
        ValueError: Если статус не из допустимого набора.
    """
    normalized = status.strip().lower()
    if normalized not in VALID_DELIVERY_STATUSES:
        raise ValueError(
            f"Некорректный статус delivery unit: {status!r}. "
            "Допустимы `planned`, `local`, `draft`, `review`, `merged`, `closed`."
        )
    return normalized


def normalize_cleanup_value(cleanup: str | None, *, default: str) -> str:
    """Нормализовать значение cleanup.

    Проверяет допустимость и возвращает значение или default.

    Args:
        cleanup: Исходное значение или `None`.
        default: Значение по умолчанию.

    Returns:
        Нормализованное значение cleanup.

    Raises:
        ValueError: Если значение не из допустимого набора.
    """
    value = (cleanup or default).strip()
    if value not in VALID_CLEANUP_VALUES:
        raise ValueError(
            f"Некорректное значение Cleanup: {value!r}. "
            "Допустимы `не требуется`, `ожидается`, `выполнено`."
        )
    return value
