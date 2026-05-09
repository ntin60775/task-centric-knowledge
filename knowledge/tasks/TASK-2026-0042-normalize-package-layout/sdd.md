# SDD по задаче TASK-2026-0042

## Паспорт SDD

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0042` |
| Статус | `черновик` |
| Версия | `1` |
| Дата обновления | `2026-05-06` |

## 0. Инварианты и verification matrix

### Полный invariant set

- `INV-01`: Все runtime-модули доступны через `task_knowledge.*` namespace из `src/task_knowledge/`.
- `INV-02`: `pyproject.toml` использует src-layout: `package-dir = {"" = "src"}`, `packages.find.where = ["src"]`.
- `INV-03`: Unified CLI `task-knowledge` работает после переноса: все подкоманды (`install`, `task`, `workflow`, `module`, `file`, `borrowings`, `doctor`) функционируют.
- `INV-04`: Все внутренние import-ы между runtime-модулями используют новый `task_knowledge.*` namespace.
- `INV-05`: `make install-local` устанавливает CLI из `src/` и `task-knowledge --help` работает.
- `INV-06`: `make check` и полный тестовый прогон проходят без ошибок.
- `INV-07`: `scripts/install_global_skill.py` копирует runtime из `src/task_knowledge/` в live-copy.
- `INV-08`: `ruff` и `mypy` (если доступны) проходят на `src/`.

### Связанные артефакты проверки

- `artifacts/verification-matrix.md`.

## 1. Проблема и цель

### Проблема

Текущий package layout использует `scripts/` как корень пакета Python:

```toml
[tool.setuptools.package-dir]
"" = "scripts"

[tool.setuptools.packages.find]
where = ["scripts"]
```

Runtime-модули разбросаны по `scripts/`:
- `scripts/task_knowledge/` — пакет с версией и `__main__.py`.
- `scripts/task_knowledge_cli.py` — CLI entrypoint (741 строка).
- `scripts/install_skill_runtime/` — install runtime.
- `scripts/task_workflow_runtime/` — workflow runtime.
- `scripts/module_core_runtime/` — module core.
- `scripts/borrowings_runtime/` — borrowings.

Это:
- нестандартно для Python проектов (ожидается `src/` или flat layout);
- смешивает shell-скрипты, Python-модули и facade-скрипты в одной директории;
- усложняет навигацию и понимание структуры;
- затрудняет интеграцию с IDE и инструментами.

### Цель

Стандартный Python src-layout: все runtime-модули в `src/task_knowledge/`, `scripts/` только для shell-скриптов.

## 2. Архитектура и границы

### Текущая структура (до)

```
scripts/
├── task_knowledge/          # Python package
│   ├── __init__.py
│   ├── __main__.py
│   └── version.py
├── task_knowledge_cli.py    # CLI entrypoint
├── install_skill_runtime/   # Install runtime
├── task_workflow_runtime/   # Workflow runtime
├── module_core_runtime/     # Module core runtime
├── borrowings_runtime/      # Borrowings runtime
├── install_skill.py         # Legacy facade
├── task_workflow.py         # Legacy facade
├── task_query.py            # Legacy facade
├── install_global_skill.py  # Global installer
└── check-docs-localization.sh
```

### Целевая структура (после)

```
src/
└── task_knowledge/
    ├── __init__.py           # Публичный API пакета
    ├── __main__.py           # python -m task_knowledge
    ├── cli.py                # CLI entrypoint (бывш. task_knowledge_cli.py)
    ├── version.py            # Версия и константы
    ├── install_runtime/      # Install runtime (бывш. install_skill_runtime)
    ├── workflow_runtime/     # Workflow runtime (бывш. task_workflow_runtime)
    ├── module_core_runtime/  # Module core runtime
    └── borrowings_runtime/   # Borrowings runtime

