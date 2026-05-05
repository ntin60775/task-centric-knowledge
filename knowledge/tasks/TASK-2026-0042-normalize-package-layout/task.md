# Карточка задачи TASK-2026-0042

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0042` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0042` |
| Технический ключ для новых именуемых сущностей | `—` |
| Краткое имя | `normalize-package-layout` |
| Человекочитаемое описание | Нормализация package layout — перевод runtime-модулей в `src/task_knowledge/`. |
| Статус | `готова к работе` |
| Приоритет | `высокий` |
| Ответственный | `не назначен` |
| Ветка | `task/task-2026-0042-normalize-package-layout` |
| Требуется SDD | `да` |
| Статус SDD | `черновик` |
| Ссылка на SDD | `sdd.md` |
| Дата создания | `2026-05-06` |
| Дата обновления | `2026-05-06` |

## Цель

Перевести все runtime-модули из `scripts/` в стандартную структуру `src/task_knowledge/`, привести `pyproject.toml` к стандартному Python package layout и обновить все import-ы и конфигурацию инструментов. Целевая структура: Python package `task_knowledge` в `src/task_knowledge/` со всеми runtime-подмодулями (`install`, `workflow`, `query`, `module_core`, `borrowings`, `version`), CLI entrypoint в `src/task_knowledge/cli.py`, и `scripts/` только для shell-скриптов и глобального installer.

## Подсказка по статусу

- `черновик` — задача в процессе начального анализа, плана или спецификации.
- `готова к работе` — план утверждён, SDD готов, можно начинать реализацию.
- `в работе` — активная реализация.
- `на проверке` — ожидание review или тестирования.
- `ждёт пользователя` — ожидание решения или ввода пользователя.
- `заблокирована` — блокирована внешним фактором.
- `завершена` — задача закрыта, все delivery units в `merged` или `closed`.
- `отменена` — задача отменена.

## Git-подсказка

## Границы

### Входит

- Создание структуры `src/task_knowledge/` как корня Python package.
- Перенос `scripts/task_knowledge/` (пакет: `__init__.py`, `__main__.py`, `version.py`) в `src/task_knowledge/`.
- Перенос `scripts/task_knowledge_cli.py` в `src/task_knowledge/cli.py`.
- Перенос `scripts/install_skill_runtime/` в `src/task_knowledge/install_runtime/` (или `install/`).
- Перенос `scripts/task_workflow_runtime/` в `src/task_knowledge/workflow_runtime/` (или `workflow/`).
- Перенос `scripts/module_core_runtime/` в `src/task_knowledge/module_core_runtime/` (или `module_core/`).
- Перенос `scripts/borrowings_runtime/` в `src/task_knowledge/borrowings_runtime/` (или `borrowings/`).
- Обновление всех внутренних import-ов между runtime-модулями.
- Обновление `pyproject.toml`: `package-dir` на `src`, `packages.find` на `src`.
- Обновление `tool.ruff.src` и `tool.mypy.files` на `src`.
- Обновление `Makefile` и `scripts/install_global_skill.py` для новых путей.
- Обновление references (`deployment.md`, `adoption.md`, etc.) при необходимости.
- Обновление тестов: пути импорта.
- Обновление `AGENTS.md` (managed-блоки) если они ссылаются на пути в `scripts/`.
- Создание `src/task_knowledge/` с правильным `__init__.py`.

### Не входит

- Изменение логики runtime-модулей.
- Удаление facade-скриптов (это TASK-2026-0041, следует выполнять после).
- Изменение `scripts/install_global_skill.py` логики (только пути).
- Изменение `assets/`, `references/`, `knowledge/`.
- Добавление новых зависимостей.

## Контекст

- источник постановки: плановая нормализация структуры проекта к стандартному Python package layout с src-layout.
- связанная бизнес-область: инфраструктура проекта, developer experience.
- ограничения и зависимости: должна выполняться перед TASK-2026-0041 (удаление facade-ов), так как после нормализации путей удаление facade-ов будет проще. Фасады (`install_skill.py`, `task_workflow.py`, `task_query.py`) на этом этапе можно либо перенести, либо оставить как forwarding-обёртки, либо удалить (рекомендуется удалить вместе с TASK-2026-0041 после данной задачи).
- исходный наблюдаемый симптом / лог-маркер: `не требуется`
- основной контекст сессии: `текущая задача`

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | Перенос всех runtime-модулей из `scripts/` в `src/task_knowledge/`, обновление всех import-ов |
| Конфигурация / схема данных / именуемые сущности | `pyproject.toml`: `package-dir`, `packages.find`, `py-modules`, `ruff.src`, `mypy.files` |
| Интерфейсы / формы / страницы | `Makefile` цели, `scripts/install_global_skill.py` пути |
| Интеграции / обмены | `scripts/check-docs-localization.sh`, `AGENTS.md` managed-блоки |
| Документация | `references/deployment.md`, `README.md`, `SKILL.md` |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0042-normalize-package-layout/`
- файл плана: `plan.md`
- файл SDD: `sdd.md`
- файл verification matrix: `artifacts/verification-matrix.md`
- канонический нормативный contract: `pyproject.toml`

## Контур публикации

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | — | `—` | `—` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |

## Текущий этап

Спецификация и планирование. Документация задачи подготовлена.

## Стратегия проверки

### Покрывается кодом или тестами

- `python3 -m unittest discover -s tests -v` — полный тестовый прогон.
- `make check` — обязательный source gate.
- `python3 -m ruff check src/ tests/` — линтинг.
- `python3 -m mypy src/` — проверка типов.
- `make install-local` — установка CLI layer из `src/`.
- `task-knowledge --help` — проверка работы CLI.
- `task-knowledge doctor --project-root .` — проверка окружения.
- `git diff --check`.
- Доказательство покрытия `artifacts/verification-matrix.md`.

### Остаётся на ручную проверку

- Визуальная проверка структуры `src/task_knowledge/` на полноту.
- Проверка `make install-global` и `make verify-global-install`.

## Критерии готовности

- Все runtime-модули перенесены в `src/task_knowledge/`.
- `pyproject.toml` настроен на `src/` layout.
- Все import-ы обновлены и работают.
- `make check` зелёный.
- Полный тестовый прогон зелёный.
- `make install-local` и `task-knowledge --help` работают.
- `ruff` и `mypy` (если доступны) проходят.
- Verification matrix покрыта.

## Итоговый список ручных проверок

- Визуальная проверка структуры `src/task_knowledge/`.
- Проверка глобальной установки.

## Итог

Заполняется при завершении или передаче.
