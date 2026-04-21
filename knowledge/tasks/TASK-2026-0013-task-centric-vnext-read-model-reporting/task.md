# Карточка задачи TASK-2026-0013

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0013` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0013` |
| Технический ключ для новых именуемых сущностей | `vnext-read-model` |
| Краткое имя | `task-centric-vnext-read-model-reporting` |
| Человекочитаемое описание | `Операторский read-model слой status / current-task / task show поверх Task Core` |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `task/task-2026-0013-task-centric-vnext-read-model-reporting` |
| Требуется SDD | `да` |
| Статус SDD | `завершено` |
| Ссылка на SDD | `sdd.md` |
| Дата создания | `2026-04-12` |
| Дата обновления | `2026-04-13` |

## Цель

Реализовать операторский read-only слой `status`, `current-task` и `task show`,
который читает `Task Core`, но не становится новым источником истины и не дублирует смысл `task.md`.

## Границы

### Входит

- read-модель поверх `Task Core`;
- отдельный CLI-вход только для чтения `scripts/task_query.py`;
- runtime-модули `read_model.py` и `query_cli.py`;
- warnings при неоднозначности, drift и legacy-fallback;
- диагностика активной задачи, текущего этапа, следующего шага и открытых delivery units;
- unit и architecture-тесты read-model слоя;
- синхронизация task-local и skill-level документации.

### Не входит

- runtime-мутирующие команды;
- перенос смыслов из `task.md` в read-model;
- governance-контур `install_skill.py`;
- memory-layer и интеграции конкретных хостов.

## Контекст

- источник постановки: Track 4 из `TASK-2026-0008`;
- upstream-контракты: `TASK-2026-0010`, `TASK-2026-0011`;
- transport-решение зафиксировано в отдельном read-only facade `scripts/task_query.py`;
- политика определения активной задачи: `branch -> task-scoped dirty fallback -> warning`.

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| CLI / helper | добавлен новый read-only entrypoint `scripts/task_query.py` |
| Read model | добавлены `read_model.py`, `query_cli.py`, агрегаты status/current-task/task show |
| Runtime contract | зафиксированы warnings, current-task resolution policy и payload text/json |
| Тесты | добавлены `test_task_query.py` и `test_task_query_architecture.py` |
| Документация | обновлены task-local артефакты, `SKILL.md`, `references/task-workflow.md` |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0013-task-centric-vnext-read-model-reporting/`
- файл плана: `plan.md`
- файл SDD: `sdd.md`
- матрица проверки: `artifacts/verification-matrix.md`
- CLI-вход: `skills-global/task-centric-knowledge/scripts/task_query.py`
- runtime-модули: `skills-global/task-centric-knowledge/scripts/task_workflow_runtime/read_model.py`, `skills-global/task-centric-knowledge/scripts/task_workflow_runtime/query_cli.py`
- тесты: `skills-global/task-centric-knowledge/tests/test_task_query.py`, `skills-global/task-centric-knowledge/tests/test_task_query_architecture.py`
- стратегический источник: `knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/strategy-roadmap.md`

## Контур публикации

Delivery unit для этой задачи не требуется.

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | — | `—` | `—` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |

## Текущий этап

Реализация и дополнительный экспертный review/fix цикл завершены.
Read-only CLI устойчив к отсутствующему selector-резолвингу, дубликатам `TASK-ID` и битым строкам delivery units,
включая случаи с неверным числом колонок; dirty fallback больше не ломается от посторонних грязных путей,
а regression coverage расширено на health-, legacy- и publish-warning ветки.

## Стратегия проверки

### Покрывается кодом или тестами

- `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_query.py`
- `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_query_architecture.py`
- `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules status --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules current-task --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules task show TASK-2026-0013`
- `git diff --check`
- `scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0013-task-centric-vnext-read-model-reporting/task.md knowledge/tasks/TASK-2026-0013-task-centric-vnext-read-model-reporting/plan.md knowledge/tasks/TASK-2026-0013-task-centric-vnext-read-model-reporting/sdd.md knowledge/tasks/TASK-2026-0013-task-centric-vnext-read-model-reporting/artifacts/verification-matrix.md skills-global/task-centric-knowledge/SKILL.md skills-global/task-centric-knowledge/references/task-workflow.md`

### Остаётся на ручную проверку

- `не требуется`

## Критерии готовности

- реализованы `status`, `current-task`, `task show` как read-only operator surface;
- task-oriented output всегда использует каноническую summary-связку;
- ambiguity handling и drift warnings доказаны тестами;
- read-model не владеет состоянием `Task Core`;
- verification matrix переведена в `covered`.

## Итоговый список ручных проверок

- `не требуется`

## Итог

Добавлен новый operator CLI `scripts/task_query.py` поверх `task_workflow_runtime/query_cli.py` и `read_model.py`.
Read-model собирает статус knowledge-контура, безопасно определяет `current-task`, поддерживает `task show current|TASK-ID`, не мутирует данные и не переопределяет `task.md`.
Поведение закрыто unit- и architecture-тестами, включая selector-error, duplicate `TASK-ID`,
malformed delivery rows, planned delivery units в финальной задаче, health warnings и legacy fallback-paths.
Документация skill-а и task-local артефакты синхронизированы с фактической реализацией.