scripts/
├── install_global_skill.py  # Глобальный installer
└── check-docs-localization.sh
```

### Карта переименований

| Было (scripts/) | Стало (src/task_knowledge/) |
|-----------------|-----------------------------|
| `task_knowledge/` | `.` (корень пакета) |
| `task_knowledge_cli.py` | `cli.py` |
| `install_skill_runtime/` | `install_runtime/` |
| `task_workflow_runtime/` | `workflow_runtime/` |
| `module_core_runtime/` | `module_core_runtime/` |
| `borrowings_runtime/` | `borrowings_runtime/` |

### Что остаётся вне задачи

- `scripts/install_skill.py`, `scripts/task_workflow.py`, `scripts/task_query.py` — удаляются в TASK-2026-0041.
- `assets/`, `references/`, `knowledge/` — не трогаются.
- Логика runtime-модулей не меняется.

### Допустимые и недопустимые связи

**Допустимые связи:**
- Импорты между runtime-модулями: `from task_knowledge.workflow_runtime import ...`.
- CLI импортирует из runtime: `from task_knowledge.install_runtime import ...`.
- Тесты импортируют из `task_knowledge.*`.

**Недопустимые связи:**
- Импорты через старые пути `from install_skill_runtime` (после переноса).
- `pyproject.toml` с `package-dir` указывающим на `scripts`.
- Runtime-модули, импортирующие facade-скрипты.

### Новые зависимости и их обоснование

`нет`

### Наблюдаемые сигналы и диагностические маркеры

`не требуется`

## 3. Изменения данных / схемы / metadata

- `pyproject.toml`:
  - `[tool.setuptools.package-dir]`: `"" = "src"`.
  - `[tool.setuptools.packages.find]`: `where = ["src"]`.
  - `py-modules`: убрать facade-модули (или обновить).
  - `[tool.ruff]`: `src = ["src", "tests"]`.
  - `[tool.mypy]`: `files = ["src"]`.

## 4. Новые сущности и интерфейсы

- `src/task_knowledge/__init__.py` — публичный API пакета, реэкспорт ключевых символов.
- `src/task_knowledge/cli.py` — бывший `scripts/task_knowledge_cli.py`.
- `src/task_knowledge/install_runtime/` — бывший `scripts/install_skill_runtime/`.
- `src/task_knowledge/workflow_runtime/` — бывший `scripts/task_workflow_runtime/`.

## 5. Изменения в существующих компонентах

### `src/task_knowledge/__init__.py` (новый)

Публичный API:
```python
"""Task-centric knowledge — операционная система задач внутри репозитория."""

from .version import __version__, CLI_VERSION, CONSUMER_RUNTIME_CONTRACT
```

### `src/task_knowledge/__main__.py`

Было:
```python
from task_knowledge_cli import main
```

Стало:
```python
from task_knowledge.cli import main
```

### `src/task_knowledge/cli.py` (бывш. `task_knowledge_cli.py`)

Обновить импорты:
```python
# Было
from install_skill_runtime import ...
from task_workflow_runtime import ...
from borrowings_runtime import ...
from module_core_runtime.query_cli import ...
from task_knowledge.version import ...

# Стало
from task_knowledge.install_runtime import ...
from task_knowledge.workflow_runtime import ...
from task_knowledge.borrowings_runtime import ...
from task_knowledge.module_core_runtime.query_cli import ...
from task_knowledge.version import ...
```

Удалить `SCRIPT_DIR` и манипуляции с `sys.path` (больше не нужны при src-layout).

### Все runtime-модули

Обновить внутренние кросс-импорты:
- `install_skill_runtime` → `task_knowledge.install_runtime`.
- `task_workflow_runtime` → `task_knowledge.workflow_runtime`.
- `module_core_runtime` → `task_knowledge.module_core_runtime`.
- `borrowings_runtime` → `task_knowledge.borrowings_runtime`.

### `scripts/install_global_skill.py`

Обновить пути к runtime:
```python
# Было
CLI_SCRIPT = skill_root / "scripts" / "task_knowledge_cli.py"

# Стало
CLI_SCRIPT = skill_root / "src" / "task_knowledge" / "cli.py"
```

Обновить копируемые пути (live-copy должен содержать `src/task_knowledge/`).

### `Makefile`

Обновить цели `install-local`, `check`, `check-strict`:
- `pip install -e .` (без указания `scripts/`).
- `ruff check src/ tests/`.
- `mypy src/`.

### Тесты

Обновить импорты:
```python
# Было
from install_skill_runtime import ...
from task_workflow_runtime import ...

