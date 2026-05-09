# Карточка задачи TASK-2026-0048.1

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0048.1` |
| Parent ID | `TASK-2026-0048` |
| Уровень вложенности | `1` |
| Ключ в путях | `TASK-2026-0048.1` |
| Технический ключ для новых именуемых сущностей | `—` |
| Краткое имя | `doxygen-phase-2-module-core-and-helpers` |
| Человекочитаемое описание | Doxygen phase 2: документирование module_core_runtime, внутренних хелперов и оставшихся runtime-модулей. |
| Статус | `завершена` |
| Приоритет | `средний` |
| Ответственный | `не назначен` |
| Ветка | `task/task-2026-0048-doxygen-integration` |
| Требуется SDD | `нет` |
| Статус SDD | `—` |
| Ссылка на SDD | `—` |
| Дата создания | `2026-05-07` |
| Дата обновления | `2026-05-07` |

## Цель

Документировать Doxygen-блоками оставшиеся runtime-модули, которые не вошли в phase 1: `module_core_runtime` (read_model, verification, file_local_contracts, query_cli), `install_global_skill.py`, и внутренние хелперы workflow/install runtime.

## Границы

### Входит

- Добавление Doxygen-блоков к классам и функциям в:
  - `scripts/module_core_runtime/read_model.py`
  - `scripts/module_core_runtime/verification.py`
  - `scripts/module_core_runtime/file_local_contracts.py`
  - `scripts/module_core_runtime/query_cli.py`
  - `scripts/install_global_skill.py`
  - `scripts/task_workflow_runtime/git_ops.py`
  - `scripts/task_workflow_runtime/registry_sync.py`
  - `scripts/task_workflow_runtime/task_markdown.py`
  - `scripts/task_workflow_runtime/path_safety.py`
  - `scripts/task_workflow_runtime/forge.py`
  - `scripts/task_workflow_runtime/legacy_upgrade.py`
  - `scripts/task_workflow_runtime/read_model.py`
  - `scripts/task_workflow_runtime/query_cli.py`
- Обеспечение `make docs-check` без warnings после изменений.
- Обеспечение `make check` зелёным.

### Не входит

- Изменение логики модулей.
- Добавление новых зависимостей.
- Документирование `tests/`.

## Контекст

- источник постановки: продолжение TASK-2026-0048 phase 1.
- связанная бизнес-область: developer experience, code maintainability.
- ограничения и зависимости: должна выполняться в той же ветке, что и родитель.
- исходный наблюдаемый симптом / лог-маркер: `не требуется`
- основной контекст сессии: `подзадача TASK-2026-0048`

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | Добавление Doxygen-блоков перед функциями/классами в оставшихся модулях. |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0048-doxygen-integration/subtasks/TASK-2026-0048.1-doxygen-phase-2-module-core-and-helpers/`
- файл плана: `plan.md`
- родительская задача: `knowledge/tasks/TASK-2026-0048-doxygen-integration/task.md`

## Контур публикации

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | `—` | `—` | `—` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |

## Текущий этап

Реализация завершена. Все целевые модули покрыты Doxygen-блоками. `make docs-check` clean, `make check` зелёный. Результат зафиксирован в git.

## Стратегия проверки

### Покрывается кодом или тестами

- `make docs-check` — генерация без warnings.
- `make check` — компиляция и тесты.

### Остаётся на ручную проверку

- Визуальная проверка HTML-вывода для новых модулей.

## Критерии готовности

- Все перечисленные модули покрыты Doxygen-блоками.
- `make docs-check` clean.
- `make check` зелёный.

## Итоговый список ручных проверок

- Визуальная проверка HTML-вывода для module_core_runtime.

## Итог

Добавлено ~970 строк Doxygen-документации в 13 файлов:
- `scripts/module_core_runtime/read_model.py` — 11 классов + 8 функций + 7 внутренних helpers
- `scripts/module_core_runtime/verification.py` — 8 классов + 4 функции
- `scripts/module_core_runtime/file_local_contracts.py` — 6 классов + 2 функции
- `scripts/module_core_runtime/query_cli.py` — 5 функций
- `scripts/install_global_skill.py` — 3 класса + 27 функций
- `scripts/task_workflow_runtime/git_ops.py` — 18 функций
- `scripts/task_workflow_runtime/path_safety.py` — 2 функции
- `scripts/task_workflow_runtime/forge.py` — 3 класса + 3 функции
- `scripts/task_workflow_runtime/legacy_upgrade.py` — 2 класса + 14 функций
- `scripts/task_workflow_runtime/registry_sync.py` — 34 функции
- `scripts/task_workflow_runtime/task_markdown.py` — 19 функций
- `scripts/task_workflow_runtime/read_model.py` — 6 классов + 37 функций
- `scripts/task_workflow_runtime/query_cli.py` — 10 функций

Проверки: `make docs-check` clean, `make check` — 260 tests OK.
Commit: `TASK-2026-0048.1: add Doxygen blocks to module_core_runtime, install_global_skill, and task_workflow_runtime helpers`.
