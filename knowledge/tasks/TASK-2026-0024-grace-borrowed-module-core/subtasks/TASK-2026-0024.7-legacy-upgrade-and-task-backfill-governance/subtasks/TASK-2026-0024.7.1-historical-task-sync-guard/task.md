# Карточка задачи TASK-2026-0024.7.1

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0024.7.1` |
| Parent ID | `TASK-2026-0024.7` |
| Уровень вложенности | `2` |
| Ключ в путях | `TASK-2026-0024.7.1` |
| Технический ключ для новых именуемых сущностей | `historical-task-sync-guard` |
| Краткое имя | `historical-task-sync-guard` |
| Человекочитаемое описание | `Запретить helper-синхронизации переписывать branch и исторические метаданные закрытой задачи при запуске из чужой активной ветки и ограничить sync только безопасным compatibility-обновлением.` |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `task/task-2026-0024-grace-borrowed-module-core` |
| Требуется SDD | `нет` |
| Статус SDD | `не требуется` |
| Ссылка на SDD | `—` |
| Дата создания | `2026-04-20` |
| Дата обновления | `2026-04-20` |

## Цель

Устранить defect helper-синхронизации,
при котором запуск registry/task sync для уже завершённой исторической задачи
из чужой активной ветки может:
переписать поле `Ветка`,
обновить `Дата обновления`
и тем самым создать ложную неоднозначность `current-task`
или разрушить историческую достоверность task-артефакта.
Этот guard также защищает rollout метаданных совместимости execution/readiness:
новая single-writer модель не должна делать закрытую задачу похожей на активный execution target.

## Границы

### Входит

- описать воспроизводимый сценарий сбоя на закрытой historical-задаче;
- определить, какие поля historical-задачи helper не имеет права менять при sync из чужого branch-контекста;
- определить безопасный режим sync для historical-задач:
  обновлять только registry summary / compatibility-метаданные там, где это не искажает историю;
- определить, что метаданные совместимости execution/readiness не меняют branch/date/history закрытой задачи;
- определить expected behavior для `task_workflow.py --register-if-missing` и связанных runtime helper-слоёв;
- исправить read-model collapse для нормального parent/subtask наследования ветки:
  чистая shared ветка одного aggregate выбирает родителя, а dirty-scope может выбрать конкретную подзадачу;
- увязать решение с policy `closed historical` из `TASK-2026-0024.7`.

### Не входит

- полный redesign task routing;
- изменение branch-логики для активных задач;
- массовое исправление всех historical-задач без отдельного governed прохода.

## Контекст

- источник постановки: при устранении `summary_drift` по `TASK-2026-0023` helper обновил summary, но заодно перезаписал historical branch на текущую ветку `task/task-2026-0024-grace-borrowed-module-core`;
- связанная область: helper sync, historical task integrity, read-model ambiguity;
- ограничения и зависимости: для закрытых задач source-of-truth должен оставаться историческим снимком их реального рабочего контекста;
- исходный наблюдаемый симптом / лог-маркер: после sync появляется `branch_tie/current_task_ambiguous`, потому что завершённая задача начинает выглядеть как активная задача текущей ветки;
- основной контекст сессии: `defect-подзадача внутри upgrade/backfill governance`

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | `skills-global/task-centric-knowledge/scripts/task_workflow_runtime/read_model.py`, `task_workflow.py` и runtime синхронизации task/registry |
| Конфигурация / схема данных / именуемые сущности | policy branch-safe sync для historical task-карточек |
| Интерфейсы / формы / страницы | read-model `status/current-task` косвенно перестаёт получать ложные ambiguity-сигналы |
| Интеграции / обмены | связь с registry sync, upgrade/backfill governance и historical task policy |
| Документация | task-local defect draft, последующее отражение в `references/upgrade-transition.md` или helper runtime docs при необходимости |

## Связанные материалы

- родительская подзадача: `knowledge/tasks/TASK-2026-0024-grace-borrowed-module-core/subtasks/TASK-2026-0024.7-legacy-upgrade-and-task-backfill-governance/`
- затронутая historical-задача: `knowledge/tasks/TASK-2026-0023-owned-text-localization-guard-rename/`
- точка входа helper-а: `skills-global/task-centric-knowledge/scripts/task_workflow.py`
- policy исторических задач: `knowledge/tasks/TASK-2026-0024-grace-borrowed-module-core/subtasks/TASK-2026-0024.7-legacy-upgrade-and-task-backfill-governance/task.md`

## Текущий этап

Подзадача завершена:
read-model больше не создаёт ложный `branch_tie` для shared parent/subtask branch одного aggregate,
а helper sync защищает закрытые historical-задачи от перезаписи `Ветка` и `Дата обновления`
при запуске из чужой активной ветки.

## Политика безопасной синхронизации

### Классы задач

- `active`: задача не находится в финальном статусе и может синхронизировать `Ветка`, `Дата обновления`, summary и registry branch по текущему рабочему контексту.
- `closed historical`: задача в статусе `завершена` или `отменена`; её `Ветка`, `Дата создания`, `Дата обновления`, historical branch/date/history и narrative считаются историческим снимком.
- `reference`: задача или артефакт используется как справочный источник; любые изменения допускаются только через явный task-scoped migration/backfill, а не через обычный sync.

### Правило определения historical safe-sync

Historical safe-sync включается, если выполнены все условия:

- целевой `task.md` имеет финальный статус `завершена` или `отменена`;
- активная git-ветка не совпадает с сохранённым полем `Ветка` этой задачи;
- запуск не является явным migration/backfill-действием с отдельным подтверждённым scope.

Если `Ветка` у финальной задачи пустая или placeholder, helper не должен подставлять текущую ветку автоматически.
Такой случай считается `blocked` для обычного sync и требует отдельного migration/backfill решения.

### Allowlist обычного historical sync

Без отдельного migration/backfill scope helper может обновлять только:

- строку `knowledge/tasks/registry.md` для этой задачи, но без изменения branch-колонки;
- registry summary, если он получен из канонического `Человекочитаемое описание`, явного `--summary` или устойчивой первой строки `## Цель`;
- отсутствующую строку registry для historical-задачи, если `--register-if-missing` передан явно и branch берётся из сохранённого `Ветка`, а не из active branch;
- compatibility metadata, если она добавляется в отдельный allowlisted блок и не меняет historical fields.

