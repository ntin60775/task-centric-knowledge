# Карточка задачи TASK-2026-0024.7

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0024.7` |
| Parent ID | `TASK-2026-0024` |
| Уровень вложенности | `1` |
| Ключ в путях | `TASK-2026-0024.7` |
| Технический ключ для новых именуемых сущностей | `legacy-upgrade-backfill` |
| Краткое имя | `legacy-upgrade-and-task-backfill-governance` |
| Человекочитаемое описание | `Определить versioned upgrade старых версий task-centric-knowledge и policy compatibility-backfill старых задач без реткона закрытых исторических артефактов.` |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `main` |
| Требуется SDD | `нет` |
| Статус SDD | `не требуется` |
| Ссылка на SDD | `—` |
| Дата создания | `2026-04-20` |
| Дата обновления | `2026-04-20` |

## Цель

Определить governed-переход со старых версий `task-centric-knowledge` на новую версию с `Module Core`
и policy по обновлению старых task-артефактов,
включая rollout controller-guided single-writer execution-модели,
при которой:
закрытые задачи получают только compatibility-backfill и migration-note,
активные и незавершённые задачи допускается доводить до новых правил глубже,
а исторический narrative завершённых задач не переписывается задним числом.

## Границы

### Входит

- определить versioned upgrade path для старых версий skill-а и knowledge-системы;
- определить классы legacy задач: `closed historical`, `active`, `reference`;
- определить, какие task-артефакты и поля допускается обновлять автоматически, а какие только вручную;
- определить форму compatibility-backfill, migration-note и статусов перехода вроде `legacy-compatible`, `partially-upgraded`, `fully-upgraded`;
- определить, как legacy repos получают execution/readiness fields без переписывания task narrative;
- определить, какие старые skill-level executor-контракты должны деградировать или мигрировать к `single writer + main controller`;
- увязать новый migration-track с существующим install/upgrade governance и `project data` safety.

### Не входит

- массовый реткон закрытых исторических задач;
- автоматическое переписывание старых `plan.md`, `sdd.md`, `verification-matrix.md` так, как будто новая версия существовала в прошлом;
- физическая миграция всех legacy задач в этом ходе.

## Контекст

- источник постановки: пользователь явно ожидает, что новая версия будет иметь upgrade-процесс со старых версий и policy обновления старых задач;
- связанная область: install/upgrade governance, historical task integrity и controlled legacy backfill;
- ограничения и зависимости: `references/upgrade-transition.md` уже требует не ломать `project data`, а `TASK-2026-0021` уже допускала ограниченный legacy sync без изменения смысла завершённых задач;
- принятая policy пользователя: режим `2` — закрытые задачи только compatibility-backfill, активные допускается доводить до новых правил глубже;
- основной контекст сессии: `governance-подзадача Module Core`

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | будущий installer/runtime governance, возможно read-model warnings и migration helpers |
| Конфигурация / схема данных / именуемые сущности | versioned upgrade path, migration-note policy, legacy classification и статусы совместимости |
| Интерфейсы / формы / страницы | возможные read-only diagnostics по степени upgrade/backfill |
| Интеграции / обмены | связь с `install/check/doctor/upgrade`, `migrate-cleanup-plan/confirm` и refresh borrowed-layer |
| Документация | `references/upgrade-transition.md`, `references/deployment.md`, `SKILL.md`, migration notes и task-local policy |

## Связанные материалы

- родительская задача: `knowledge/tasks/TASK-2026-0024-grace-borrowed-module-core/`
- безопасный upgrade старой версии: `skills-global/task-centric-knowledge/references/upgrade-transition.md`
- governance установки и обновления: `skills-global/task-centric-knowledge/references/deployment.md`
- граница продукта: `knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/artifacts/v1-product-thesis.md`
- precedent ограниченного legacy sync: `knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/`

## Текущий этап

Подзадача завершена.
Реализованы:

- репозиторное состояние upgrade/backfill по пути `knowledge/operations/task-centric-knowledge-upgrade.md`;
- explicit helper-режим `workflow backfill`;
- task-local migration notes для `active` и `closed historical`;
- repo-level diagnostics для `install/check/doctor/status`;
- policy `active / closed historical / reference` с явной marker-моделью для `reference`.

Следующий implementable шаг в родительской цепочке — задача `TASK-2026-0024.2`.

## Стратегия проверки

### Покрывается кодом или тестами

- прогон install-тестов: `python3 -m unittest skills-global/task-centric-knowledge/tests/test_install_skill.py`
- прогон status/query тестов: `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_query.py`
- прогон workflow-тестов: `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_workflow.py`
- прогон unified CLI тестов: `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_knowledge_cli.py`
- `git diff --check`

### Остаётся на ручную проверку

- `не требуется`

## Критерии готовности

- versioned upgrade path описан без двусмысленностей;
- policy `closed historical / active / reference` однозначна;
- compatibility-backfill отделён от реткона исторических задач;
- rollout execution/readiness fields не меняет историческую task-truth;
- следующий implementer понимает, какие legacy-поля можно обновлять автоматически, а какие нет.

## Итоговый список ручных проверок

- `не требуется`

## Итог

Реализован governed-контур legacy upgrade/backfill:
repo получает versioned upgrade-state по эпохам `legacy-v1 -> module-core-v1`,
compatibility-backfill выполняется только через explicit `workflow backfill`,
`closed historical` остаются immutable кроме task-local migration note,
а `reference` определяется только явной пометкой и уходит в `manual-reference`.
