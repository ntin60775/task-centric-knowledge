# План задачи TASK-2026-0013

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0013` |
| Parent ID | `—` |
| Версия плана | `5` |
| Связь с SDD | `sdd.md`, `artifacts/verification-matrix.md` |
| Дата обновления | `2026-04-13` |

## Цель

Построить операторский read-model слой `status / current-task / task show` поверх `Task Core`
без превращения его в новый источник истины и без смешивания с mutate/helper-поверхностью.

## Границы

### Входит

- read-only projection над knowledge-системой;
- новый facade `scripts/task_query.py`;
- output contract text/json и warnings;
- task summary triple в каждом task-oriented ответе;
- политика определения `current-task`: `branch -> dirty fallback -> warning`;
- тесты и документация read-model слоя.

### Не входит

- mutate-команды;
- governance и cleanup;
- memory-layer;
- интеграции конкретных хостов.

## Планируемые изменения

### Код

- добавить `skills-global/task-centric-knowledge/scripts/task_query.py` как thin facade-entrypoint;
- добавить `skills-global/task-centric-knowledge/scripts/task_workflow_runtime/read_model.py` с task discovery, current-task resolver, drift/warning policy и projection payload;
- добавить `skills-global/task-centric-knowledge/scripts/task_workflow_runtime/query_cli.py` с text/json transport и formatter;
- расширить `models.py` каноническими task-status константами.

### Документация

- синхронизировать `knowledge/tasks/TASK-2026-0013-.../{task,plan,sdd}.md` и `artifacts/verification-matrix.md`;
- обновить `skills-global/task-centric-knowledge/SKILL.md`;
- обновить `skills-global/task-centric-knowledge/references/task-workflow.md`.

### Тесты

- добавить `skills-global/task-centric-knowledge/tests/test_task_query.py`;
- добавить `skills-global/task-centric-knowledge/tests/test_task_query_architecture.py`;
- покрыть resolved/ambiguous/unresolved сценарии, drift warnings и text output.

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- новый read-only маршрут: `scripts/task_query.py -> task_workflow_runtime/query_cli.py -> task_workflow_runtime/read_model.py`;
- `read_model.py` читает только существующие runtime-слои `git_ops.py`, `models.py`, `task_markdown.py`;
- `task_workflow.py` и `install_skill.py` сохраняют прежнюю mutate/governance роль и не становятся transport-layer для operator-команд.

### Границы, которые должны остаться изолированными

- `task.md` остаётся единственным источником истины по summary/status/branch;
- `registry.md` используется только как navigation cache и источник drift-сигналов;
- read-model не импортирует governance runtime и не выполняет git mutation.

### Критический функционал

- детерминированно строить `status`, `current-task`, `task show`;
- безопасно разрешать активную задачу без молчаливого выбора при неоднозначности;
- показывать каноническую summary-связку во всех task-oriented ответах.

### Основной сценарий

- оператор запускает `task_query.py`;
- получает компактный task-oriented ответ в `text` или `json`;
- read-model использует только `Task Core`, delivery-проекции и registry-кэш для warnings;
- при неоднозначности возвращается warning и список кандидатов вместо произвольного выбора.

### Исходный наблюдаемый симптом

- до реализации в runtime отсутствовал отдельный operator read-model поверх `Task Core`.

## Риски и зависимости

- legacy-задачи без `Человекочитаемого описания` могут давать migration-warning и шумный `status`;
- parent/subtask на одной ветке требуют аккуратного dirty fallback без ложного выбора родителя;
- text formatter нельзя превращать в источник доменной логики.
- read-only reporting не должен падать на malformed delivery rows и missing selector.
- read-only reporting не должен молча терять publish-строки с неверным числом колонок и карточки с duplicate `TASK-ID`.

## Связь с SDD

- реализованы этапы `Output contract`, `Projection runtime`, `Acceptance`;
- verification coverage фиксируется в `artifacts/verification-matrix.md`;
- канонический source-of-truth остаётся в `task.md` по контракту `TASK-2026-0010`.

## Проверки

### Что можно проверить кодом или тестами

- `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_query.py`
- `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_query_architecture.py`
- `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules status --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules current-task --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules task show TASK-2026-0013`
- `git diff --check`
- `scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0013-task-centric-vnext-read-model-reporting/task.md knowledge/tasks/TASK-2026-0013-task-centric-vnext-read-model-reporting/plan.md knowledge/tasks/TASK-2026-0013-task-centric-vnext-read-model-reporting/sdd.md knowledge/tasks/TASK-2026-0013-task-centric-vnext-read-model-reporting/artifacts/verification-matrix.md skills-global/task-centric-knowledge/SKILL.md skills-global/task-centric-knowledge/references/task-workflow.md`

### Что остаётся на ручную проверку

- `не требуется`

## Шаги

- [x] Создать task-ветку и синхронизировать контекст `TASK-2026-0013`.
- [x] Зафиксировать transport-layer как отдельный read-only facade `scripts/task_query.py`.
- [x] Реализовать projections, formatter и warnings в runtime.
- [x] Добавить coverage для resolved/ambiguous/unresolved и drift-сценариев.
- [x] Синхронизировать CLI contract с task-артефактами и документацией.
- [x] Прогнать verify-команды и локализационный guard.
- [x] Закрыть замечания экспертного review-цикла по crash-paths, dirty fallback и warning coverage.

## Критерии завершения

- operator-команды реализованы и не конфликтуют с `Task Core`;
- task summary contract соблюдается во всех task-oriented ответах;
- ambiguity handling доказан тестами;
- import-graph и thin facade закрыты architecture-проверкой;
- verification matrix переведена в `covered`.
