# Verification Matrix: TASK-2026-0049

## Методология

Каждая строка — инвариант, сценарий нарушения, проверяемая команда и статус покрытия.

## Матрица

| ID | Инвариант | Сценарий нарушения | Проверка / Команда | Статус |
|----|-----------|-------------------|-------------------|--------|
| V-01 | `Doxyfile` удалён из репозитория | Файл всё ещё существует в корне | `test ! -f Doxyfile` | покрыт |
| V-02 | Doxygen-цели удалены из `Makefile` | `make docs` или `make docs-check` вызывает `doxygen` | `grep -i doxygen Makefile` должно вернуть пусто | покрыт |
| V-03 | В `scripts/` не осталось Doxygen-блоков | `## @brief`, `#  @param`, `#  @return` присутствуют | `grep -rE "^## @brief|^#  @param|^#  @return" scripts/` — 0 строк | покрыт |
| V-04 | Все public функции имеют docstrings | Функция в `__all__` или без `_` prefix без docstring | `python3 scripts/check_doc_coverage.py scripts/` — exit 0 | покрыт |
| V-05 | Все public классы имеют docstrings | Класс без `_` prefix без docstring | `python3 scripts/check_doc_coverage.py scripts/` — exit 0 | покрыт |
| V-06 | mkdocs.yml валиден и сборка проходит | `mkdocs build` падает с ошибкой | `mkdocs build --strict` — exit 0 | покрыт |
| V-07 | `make docs-check` clean | Сборка или coverage checker падает | `make docs-check` — exit 0 | покрыт |
| V-08 | `make docs-coverage` показывает 100% public API | coverage checker находит пропуски | `make docs-coverage` — exit 0 | покрыт |
| V-09 | `make check` зелёный | Unit tests ломаются из-за миграции | `python3 -m unittest discover -s tests` — OK | покрыт |
| V-10 | `.gitignore` исключает сгенерированные docs | `output/docs/site/` или `output/docs/api/` попадают в git | `git check-ignore output/docs/site/` — exit 0 | покрыт |
| V-11 | pyproject.toml содержит dev-зависимости | `mkdocs`, `mkdocstrings`, `griffe` отсутствуют | `grep -E "mkdocs|mkdocstrings|griffe" pyproject.toml` | покрыт |
| V-12 | AGENTS.md / SKILL.md не ссылаются на Doxygen | Остались stale references | `grep -i doxygen AGENTS.md SKILL.md` — 0 или обновлено | покрыт |
| V-13 | Формат docstrings — Google-style | Присутствуют reST-style (`:param:`) или mixed | Ручная выборочная проверка + flake8-docstrings | покрыт |

## Ручной остаток

- [x] Визуальная проверка HTML-вывода (`mkdocs serve`).
- [x] Проверка читаемости Markdown API-референса в `output/docs/api/`.
