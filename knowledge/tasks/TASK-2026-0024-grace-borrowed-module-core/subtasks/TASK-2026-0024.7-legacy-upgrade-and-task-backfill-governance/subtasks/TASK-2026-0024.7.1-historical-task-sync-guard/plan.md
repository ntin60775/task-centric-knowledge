# План задачи TASK-2026-0024.7.1

## Правило

Для задачи существует только один файл плана: `plan.md`.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0024.7.1` |
| Parent ID | `TASK-2026-0024.7` |
| Версия плана | `1` |
| Связь с SDD | `не требуется` |
| Дата обновления | `2026-04-20` |

## Цель

Определить guard для helper-синхронизации,
который запрещает переписывать historical branch и связанные метаданные
у завершённых задач при запуске sync из чужого активного контекста.
Guard также должен защищать rollout метаданных совместимости execution/readiness:
новая single-writer модель не должна создавать ложный active target для закрытой задачи.
Первый runtime-фикс в этом контуре устраняет ложный `branch_tie`
для нормального случая, когда parent и subtasks наследуют одну task-ветку.

## Границы

### Входит

- сценарий воспроизведения дефекта;
- expected behavior для historical task sync;
- allowlist безопасно обновляемых полей;
- protected fields для метаданных совместимости execution/readiness;
- связь с read-model warnings и ambiguity.

### Не входит

- broad refactor helper-а;
- изменение workflow активных задач;
- массовое backfill-исправление historical задач.

## Планируемые изменения

### Код

- будущий runtime guard в helper sync и regression-tests.
- read-model collapse shared parent/subtask branch к parent aggregate.

### Конфигурация / схема данных / именуемые сущности

- policy безопасной синхронизации historical-задач;
- allowlist compatibility-sync полей для завершённых задач.

### Документация

- task-local черновик дефекта;
- при реализации возможное уточнение runtime/reference docs.

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- подзадача зависит от текущего helper sync и read-model, но не меняет сам `Task Core`.

### Границы, которые должны остаться изолированными

- historical task metadata не должны переписываться текущей активной веткой;
- метаданные совместимости execution/readiness не должны менять branch/date/history закрытой задачи;
- summary-sync не должен превращаться в branch rewrite;
- закрытая задача не должна снова участвовать в `current-task` resolution как будто она активна.
- нормальное наследование ветки подзадачей не должно считаться ambiguity, если все кандидаты принадлежат одному aggregate.

### Критический функционал

- корректный safe-sync historical задач;
- безопасный compatibility-rollout execution/readiness metadata;
- отсутствие ложного `branch_tie/current_task_ambiguous`;
- сохранение `branch_tie/current_task_ambiguous` для несвязанных задач на одной ветке;
- сохранение исторической достоверности завершённых task-карточек.

### Основной сценарий

- оператор запускает helper sync для historical-задачи ради registry/summary sync;
- helper обновляет только разрешённые compatibility-поля;
- метаданные совместимости execution/readiness не создают active target;
- branch/history поля остаются историческими;
- `status/current-task` не получают ложных ambiguity warning-ов.

## Политика безопасной синхронизации

### Когда включается режим

- target-задача имеет статус `завершена` или `отменена`;
- active branch отличается от поля `Ветка` в target `task.md`;
- команда не является отдельным migration/backfill режимом с явным scope.

### Разрешено без migration/backfill scope

- обновить registry summary из canonical task summary, явного `--summary` или устойчивой первой строки `## Цель`;
- создать отсутствующую registry-строку только при `--register-if-missing`;
- сохранить branch-колонку registry равной historical `Ветка` из `task.md`;
- добавить совместимые metadata только в allowlisted блок, который не участвует в branch/date/history resolution.

### Запрещено без migration/backfill scope

- менять `Ветка`, `Дата создания`, `Дата обновления`, `Статус`, `Parent ID`, `Краткое имя`;
- менять narrative-секции задачи и план как будто новая версия существовала в прошлом;
- переписывать delivery unit lifecycle;
- подставлять текущую активную ветку в historical-задачу;
- создавать execution/readiness metadata, которые делают закрытую задачу active target.

### Ожидаемая ошибка

- если ordinary sync требует protected field update, helper должен остановиться с `historical_sync_blocked`;
- сообщение должно назвать protected fields и предложить отдельный migration/backfill режим.

### Исходный наблюдаемый симптом

- helper обновил summary для `TASK-2026-0023`, но одновременно переписал её historical branch на текущую ветку `TASK-2026-0024`, после чего read-model начал считать эту задачу кандидатом текущего контекста.

## Риски и зависимости

- если guard будет слишком жёстким, historical summary drift останется трудно исправлять;
- если guard будет слишком мягким, helper продолжит портить historical metadata.

## Связь с SDD

- `не требуется`

## Проверки

### Что можно проверить кодом или тестами

- regression-test helper sync для завершённой задачи;
- тест read-model: `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_query.py`;
- проверка текущей задачи: `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules current-task --format json`;
- проверка статуса: `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules status --format json`;
- проверка whitespace: `git diff --check`

### Что остаётся на ручную проверку

- `не требуется`

## Шаги

- [x] Зафиксировать reproducer ложного `branch_tie` для parent/subtask shared branch.
- [x] Исправить read-model collapse для parent aggregate.
- [x] Добавить regression-test на сохранение ambiguity для несвязанных задач на одной ветке.
- [x] Определить safe-sync policy для historical задач.
- [x] Определить allowlist обновляемых полей.
- [x] Определить protected fields для метаданных совместимости execution/readiness.
- [x] Увязать policy с read-model ambiguity rules.
- [x] Реализовать helper guard `historical_sync_blocked`.
- [x] Добавить regression-test helper sync для завершённой задачи из чужой ветки.

## Критерии завершения

- defect описан implement-ready образом;
- guard-поведение helper-а сформулировано однозначно;
- execution/readiness rollout не создаёт ложную активность;
- historical branch safety зафиксирована явно.

## Итог

Подзадача завершена.
Helper sync получил registry-only safe-sync для закрытых historical-задач,
а read-model получил collapse shared parent/subtask branch к parent aggregate.
Regression coverage добавлен для обоих контуров.
