# Карточка задачи TASK-2026-0049

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0049` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0049` |
| Технический ключ для новых именуемых сущностей | `—` |
| Краткое имя | `migrate-docs-to-mkdocs` |
| Человекочитаемое описание | Миграция документационной инфраструктуры с Doxygen на mkdocstrings + MkDocs: Google-style docstrings, Griffe-based coverage, Markdown-native вывод. |
| Статус | `на проверке` |
| Приоритет | `средний` |
| Ответственный | `не назначен` |
| Ветка | `task/task-2026-0049-migrate-docs-to-mkdocs` |
| Требуется SDD | `да` |
| Статус SDD | `готов` |
| Ссылка на SDD | `sdd.md` |
| Дата создания | `2026-05-07` |
| Дата обновления | `2026-05-07` |

## Цель

Заменить Doxygen как инструмент генерации документации Python runtime на `mkdocstrings + MkDocs`, перевести все Doxygen-блоки в нативные Python docstrings (Google-style), обеспечить программную проверку покрытия через Griffe и сохранить воспроизводимый конвейер `make docs` / `make docs-check` / `make docs-coverage`.

## Границы

### Входит

- Удаление `Doxyfile` и очистка Doxygen-артефактов из `Makefile` / `.gitignore`.
- Создание `mkdocs.yml` с конфигурацией `mkdocstrings` (Griffe backend, Google-style).
- Переписывание всех Doxygen-блоков (`## @brief`, `#  @param` и т.д.) в Google-style docstrings во всех `scripts/`.
- Создание `scripts/check_doc_coverage.py` на базе Griffe для программной проверки покрытия public API.
- Интеграция `make docs-coverage` в `Makefile`.
- Обновление `pyproject.toml`: добавление `mkdocs`, `mkdocstrings[python]`, `griffe` в dev-зависимости.
- Обновление `.gitignore`: исключение `output/docs/site/` и `output/docs/api/`.
- Обновление `AGENTS.md` / `SKILL.md` если содержат упоминания Doxygen.

### Не входит

- Изменение логики runtime-модулей.
- Документирование `tests/`.
- Переход на Sphinx, pdoc или другой инструмент.
- Создание внешнего docs hosting / CI pipeline для публикации сайта.
- Изменение markdown-артефактов `references/` и `assets/` (кроме обновления cross-references при необходимости).

## Контекст

- источник постановки: обсуждение инфраструктуры документирования после завершения TASK-2026-0048.1.
- связанная бизнес-область: developer experience, code maintainability, agent readability.
- ограничения и зависимости: должна выполняться после вливания TASK-2026-0048 в `main`; требуется Python ≥ 3.10.
- исходный наблюдаемый симптом / лог-маркер: Doxygen неидиоматичен для Python; `## @brief` перед декораторами создаёт шум; нативные docstrings читаются через `inspect` без парсинга.
- основной контекст сессии: `текущая задача`

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | Все `scripts/*.py`: замена Doxygen-блоков на Google-style docstrings. Новый `scripts/check_doc_coverage.py`. |
| Конфигурация / схема данных / именуемые сущности | Удаление `Doxyfile`, создание `mkdocs.yml`, обновление `pyproject.toml`, `.gitignore`. |
| Интерфейсы / формы / страницы | `Makefile`: новые цели `docs`, `docs-check`, `docs-coverage`; удаление старых Doxygen-целей. |
| Документация | Сгенерированные Markdown (`output/docs/api/`) и HTML (`output/docs/site/`) не в git. |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0049-migrate-docs-to-mkdocs/`
- файл плана: `plan.md`
- спецификация: `sdd.md`
- матрица верификации: `artifacts/verification-matrix.md`
- канонический нормативный contract: `mkdocs.yml`

## Контур публикации

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `DU-1` | Миграция docs-инфраструктуры на mkdocstrings | `—` | `main` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |

## Текущий этап

Реализация завершена. Все проверки пройдены. Ожидает финального ревью и закрытия.

## Стратегия проверки

### Покрывается кодом или тестами

- `make docs-check` — сборка без warnings и ошибок.
- `make docs-coverage` — 100% покрытие public API docstrings (Griffe-based checker).
- `make check` — компиляция + unit tests (260 тестов).
- `python3 scripts/check_doc_coverage.py scripts/` — программная проверка отсутствия пустых docstrings у public API.
- `grep -r "## @brief" scripts/` — должно вернуть 0 совпадений (не осталось Doxygen-блоков).

### Остаётся на ручную проверку

- Визуальная проверка сгенерированного HTML (`make docs-serve` → localhost).
- Читаемость Markdown-вывода в `output/docs/api/`.

## Критерии готовности

- `Doxyfile` удалён, `mkdocs.yml` создан и валиден.
- Все Doxygen-блоки в `scripts/` переписаны в Google-style docstrings.
- `scripts/check_doc_coverage.py` проходит по всем модулям без ошибок.
- `make docs-check` clean.
- `make check` зелёный.
- `.gitignore` исключает `output/docs/`.

## Итоговый список ручных проверок

- [x] Визуальная проверка HTML-вывода MkDocs Material.
- [x] Проверка читаемости Markdown API-референса в `output/docs/api/`.

## Итог

Заполняется при завершении или передаче.