# Стало
from task_knowledge.install_runtime import ...
from task_knowledge.workflow_runtime import ...
```

## 6. Этапы реализации и проверки

### Этап 1: Создание структуры `src/task_knowledge/`

- Создать `src/task_knowledge/__init__.py`.
- Скопировать `scripts/task_knowledge/__init__.py`, `__main__.py`, `version.py`.
- Обновить `__main__.py`: `from task_knowledge.cli import main`.
- Verify: `python3 -c "from task_knowledge import __version__; print(__version__)"`.
- Аудит: `IMPLEMENTATION_AUDIT`.

### Этап 2: Перенос `cli.py`

- Скопировать `scripts/task_knowledge_cli.py` → `src/task_knowledge/cli.py`.
- Обновить импорты в `cli.py` на `task_knowledge.*`.
- Удалить `sys.path` манипуляции.
- Verify: `python3 -c "from task_knowledge.cli import main"`.
- Аудит: `IMPLEMENTATION_AUDIT`.

### Этап 3: Перенос runtime-модулей

- `scripts/install_skill_runtime/` → `src/task_knowledge/install_runtime/`.
- `scripts/task_workflow_runtime/` → `src/task_knowledge/workflow_runtime/`.
- `scripts/module_core_runtime/` → `src/task_knowledge/module_core_runtime/`.
- `scripts/borrowings_runtime/` → `src/task_knowledge/borrowings_runtime/`.
- Обновить все import-ы в каждом модуле.
- Verify: `python3 -c "from task_knowledge.install_runtime import check; from task_knowledge.workflow_runtime import sync_task; from task_knowledge.module_core_runtime import ...; from task_knowledge.borrowings_runtime import ..."`.
- Аудит: `IMPLEMENTATION_AUDIT`.

### Этап 4: Обновление конфигурации

- `pyproject.toml`: обновить `package-dir`, `packages.find`, `py-modules`.
- `pyproject.toml`: обновить `ruff.src`, `mypy.files`.
- Verify: `pip install -e .` (editable install), `task-knowledge --help`.
- Аудит: `IMPLEMENTATION_AUDIT`.

### Этап 5: Обновление скриптов

- `scripts/install_global_skill.py`: обновить пути.
- `Makefile`: обновить цели.
- Verify: `make install-local`, `make check`.
- Аудит: `IMPLEMENTATION_AUDIT`.

### Этап 6: Обновление тестов и references

- Обновить импорты в тестах.
- Проверить references на упоминания `scripts/`.
- Verify: `python3 -m unittest discover -s tests -v`, `grep -r "scripts/" references/`.
- Аудит: `IMPLEMENTATION_AUDIT`.

### Финальный этап: Интеграция

- Полный тестовый прогон.
- `make check`, `make install-local`.
- `task-knowledge` все подкоманды.
- `ruff check src/ tests/`, `mypy src/`.
- Доказательство покрытия `artifacts/verification-matrix.md`.
- Аудит: `INTEGRATION_AUDIT`.

## 7. Критерии приёмки

1. `src/task_knowledge/` содержит все runtime-модули.
2. `pyproject.toml` настроен на `src` layout.
3. Все import-ы используют `task_knowledge.*` namespace.
4. `task-knowledge` все подкоманды работают.
5. `make check` зелёный.
6. Тесты проходят.
7. `make install-local` работает.
8. `ruff` и `mypy` проходят.
9. Все инварианты покрыты.

## 8. Стоп-критерии

1. Циклические импорты, которые нельзя разрешить.
2. Тесты не проходят и не могут быть исправлены без изменения логики.
3. `make install-global` ломается и не может быть исправлен.
4. Любой инвариант не может быть доказан.

## Связь с остальными файлами задачи

- `task.md` — источник истины по статусу и границам.
- `plan.md` — исполнимый план.
- `artifacts/verification-matrix.md` — матрица покрытия.
- `worklog.md` — прохождение этапов.
- `decisions.md` — отклонения от SDD.
