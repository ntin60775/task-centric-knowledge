# План задачи TASK-2026-0024.7

## Правило

Для задачи существует только один файл плана: `plan.md`.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0024.7` |
| Parent ID | `TASK-2026-0024` |
| Версия плана | `2` |
| Связь с SDD | `не требуется` |
| Дата обновления | `2026-04-20` |

## Цель

Определить versioned upgrade path на новую версию `task-centric-knowledge`
и умеренную policy legacy task backfill:
закрытые задачи — только compatibility-backfill и migration-note,
активные и незавершённые — допускается доводить до новых правил глубже,
reference-задачи — только по отдельному явному решению.
Отдельно описать rollout execution/readiness модели,
чтобы legacy repos получали single-writer contract без реткона старых task-артефактов.

## Границы

### Входит

- versioned путь перехода старой версии skill-а и managed-ресурсов на новую;
- классификация legacy задач;
- allowlist task-артефактов и полей для compatibility-backfill;
- migration-note и модель фиксации степени upgrade/backfill;
- rollout policy для `ExecutionPacket`, `ExecutionReadiness`, `FailureHandoff`;
- migration policy для старых skill-level executor-контрактов к модели `main controller + single writer`;
- связь с install/upgrade governance и diagnostics.

### Не входит

- массовая миграция всех legacy задач в этой подзадаче;
- переписывание исторического narrative закрытых задач;
- реализация rich migration UI или отдельного migration framework.

## Планируемые изменения

### Код

- runtime `task_workflow_runtime/legacy_upgrade.py` и `backfill_flow.py`;
- controlled backfill surface в `task_workflow.py` и `task-knowledge workflow backfill`;
- repo-level diagnostics в install/query runtime.

### Конфигурация / схема данных / именуемые сущности

- репозиторное состояние upgrade/backfill по пути `knowledge/operations/task-centric-knowledge-upgrade.md`;
- эпохи `legacy-v1` и `module-core-v1`;
- repo-level статусы `legacy-compatible`, `partially-upgraded`, `fully-upgraded`;
- rollout-статусы `legacy`, `dual-readiness`, `single-writer`;
- task-local migration note для legacy-задачи;
- field-marker `Справочный режим = reference`.

### Документация

- task-local contract в `artifacts/legacy-upgrade-backfill-contract.md`;
- обновление `references/upgrade-transition.md`, `references/deployment.md`, `SKILL.md` и `README.md`.

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- migration/backfill layer опирается на существующий install/upgrade governance, но не подменяет `Task Core` source-of-truth;
- execution-policy rollout не должен переписывать закрытые task-local docs и не должен подменять skill-specific runtime contracts без отдельной controlled migration.

### Границы, которые должны остаться изолированными

- `project data` остаются защищёнными;
- compatibility-backfill не превращается в narrative rewrite;
- закрытые исторические задачи не переписываются так, будто новая система существовала изначально;
- active задачи можно доводить глубже только в пределах их текущего жизненного цикла и без потери доказательной целостности.

### Критический функционал

- воспроизводимый upgrade-path между версиями;
- безопасная policy обновления старых задач;
- безопасный rollout single-writer execution contract;
- сохранение исторической достоверности закрытых task-артефактов.

### Основной сценарий

- оператор обновляет старую совместимую версию skill-а;
- получает понятный versioned переход;
- для старых задач система различает `closed historical`, `active` и `reference`;
- compatibility-backfill обновляет только разрешённые поля и при необходимости добавляет migration-note.

### Исходный наблюдаемый симптом

- новая волна `Module Core` пока не описывает, как на неё переходить со старых версий и как обращаться со старыми задачами без реткона истории.

## Риски и зависимости

- если policy окажется слишком агрессивной, будут переписаны исторические артефакты;
- если policy окажется слишком слабой, новая версия будет плохо внедряться в уже живые репозитории;
- подзадача зависит от существующего upgrade governance в `references/upgrade-transition.md`.

## Связь с SDD

- `не требуется`

## Проверки

### Что можно проверить кодом или тестами

- прогон install-тестов: `python3 -m unittest skills-global/task-centric-knowledge/tests/test_install_skill.py`
- прогон status/query тестов: `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_query.py`
- прогон workflow-тестов: `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_workflow.py`
- прогон unified CLI тестов: `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_knowledge_cli.py`
- `git diff --check`

### Что остаётся на ручную проверку

- `не требуется`

## Шаги

- [x] Зафиксировать versioned upgrade path для старых версий.
- [x] Определить policy `closed historical / active / reference`.
- [x] Определить allowlist compatibility-backfill для legacy task-артефактов.
- [x] Описать migration-note и статусы степени upgrade/backfill.
- [x] Описать compatibility metadata для execution/readiness rollout.
- [x] Описать migration path старых executor-контрактов к `main controller + single writer`.
- [x] Увязать policy с install/upgrade governance и diagnostics.

## Критерии завершения

- upgrade/backfill governance описан достаточно конкретно для последующей реализации;
- policy режима `2` однозначно отражена в документах;
- execution/readiness rollout не нарушает historical integrity;
- historical integrity закрытых задач защищена явно.

## Итог

Подзадача реализована.
Репозиторное состояние upgrade/backfill, explicit `workflow backfill`,
task-local migration notes и новые diagnostics в `status`/`install`
закрыли плановую policy без смешивания ordinary sync и controlled backfill.
