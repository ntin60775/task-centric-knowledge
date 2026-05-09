# План задачи TASK-2026-0048.1

## Правило

Для задачи существует только один файл плана: `plan.md`.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0048.1` |
| Parent ID | `TASK-2026-0048` |
| Версия плана | `1` |
| Связь с SDD | `—` |
| Дата обновления | `2026-05-07` |

## Цель

Документировать Doxygen-блоками оставшиеся runtime-модули, не вошедшие в phase 1.

## Границы

### Входит

- Документирование `module_core_runtime` (read_model, verification, file_local_contracts, query_cli).
- Документирование `install_global_skill.py`.
- Документирование внутренних хелперов workflow и install runtime.
- Проверка `make docs-check` и `make check`.

### Не входит

- Изменение логики.
- Добавление зависимостей.
- Документирование `tests/`.

## Планируемые изменения

### Код

- Добавить Doxygen-блоки ко всем классам и публичным функциям в целевых модулях.

## Зависимости и границы

### Новые runtime/package зависимости

`нет`

### Границы, которые должны остаться изолированными

- `tests/` — не трогать.
- `assets/`, `references/`, `knowledge/` — не трогать.

### Критический функционал

- `make docs-check` clean.
- `make check` зелёный.

### Основной сценарий

1. Документировать `module_core_runtime/read_model.py`.
2. Документировать `module_core_runtime/verification.py`.
3. Документировать `module_core_runtime/file_local_contracts.py`.
4. Документировать `module_core_runtime/query_cli.py`.
5. Документировать `install_global_skill.py`.
6. Документировать внутренние хелперы workflow/install.
7. Прогнать `make docs-check` и `make check`.
8. Зафиксировать результат в git.

## Проверки

### Что можно проверить кодом или тестами

- `make docs-check` — clean.
- `make check` — компиляция + тесты.

### Что остаётся на ручную проверку

- Визуальная проверка HTML-вывода.

## Шаги

- [x] Шаг 1: Документировать `scripts/module_core_runtime/read_model.py`.
- [x] Шаг 2: Документировать `scripts/module_core_runtime/verification.py`.
- [x] Шаг 3: Документировать `scripts/module_core_runtime/file_local_contracts.py`.
- [x] Шаг 4: Документировать `scripts/module_core_runtime/query_cli.py`.
- [x] Шаг 5: Документировать `scripts/install_global_skill.py`.
- [x] Шаг 6: Документировать внутренние хелперы workflow/install (`git_ops.py`, `registry_sync.py`, `task_markdown.py`, `path_safety.py`, `forge.py`, `legacy_upgrade.py`, `read_model.py`, `query_cli.py`).
- [x] Шаг 7: Прогнать `make docs-check` и устранить warnings.
- [x] Шаг 8: Прогнать `make check`.
- [x] Шаг 9: Сделать task-scoped commit.

## Критерии завершения

- Все целевые модули покрыты Doxygen-блоками.
- `make docs-check` clean.
- `make check` зелёный.
