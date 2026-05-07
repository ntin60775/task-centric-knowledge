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


## @brief Результат одного шага workflow.
#  @param key      Идентификатор шага.
#  @param status   Статус выполнения (`ok`, `error`, `skipped` и т.п.).
#  @param detail   Человекочитаемое описание результата.
#  @param path     Опциональный путь к затронутому файлу.
@dataclass
class StepResult:
    """Результат одного шага workflow."""
    key: str
    status: str
    detail: str
    path: str | None = None


## @brief Delivery unit — единица публикации задачи.
#
#  @param unit_id           Идентификатор unit (`DU-01`).
#  @param purpose           Назначение публикации.
#  @param head              Имя head-ветки.
#  @param base              Имя base-ветки.
#  @param host              Хост публикации (`github`, `gitlab`, `generic`, `none`).
#  @param publication_type  Тип (`pr`, `mr`, `none`).
#  @param status            Статус (`planned`, `local`, `draft`, `review`, `merged`, `closed`).
#  @param url               URL опубликованного PR/MR.
#  @param merge_commit      SHA merge commit.
#  @param cleanup           Состояние cleanup (`не требуется`, `ожидается`, `выполнено`).
@dataclass
class DeliveryUnit:
    """Delivery unit — единица публикации задачи."""
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

    ## @brief Создать DeliveryUnit из списка ячеек таблицы.
    #  @param cells Список из 10 строк — колонки таблицы delivery unit.
    #  @return      Экземпляр DeliveryUnit.
    #  @raises ValueError Если количество колонок не равно 10.
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

    ## @brief Преобразовать DeliveryUnit в список ячеек таблицы.
    #  @return Список из 10 форматированных строк.
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


## @brief Версия delivery unit с рангом свежести.
#  @param unit           Связанный DeliveryUnit.
#  @param freshness_rank Кортеж для сортировки по приоритету свежести.
@dataclass
class DeliveryUnitVersion:
    """Версия delivery unit с рангом свежести."""
    unit: DeliveryUnit
    freshness_rank: tuple[int, int, int, str]


## @brief Снимок состояния публикации (PR/MR).
#  @param host             Хост публикации.
#  @param publication_type Тип публикации.
#  @param status           Текущий статус.
#  @param url              URL публикации.
#  @param head             Head-ветка.
#  @param base             Base-ветка.
#  @param merge_commit     SHA merge commit.
@dataclass
class PublicationSnapshot:
    """Снимок состояния публикации (PR/MR)."""
    host: str
    publication_type: str
    status: str
    url: str
    head: str
    base: str
    merge_commit: str


