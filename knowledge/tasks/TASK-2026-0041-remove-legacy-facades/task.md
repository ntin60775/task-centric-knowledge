# Карточка задачи TASK-2026-0041

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0041` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0041` |
| Технический ключ для новых именуемых сущностей | `—` |
| Краткое имя | `remove-legacy-facades` |
| Человекочитаемое описание | Удаление legacy-фасадов и перевод всего контура на unified CLI. |
| Статус | `в работе` |
| Приоритет | `высокий` |
| Ответственный | `Kimi Code CLI` |
| Ветка | `task/task-2026-0041-remove-legacy-facades` |
| Требуется SDD | `да` |
| Статус SDD | `черновик` |
| Ссылка на SDD | `sdd.md` |
| Дата создания | `2026-05-06` |
| Дата обновления | `2026-05-06` |

## Цель

Удалить три legacy-фасада (`scripts/install_skill.py`, `scripts/task_workflow.py`, `scripts/task_query.py`), legacy-режим `--mode` в unified CLI, и перевести все references, adoption, README и Makefile на использование `task-knowledge` как единственного entrypoint. Весь операторский контур должен работать через `task-knowledge <command>` без обратной совместимости с facade-скриптами.

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

- Поле `Ветка` хранит текущую активную ветку рабочего контекста, а не обязательную долгоживущую task-ветку.
- При открытии верхнеуровневой задачи стартовый контекст синхронизируется в `task/task-2026-0041-remove-legacy-facades`.
- При каждом создании или переключении ветки нужно синхронизировать это поле и строку в `registry.md`.

## Границы

### Входит

- Удаление `scripts/install_skill.py` (60 строк facade).
- Удаление `scripts/task_workflow.py` (31 строка facade).
- Удаление `scripts/task_query.py` (18 строк facade).
- Удаление legacy-ветки `--mode` из `task_knowledge_cli.py` (функция `_run_legacy_install_cli` и вызов `main(argv, script_path=...)` в `scripts/install_skill_runtime/cli.py`).
- Обновление `pyproject.toml`: удаление `install_skill`, `task_query`, `task_workflow` из `py-modules`.
- Обновление `references/adoption.md`: замена всех вызовов `python3 scripts/install_skill.py`, `python3 scripts/task_workflow.py`, `python3 scripts/task_query.py` на `task-knowledge ...`.
- Обновление `references/deployment.md`: замена facade-вызовов на unified CLI.
- Обновление `references/task-workflow.md`: замена facade-вызовов на unified CLI.
- Обновление `references/task-routing.md`: при необходимости.
- Обновление `references/upgrade-transition.md`: при необходимости.
- Обновление `references/consumer-runtime-v1.md`: при необходимости.
- Обновление `README.md`: удаление упоминаний facade-скриптов.
- Обновление `Makefile`: цели, использующие facade-скрипты.
- Обновление `SKILL.md`: при необходимости.
- Проверка, что `scripts/install_skill_runtime/cli.py` всё ещё нужен для output-форматирования (его использует unified CLI).
- Обновление тестов: если тесты напрямую импортируют facade-скрипты.

### Не входит

- Изменение runtime-модулей (`install_skill_runtime/`, `task_workflow_runtime/`, `module_core_runtime/`, `borrowings_runtime/`) — они остаются нетронутыми.
- Изменение unified CLI логики (кроме удаления legacy-ветки `--mode`).
- Изменение `scripts/install_global_skill.py`.
- Рефакторинг внутренней архитектуры runtime-модулей (это задача TASK-2026-0042).

## Контекст

- источник постановки: плановая очистка архитектуры после завершения rollout unified CLI (TASK-2026-0037, TASK-2026-0040).
- связанная бизнес-область: операторский контур `task-centric-knowledge`.
- ограничения и зависимости: задача должна выполняться после TASK-2026-0042 (нормализация package layout), чтобы не приходилось дважды править import-ы. Если TASK-2026-0042 ещё не сделана, нужно сначала выполнить её.
- исходный наблюдаемый симптом / лог-маркер: `не требуется`
- основной контекст сессии: `текущая задача`

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | Удаление 3 facade-файлов, удаление legacy-ветки в unified CLI, обновление pyproject.toml |
| Конфигурация / схема данных / именуемые сущности | `pyproject.toml`: `py-modules` |
| Интерфейсы / формы / страницы | `Makefile` цели |
| Интеграции / обмены | `references/adoption.md`, `references/deployment.md`, `references/task-workflow.md` |
| Документация | `README.md`, `SKILL.md`, `references/*.md`, `Makefile` |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0041-remove-legacy-facades/`
- файл плана: `plan.md`
- файл SDD: `sdd.md`
- файл verification matrix: `artifacts/verification-matrix.md`
- канонический нормативный contract: `references/core-model.md`
- связанные операции в `knowledge/operations/`: `task-centric-knowledge-upgrade.md`

## Контур публикации

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | — | `—` | `—` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |

## Текущий этап

Спецификация и планирование. Документация задачи подготовлена, ожидается утверждение плана и SDD.

## Стратегия проверки

### Покрывается кодом или тестами

- `python3 -m unittest discover -s tests -v` — полный тестовый прогон после удаления facade-ов.
- `make install-local` — проверка, что `task-knowledge` устанавливается и работает.
- `task-knowledge --help` — проверка, что unified CLI функционирует.
- `task-knowledge doctor --project-root .` — проверка окружения.
- `task-knowledge install check --project-root .` — проверка install-контура.
- `task-knowledge task status --project-root .` — проверка read-model.
- `task-knowledge workflow sync --project-root . --task-dir knowledge/tasks/TASK-2026-0041-remove-legacy-facades --register-if-missing` — проверка workflow.
- `git diff --check` — отсутствие синтаксических ошибок.
- `make check` — обязательный source gate.
- `python3 -m ruff check scripts/ tests/` — линтинг.
- Доказательство покрытия `artifacts/verification-matrix.md`.

### Остаётся на ручную проверку

- Визуальная проверка, что все references используют `task-knowledge` вместо facade-скриптов.
- Проверка, что `make install-global` и `make verify-global-install` всё ещё работают.

## Критерии готовности

- Все три facade-файла удалены.
- `pyproject.toml` не ссылается на удалённые facade-модули.
- Все references (`adoption.md`, `deployment.md`, `task-workflow.md`, `consumer-runtime-v1.md`, `upgrade-transition.md`) используют `task-knowledge` вместо facade-скриптов.
- `README.md` и `SKILL.md` не упоминают facade-скрипты как действующий операторский интерфейс.
- `Makefile` цели используют `task-knowledge`, а не facade-скрипты.
- Legacy-ветка `--mode` удалена из unified CLI.
- Полный тестовый прогон зелёный.
- `make check` проходит.
- `make install-local` работает, `task-knowledge --help` доступен.
- `scripts/install_skill_runtime/cli.py` сохранён (его использует unified CLI для форматирования вывода).

## Итоговый список ручных проверок

- Проверка references на отсутствие facade-скриптов.
- Проверка `make install-global` и `make verify-global-install`.

## Итог

Заполняется при завершении или передаче.