### Защищённые поля

В ordinary historical sync запрещено менять:

- `Ветка`;
- `Дата создания`;
- `Дата обновления`;
- `Статус`;
- `Parent ID`;
- `Краткое имя`;
- `Человекочитаемое описание`, кроме отдельного explicit summary migration;
- `Текущий этап`, `Цель`, `Итог`, `План`, `Стратегия проверки` и другие narrative-секции;
- delivery unit поля `Head`, `Base`, `Статус`, `URL`, `Merge commit`, `Cleanup`;
- branch/date/history поля будущих execution/readiness metadata.

### Ожидаемое поведение helper-а

- `task_workflow.py --register-if-missing` для `closed historical` из чужой ветки не вызывает обычный `update_task_file`.
- Registry update в этом режиме использует сохранённую historical ветку из `task.md`.
- Если requested sync требует поменять protected field, helper останавливается с явной ошибкой `historical_sync_blocked`.
- Если нужен controlled backfill, он должен идти отдельным migration/backfill режимом с явным scope, отдельной проверкой и отдельным commit-ом.

### Связь с read-model

- Historical safe-sync не должен создавать нового branch-match для текущей активной ветки.
- `current-task` не должен получать `current_task_ambiguous` из-за закрытой задачи, которую helper синхронизировал ради registry summary.
- Нормальный parent/subtask shared branch обрабатывается отдельно: read-model выбирает parent aggregate в clean tree и конкретную подзадачу через dirty-scope.

## Стратегия проверки

### Покрывается кодом или тестами

- regression-test на sync завершённой задачи из чужой ветки;
- тест helper sync: `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_workflow.py`;
- тест read-model: `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_query.py`;
- полный набор тестов task-centric-knowledge: `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests`;
- проверка текущей задачи: `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules current-task --format json`;
- проверка статуса: `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules status --format json`;
- проверка whitespace: `git diff --check`

### Остаётся на ручную проверку

- `не требуется`

## Критерии готовности

- проблема описана воспроизводимо и без двусмысленностей;
- normal parent/subtask branch inheritance не даёт `current_task_ambiguous`;
- safe-sync policy для historical-задач определена;
- allowlist обычного historical sync и protected fields определены;
- метаданные совместимости execution/readiness не создают ложный active target;
- следующий implementer понимает, какие поля можно обновлять, а какие нет.

## Итоговый список ручных проверок

- `не требуется`

## Итог

Реализован guard `historical_sync_blocked`:
закрытая historical-задача синхронизируется через registry-only safe-sync,
если её запускают из чужой активной ветки.
`task.md` не меняет protected fields,
registry сохраняет historical branch,
а отсутствие зафиксированной historical branch блокирует ordinary sync.
Добавлены regression-tests для helper sync и read-model.
