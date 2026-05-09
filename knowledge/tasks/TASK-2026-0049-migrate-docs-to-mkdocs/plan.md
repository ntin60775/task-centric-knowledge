# План задачи TASK-2026-0049

## Правило

Для задачи существует только один файл плана: `plan.md`.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0049` |
| Parent ID | `—` |
| Версия плана | `1` |
| Связь с SDD | `sdd.md` |
| Дата обновления | `2026-05-07` |

## Цель

Мигрировать документационную инфраструктуру с Doxygen на mkdocstrings + MkDocs с сохранением полноты покрытия и проверяемости.

## Границы

### Входит

- Создание `mkdocs.yml`, `scripts/check_doc_coverage.py`.
- Переписывание Doxygen → Google-style docstrings во всех `scripts/`.
- Обновление `Makefile`, `pyproject.toml`, `.gitignore`.
- Удаление `Doxyfile` и Doxygen-целей.

### Не входит

- Изменение логики.
- Документирование `tests/`.
- Внешний hosting.

## Планируемые изменения

### Код

- Создать `scripts/check_doc_coverage.py` (Griffe-based).
- Переписать docstrings: `scripts/module_core_runtime/*`, `scripts/install_global_skill.py`, `scripts/task_workflow_runtime/*`, `scripts/install_skill_runtime/*`, `scripts/borrowings_runtime/*`, `scripts/task_knowledge_cli.py`.

### Конфигурация

- Создать `mkdocs.yml`.
- Удалить `Doxyfile`.
- Обновить `Makefile` (убрать `docs`, `docs-check` для Doxygen; добавить для mkdocs).
- Обновить `pyproject.toml` (dev-зависимости).
- Обновить `.gitignore`.

## Зависимости и границы

### Новые runtime/package зависимости

`mkdocs`, `mkdocstrings[python]`, `griffe` — dev-dependencies.

### Границы, которые должны остаться изолированными

- `tests/` — не трогать.
- `knowledge/` (кроме каталога задачи) — не трогать.
- `assets/`, `references/` — не трогать без явной необходимости.

### Критический функционал

- `make docs-check` clean.
- `make docs-coverage` — 0 пропущенных public API.
- `make check` зелёный.

### Основной сценарий

1. Создать `mkdocs.yml` и прототип сборки.
2. Написать `scripts/check_doc_coverage.py`.
3. Мигрировать `scripts/module_core_runtime/` (4 файла).
4. Мигрировать `scripts/install_global_skill.py`.
5. Мигрировать `scripts/task_workflow_runtime/` (8 файлов).
6. Мигрировать оставшиеся `scripts/` (phase 1 модули).
7. Обновить `Makefile`, `pyproject.toml`, `.gitignore`.
8. Удалить `Doxyfile`.
9. Прогнать `make docs-check`, `make docs-coverage`, `make check`.
10. Зафиксировать результат в git.

## Проверки

### Что можно проверить кодом или тестами

- `make docs-check` — clean.
- `make docs-coverage` — Griffe checker.
- `make check` — 260 тестов.
- `grep -r "## @brief" scripts/` — 0 результатов.

### Что остаётся на ручную проверку

- Визуальный осмотр HTML (`mkdocs serve`).
- Читаемость Markdown API.

## Шаги

- [ ] Шаг 1: Создать `mkdocs.yml` и проверить прототип сборки на 1 файле.
- [ ] Шаг 2: Написать `scripts/check_doc_coverage.py` (Griffe-based).
- [ ] Шаг 3: Мигрировать `scripts/module_core_runtime/read_model.py`.
- [ ] Шаг 4: Мигрировать `scripts/module_core_runtime/verification.py`.
- [ ] Шаг 5: Мигрировать `scripts/module_core_runtime/file_local_contracts.py`.
- [ ] Шаг 6: Мигрировать `scripts/module_core_runtime/query_cli.py`.
- [ ] Шаг 7: Мигрировать `scripts/install_global_skill.py`.
- [ ] Шаг 8: Мигрировать `scripts/task_workflow_runtime/` (8 файлов).
- [ ] Шаг 9: Мигрировать оставшиеся `scripts/` (phase 1 модули).
- [ ] Шаг 10: Обновить `Makefile`, `pyproject.toml`, `.gitignore`; удалить `Doxyfile`.
- [ ] Шаг 11: Прогнать `make docs-check`, `make docs-coverage`, `make check`.
- [ ] Шаг 12: Сделать task-scoped commit.

## Критерии завершения

- Все целевые модули покрыты Google-style docstrings.
- `Doxyfile` удалён.
- `make docs-check` clean.
- `make docs-coverage` показывает 100% public API.
- `make check` зелёный.
