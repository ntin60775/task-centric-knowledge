# План задачи TASK-2026-0048

## Правило

Для задачи существует только один файл плана: `plan.md`.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0048` |
| Parent ID | `—` |
| Версия плана | `1` |
| Связь с SDD | `—` |
| Дата обновления | `2026-05-07` |

## Цель

Настроить Doxygen для Python-кода проекта, интегрировать генерацию документации в Makefile и покрыть комментариями public API runtime-модулей.

## Границы

### Входит

- Создание `Doxyfile` для Python-кода (HTML + XML вывод).
- Настройка `output/doxygen/` как директории для артефактов.
- Обновление `.gitignore`.
- Добавление `docs` и `docs-check` в `Makefile`.
- Документирование public API в `scripts/` (phase 1 и phase 2).
- Проверка отсутствия warnings в `make docs-check`.

### Не входит

- Документирование `tests/`.
- Документирование Markdown-артефактов.
- Переход на другой документирующий инструмент.
- Изменение логики модулей.

## Планируемые изменения

### Код

- Добавить Doxygen-блоки перед функциями/классами в public API модулях:
  - `scripts/task_knowledge_cli.py`
  - `scripts/task_knowledge/__main__.py`
  - `scripts/task_workflow_runtime/sync_flow.py`
  - `scripts/task_workflow_runtime/models.py`
  - `scripts/task_workflow_runtime/cli.py`
  - `scripts/install_skill_runtime/models.py`
  - `scripts/module_core_runtime/read_model.py`
  - и другие ключевые модули по мере необходимости
- Добавить минимальные fallback docstrings внутри функций для Python introspection.

### Конфигурация / схема данных / именуемые сущности

- `Doxyfile`: Python-настройки (`OPTIMIZE_OUTPUT_JAVA`, `PYTHON_DOCSTRING`, `EXTENSION_MAPPING`, `FILE_PATTERNS`, `RECURSIVE`).
- `.gitignore`: исключить `output/doxygen/`.

### Документация

- `AGENTS.md` — проверить, не требуется ли обновление managed-блоков.

## Зависимости и границы

### Новые runtime/package зависимости

`нет`

### Изменения import/module-связей и зависимостей между модулями

`нет`

### Границы, которые должны остаться изолированными

- `tests/` — не документировать в рамках этой задачи.
- `assets/`, `references/`, `knowledge/` — не трогать.
- `make check` — не добавлять в него docs-генерацию.

### Критический функционал

- `make docs` генерирует HTML/XML.
- `make docs-check` проходит без warnings.
- `make check` остаётся зелёным.

### Основной сценарий

1. Создать `Doxyfile` с Python-настройками.
2. Добавить `output/doxygen/` в `.gitignore`.
3. Добавить `docs` и `docs-check` в `Makefile`.
4. Прогнать `make docs-check` и убедиться, что нет warnings.
5. Добавить Doxygen-блоки к public API (phase 1: `@brief`, `@param`, `@return`, `@raises`).
6. Добавить Doxygen-блоки к key internal функциям (phase 2: `@note`, `@todo`, `@pre`, `@post`, `@see`).
7. Прогнать `make check`.
8. Зафиксить результат в git.

### Исходный наблюдаемый симптом

`не требуется`

## Риски и зависимости

- **Doxygen не установлен** в среде — задача может выполняться только конфигурацией и комментариями, без финальной проверки `make docs-check`.
- **Регрессия `make check`** — добавление комментариев не должно ломать компиляцию или тесты.
- **Объём работы** — 56 Python-файлов; покрытие всех за один проход может быть избыточным. Приоритет — public API.

## Проверки

### Что можно проверить кодом или тестами

- `make docs-check` — генерация без warnings.
- `make check` — компиляция и тесты.
- `git diff --check`.

### Что остаётся на ручную проверку

- Визуальная проверка HTML-вывода.
- Проверка полноты покрытия public API.

## Шаги

- [x] Шаг 1: Создать `Doxyfile` с Python-настройками (HTML + XML).
- [x] Шаг 2: Добавить `output/doxygen/` в `.gitignore`.
- [x] Шаг 3: Добавить `docs` и `docs-check` в `Makefile`.
- [ ] Шаг 4: Прогнать `make docs-check` и устранить warnings (блокируется: `doxygen` не установлен).
- [x] Шаг 5: Добавить Doxygen-блоки phase 1 к public API (`scripts/task_knowledge_cli.py`, `scripts/task_workflow_runtime/`, `scripts/install_skill_runtime/`, `scripts/borrowings_runtime/`).
- [ ] Шаг 6: Добавить Doxygen-блоки phase 2 к key internal функциям (`@note`, `@todo`, `@see`).
- [ ] Шаг 7: Добавить минимальные fallback docstrings внутри функций (частично: добавлены для dataclasses и key функций).
- [x] Шаг 8: Прогнать `make check`.
- [x] Шаг 9: Обновить `AGENTS.md` при необходимости (изменений не потребовалось).
- [x] Шаг 10: Сделать task-scoped commit.

## Критерии завершения

- `Doxyfile` создан и валиден.
- `make docs` и `make docs-check` работают.
- Public API покрыт Doxygen-блоками.
- `make check` зелёный.
- `.gitignore` обновлён.