## @brief Нормализовать значение ячейки таблицы (убрать обратные кавычки).
#  @param value Исходная строка из ячейки Markdown-таблицы.
#  @return      Строка без окружающих обратных кавычек или исходная строка.
def normalize_table_value(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`") and len(value) >= 2:
        return value[1:-1]
    return value


## @brief Оформить значение в обратные кавычки для таблицы.
#  @param value Исходная строка.
#  @return      Строка, обёрнутая в `...`.
def format_table_value(value: str) -> str:
    return f"`{value}`"


## @brief Нормализовать текст delivery unit (заменить пустое на placeholder).
#  @param value Исходная строка.
#  @return      Нормализованная строка или `—`.
def normalize_delivery_text(value: str) -> str:
    normalized = normalize_table_value(value)
    return normalized or DELIVERY_ROW_PLACEHOLDER


## @brief Санитизировать текст для вставки в Markdown-таблицу.
#
#  Заменяет переводы строк и вертикальные черты на безопасные символы.
#  @param value            Исходная строка.
#  @param allow_placeholder Разрешить замену пустой строки на `—`.
#  @return                  Санитизированная строка.
def sanitize_delivery_text(value: str, *, allow_placeholder: bool = True) -> str:
    sanitized = value.replace("\n", " ").replace("|", "/").strip()
    if not sanitized and allow_placeholder:
        return DELIVERY_ROW_PLACEHOLDER
    return sanitized


## @brief Санитизировать сводку для registry.md.
#  @param value Исходная строка.
#  @return      Строка без переводов строк и вертикальных черт.
def sanitize_registry_summary(value: str) -> str:
    return value.replace("\n", " ").replace("|", "/").strip()


## @brief Нормализовать идентификатор delivery unit.
#
#  Приводит к каноническому виду `DU-NN`.
#  @param unit_id Исходный идентификатор.
#  @return        Нормализованный идентификатор `DU-NN`.
#  @raises ValueError Если формат не соответствует ожидаемому.
def normalize_unit_id(unit_id: str) -> str:
    match = UNIT_ID_RE.fullmatch(unit_id.strip())
    if not match:
        raise ValueError(f"Некорректный Unit ID: {unit_id!r}. Ожидался формат `DU-01`.")
    return f"DU-{int(match.group('number')):02d}"


## @brief Извлечь числовой индекс из Unit ID.
#  @param unit_id Идентификатор в формате `DU-NN`.
#  @return        Числовой индекс.
def delivery_unit_index(unit_id: str) -> int:
    return int(normalize_unit_id(unit_id).split("-", 1)[1])


## @brief Нормализовать строку в валидный токен для имени ветки.
#
#  Заменяет недопустимые символы на дефисы, убирает дубликаты.
#  @param value Исходная строка.
#  @return      Нормализованный токен в нижнем регистре.
def normalize_branch_token(value: str) -> str:
    token = re.sub(r"[^a-z0-9]+", "-", value.lower())
    token = re.sub(r"-{2,}", "-", token).strip("-")
    return token


## @brief Сформировать имя task-ветки по умолчанию.
#  @param task_id    Идентификатор задачи.
#  @param short_name Краткое имя задачи.
#  @return           Имя ветки вида `task/<task-id>-<short-name>`.
def default_branch_name(task_id: str, short_name: str) -> str:
    return f"task/{normalize_branch_token(task_id)}-{normalize_branch_token(short_name)}"


## @brief Сформировать имя delivery-ветки по умолчанию.
#  @param task_id    Идентификатор задачи.
#  @param unit_id    Идентификатор delivery unit.
#  @param short_name Краткое имя задачи.
#  @return           Имя ветки вида `du/<task-id>-uNN-<short-name>`.
def default_delivery_branch_name(task_id: str, unit_id: str, short_name: str) -> str:
    return (
        f"du/{normalize_branch_token(task_id)}-u{delivery_unit_index(unit_id):02d}-"
        f"{normalize_branch_token(short_name)}"
    )


## @brief Извлечь числовой индекс delivery unit из имени ветки.
#  @param task_id     Идентификатор задачи.
#  @param branch_name Имя ветки.
#  @return            Числовой индекс или `None`, если ветка не соответствует паттерну.
def extract_delivery_branch_index(task_id: str, branch_name: str) -> int | None:
    pattern = re.compile(rf"^du/{re.escape(normalize_branch_token(task_id))}-u(?P<number>\d+)(?:-|$)")
    match = pattern.match(branch_name.strip())
    if not match:
        return None
    return int(match.group("number"))


## @brief Нормализовать статус delivery unit.
#
#  Проверяет допустимость и приводит к нижнему регистру.
#  @param status Исходный статус.
#  @return       Нормализованный статус.
#  @raises ValueError Если статус не из допустимого набора.
def normalize_delivery_status(status: str) -> str:
    normalized = status.strip().lower()
    if normalized not in VALID_DELIVERY_STATUSES:
        raise ValueError(
            f"Некорректный статус delivery unit: {status!r}. "
            "Допустимы `planned`, `local`, `draft`, `review`, `merged`, `closed`."
        )
    return normalized


## @brief Нормализовать значение cleanup.
#
#  Проверяет допустимость и возвращает значение или default.
#  @param cleanup Исходное значение или `None`.
#  @param default Значение по умолчанию.
#  @return        Нормализованное значение cleanup.
#  @raises ValueError Если значение не из допустимого набора.
def normalize_cleanup_value(cleanup: str | None, *, default: str) -> str:
    value = (cleanup or default).strip()
    if value not in VALID_CLEANUP_VALUES:
        raise ValueError(
            f"Некорректное значение Cleanup: {value!r}. "
            "Допустимы `не требуется`, `ожидается`, `выполнено`."
        )
    return value
