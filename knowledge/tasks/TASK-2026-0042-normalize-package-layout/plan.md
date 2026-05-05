# План задачи TASK-2026-0042

## Правило

Для задачи существует только один файл плана: `plan.md`.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0042` |
| Parent ID | `—` |
| Версия плана | `1` |
| Связь с SDD | `sdd.md` |
| Дата обновления | `2026-05-06` |

## Цель

Перевести runtime-модули в `src/task_knowledge/` со стандартным Python src-layout.

## Границы

### Входит

- Создание `src/task_knowledge/` пакета.
- Перенос всех runtime-модулей из `scripts/` в `src/task_knowledge/`.
- Обновление всех import-ов.
- Обновление `pyproject.toml`, `Makefile`, `install_global_skill.py`.
- Обновление конфигурации ruff/mypy.
- Обновление references и managed-блоков.

### Не входит

- Изменение логики runtime-модулей.
- Удаление facade-скриптов (TASK-2026-0041).
- Добавление новых зависимостей.

## Планируемые изменения

### Код

- Создать `src/task_knowledge/__init__.py` (публичный API пакета).
- Перенести `scripts/task_knowledge/` → `src/task_knowledge/` (пакетные файлы).
- Перенести `scripts/task_knowledge_cli.py` → `src/task_knowledge/cli.py`.
- Перенести `scripts/install_skill_runtime/` → `src/task_knowledge/install_runtime/`.
- Перенести `scripts/task_workflow_runtime/` → `src/task_knowledge/workflow_runtime/`.
- Перенести `scripts/module_core_runtime/` → `src/task_knowledge/module_core_runtime/`.
- Перенести `scripts/borrowings_runtime/` → `src/task_knowledge/borrowings_runtime/`.
- Обновить import-ы: `from install_skill_runtime` → `from task_knowledge.install_runtime`, и аналогично всем runtime-модулям.
- Обновить `scripts/install_global_skill.py`: пути к runtime-файлам.

### Конфигурация / схема данных / именуемые сущности

- `pyproject.toml`: `package-dir = {"" = "src"}`, `packages.find.where = ["src"]`, `py-modules` (зависит от статуса facade-ов).
- `tool.ruff.src = ["src", "tests"]`.
- `tool.mypy.files = ["src"]`.

### Документация

- `references/deployment.md` — пути к `scripts/`.
- `README.md` — примеры путей.
- `AGENTS.md` managed-блоки — проверка на упоминания `scripts/`.

## Зависимости и границы

### Новые runtime/package зависимости

`нет`

### Изменения import/module-связей и зависимостей между модулями

- Массовое: все runtime-модули переезжают под `task_knowledge.*`.
- Импорты между runtime-модулями: `from install_skill_runtime.X` → `from task_knowledge.install_runtime.X`.
- CLI: `from task_knowledge_cli` → `from task_knowledge.cli`.
- `__main__.py`: импорт `main` из `task_knowledge.cli`.

### Границы, которые должны остаться изолированными

- `scripts/` после переноса содержит только shell-скрипты и `install_global_skill.py`.
- `assets/`, `references/`, `knowledge/` не трогаются.
- Внешние проекты, импортирующие `task_knowledge`, не должны сломаться (обратная совместимость через re-export при необходимости).

### Критический функционал

- `task-knowledge` CLI работает как прежде.
- `make install-local` устанавливает CLI.
- `make install-global` обновляет live-copy и CLI.
- Все тесты проходят.

### Основной сценарий

1. Создать `src/task_knowledge/` структуру.
2. Перенести модули.
3. Обновить import-ы.
4. Обновить `pyproject.toml`.
5. Обновить `Makefile` и `install_global_skill.py`.
6. Прогнать тесты.
7. Обновить документацию.

### Исходный наблюдаемый симптом

`не требуется`

## Риски и зависимости

- **Циклические импорты**: при переносе могут возникнуть циклические зависимости.
- **Совместимость с facade-ами**: если TASK-2026-0041 ещё не выполнена, facade-скрипты нужно либо обновить, либо удалить.
- **Тесты**: многие тесты используют прямые импорты из `scripts/`.
- **Глобальная установка**: `install_global_skill.py` копирует `scripts/` в live-copy, нужно обновить пути.

## Связь с SDD

- SDD: `sdd.md` — инварианты, архитектура переноса, карта модулей.
- Verification matrix: `artifacts/verification-matrix.md`.
- Этапы SDD:
  1. Создание структуры `src/task_knowledge/`.
  2. Перенос runtime-модулей с обновлением import-ов.
  3. Обновление конфигурации (`pyproject.toml`, `ruff`, `mypy`).
  4. Обновление скриптов (`Makefile`, `install_global_skill.py`).
  5. Обновление references и тестов.
  6. Финальная верификация.

## Проверки

### Что можно проверить кодом или тестами

- `python3 -m unittest discover -s tests -v` — полный тестовый прогон.
- `make check` — source gate.
- `python3 -m ruff check src/ tests/` — линтинг.
- `python3 -m mypy src/` — типизация.
- `make install-local` — установка CLI.
- `task-knowledge --help` — проверка CLI.
- `task-knowledge doctor --project-root .` — проверка окружения.
- Доказательство покрытия `artifacts/verification-matrix.md`.

### Что остаётся на ручную проверку

- Визуальная проверка структуры `src/task_knowledge/`.
- `make install-global` и `make verify-global-install`.

## Шаги

- [ ] Шаг 1: Создать `src/task_knowledge/` пакет с `__init__.py`.
- [ ] Шаг 2: Перенести `scripts/task_knowledge/` → `src/task_knowledge/`.
- [ ] Шаг 3: Перенести `scripts/task_knowledge_cli.py` → `src/task_knowledge/cli.py`.
- [ ] Шаг 4: Перенести `scripts/install_skill_runtime/` → `src/task_knowledge/install_runtime/`.
- [ ] Шаг 5: Перенести `scripts/task_workflow_runtime/` → `src/task_knowledge/workflow_runtime/`.
- [ ] Шаг 6: Перенести `scripts/module_core_runtime/` → `src/task_knowledge/module_core_runtime/`.
- [ ] Шаг 7: Перенести `scripts/borrowings_runtime/` → `src/task_knowledge/borrowings_runtime/`.
- [ ] Шаг 8: Обновить все import-ы в runtime-модулях.
- [ ] Шаг 9: Обновить `pyproject.toml`, `ruff`, `mypy` конфигурацию.
- [ ] Шаг 10: Обновить `Makefile` и `scripts/install_global_skill.py`.
- [ ] Шаг 11: Обновить тесты.
- [ ] Шаг 12: Обновить references и документацию.
- [ ] Шаг 13: Прогнать полный тестовый набор и проверки.
- [ ] Шаг 14: Доказать покрытие verification matrix.

## Критерии завершения

- Все runtime-модули в `src/task_knowledge/`.
- `pyproject.toml` настроен на `src` layout.
- Все импорты обновлены и работают.
- `make check` зелёный.
- Полный тестовый прогон зелёный.
- `make install-local` и `task-knowledge --help` работают.
