# SDD по задаче TASK-2026-0027

## Паспорт SDD

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0027` |
| Статус | `в работе` |
| Версия | `1` |
| Дата обновления | `2026-04-21` |

## 0. Инварианты и verification matrix

### Полный invariant set

- `INV-01`: local finalize допускается только в безопасном task-контексте; при блокере helper не мутирует git-состояние и возвращает явный список причин и действий.
- `INV-02`: успешный local finalize создаёт task-scoped commit, вливает task-ветку в base-ветку и переводит рабочий контекст на base-ветку без `push` и без переписывания истории.
- `INV-03`: после успешного finalize task metadata синхронизируется с итоговым локальным состоянием: task truth и registry больше не указывают на старую task-ветку как на активный рабочий контекст.
- `INV-04`: publish и remote-контуры остаются опциональными; отсутствие remote/auth не должно ломать local finalize и не должно маскироваться как успех.
- `INV-05`: открытые delivery units, base-branch ambiguity, dirty чужой diff или запуск с base-ветки приводят к blocker-report, а не к частично выполненному finalize.

### Связанные артефакты проверки

- `artifacts/verification-matrix.md` — матрица покрытия для success и blocker сценариев.

## 1. Проблема и цель

### Проблема

Текущий workflow helper документирован как инструмент без отдельного `finalize-task`: он не делает локальный commit/merge/checkout финального шага даже в ясном task-контексте. Для пользователя это расходится с ожидаемым поведением проекта: если задача завершена и блокеров нет, локальный git-контур должен закрываться автоматически; если блокер есть, система должна явно назвать причину и предложить следующий шаг.

### Цель

Добавить local finalize path, который по одной команде либо завершает локальный task lifecycle (`commit -> merge -> checkout base`), либо возвращает детерминированный blocker-report без побочных мутаций.

## 2. Архитектура и границы

- новый finalize path живёт внутри `task_workflow_runtime` рядом с existing sync/publish flow;
- unified CLI `task-knowledge workflow ...` и legacy facade `scripts/task_workflow.py` получают новый action;
- finalize использует локальные git helper-операции и task metadata update, но не зависит от forge adapters;
- результат должен иметь стабильный JSON/text surface с отдельным представлением success и blocked outcome.

### Допустимые и недопустимые связи

- допустимо: finalize flow -> git helpers, task markdown helpers, registry sync;
- допустимо: finalize flow -> publish metadata read-only для проверки открытых delivery units;
- недопустимо: mandatory finalize path -> forge adapters, remote auth, network actions;
- недопустимо: finalize flow -> history rewrite (`rebase`, `reset`, branch deletion).

### Новые зависимости и их обоснование

- `нет`

### Наблюдаемые сигналы и диагностические маркеры

- blocker codes в finalize payload;
- текущая ветка, base-ветка, список blocker reasons, proposed actions;
- `merge_commit` и итоговый active branch для success path.

## 3. Изменения данных / схемы / metadata

- меняется workflow command surface: добавляется новый action `finalize`;
- при успехе меняются `task.md`, `knowledge/tasks/registry.md` и git history локального репозитория;
- новые persistent data stores не вводятся.

## 4. Новые сущности и интерфейсы

- новый CLI path: `task-knowledge workflow finalize --project-root /abs/project --task-dir ...`
- legacy CLI path: `python3 scripts/task_workflow.py --project-root /abs/project --task-dir ... --publish-action finalize` не подходит по семантике, поэтому нужен отдельный workflow action surface в unified и legacy entrypoint;
- новый runtime payload:
  - `outcome`: `finalized` | `blocked`
  - `task_id`
  - `task_branch`
  - `base_branch`
  - `commit_created`
  - `merge_commit`
  - `results`
  - `blockers`
  - `next_actions`

## 5. Изменения в существующих компонентах

- `scripts/task_knowledge_cli.py`
  - добавить parser и dispatch для `workflow finalize`;
- `scripts/task_workflow_runtime/cli.py`
  - синхронизировать legacy workflow surface;
- `scripts/task_workflow_runtime/git_ops.py`
  - добавить безопасные helper-операции для task-scoped commit, merge и checkout;
- `scripts/task_workflow_runtime/*`
  - выделить finalize runtime и связать его с metadata update;
- `README.md`, `SKILL.md`, `references/task-workflow.md`
  - описать новый local auto-finalize contract и его ограничения.

## 6. Этапы реализации и проверки

### Этап 1: Contract и blocker model

- зафиксировать action surface и payload shape;
- определить обязательные blocker conditions;
- описать sync metadata after finalize.
- Проверка: task-local docs + новые/обновлённые unit-тесты contract surface
- Аудит: `SDD_AUDIT`

### Этап 2: Runtime реализация

- реализовать finalize runtime и safe git helpers;
- встроить action в unified CLI и legacy facade;
- обновить task metadata после success path.
- Проверка: целевые unit-тесты finalize runtime и CLI routing
- Аудит: `IMPLEMENTATION_AUDIT`

### Финальный этап: Интеграция

- обновить reference docs;
- прогнать полный unittest и localization guard;
- подтвердить покрытие verification matrix.
- Проверка: `python3 -m unittest discover -s tests`, `bash scripts/check-docs-localization.sh`, `git diff --check`
- Аудит: `INTEGRATION_AUDIT`

## 7. Критерии приёмки

1. Из unified CLI можно запустить local finalize отдельным action без обращения к remote/publish tooling.
2. При безопасном task-контексте helper создаёт локальный commit, merge в base-ветку и переключает рабочий контекст на неё.
3. При любом blocker condition helper не делает частичных мутаций и возвращает явный blocker-report с действиями.
4. `task.md`, `registry.md` и reference docs синхронизированы с новым finalize contract.
5. Полный test/doc verify loop проходит без регрессий.

## 8. Стоп-критерии

1. Реализация требует обязательного remote/auth или скрыто тянет network path в local finalize.
2. Helper не может детерминированно отличить success path от blocker path и рискует оставить частично выполненный finalize.
3. Новый finalize flow ломает существующие sync/publish контракты или historical/task ambiguity scenarios.
