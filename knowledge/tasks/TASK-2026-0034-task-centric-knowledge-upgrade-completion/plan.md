# План задачи TASK-2026-0034

## Правило

Для задачи существует только один файл плана: `plan.md`.
Если задача декомпозируется, каждая подзадача получает свой собственный `plan.md` внутри своей папки.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0034` |
| Parent ID | `—` |
| Версия плана | `2` |
| Связь с SDD | `не требуется` |
| Дата обновления | `2026-04-23` |

## Цель

Довести governed upgrade текущего репозитория `task-centric-knowledge`
до фактически завершённого состояния:
обновить repo upgrade-state из актуального managed-source,
закрыть pending compatibility-backfill по legacy-задачам
и подтвердить итог через install/workflow verify-контур.

## Границы

### Входит

- открытие и синхронизация новой task-scoped ветки;
- `install check`, `install apply --force`, `doctor-deps`, `cleanup-plan`;
- controlled `workflow backfill --scope compatibility` для каждого pending task entry;
- task-local migration notes и актуализация repo upgrade-state;
- тесты и локализационный guard по новым пользовательским артефактам.

### Не входит

- сетевые publish-действия и `push`;
- cleanup-confirm и удаление файлов;
- массовая правка narrative-content historical task-артефактов вне migration notes;
- новые функции вне upgrade/backfill-governance.

## Планируемые изменения

### Код

- кодовые изменения не планируются;
- допустим только точечный fix runtime/governance слоя, если verify выявит фактический дефект в `install` или `workflow backfill`.

### Конфигурация / схема данных / именуемые сущности

- `knowledge/operations/task-centric-knowledge-upgrade.md`;
- `knowledge/tasks/registry.md` и поле `Ветка` у `TASK-2026-0034`;
- task-local migration notes в legacy-задачах;
- возможно task-local allowlisted metadata active-задачи, если controlled backfill применится к текущей задаче.

### Документация

- `knowledge/tasks/TASK-2026-0034-task-centric-knowledge-upgrade-completion/task.md`
- `knowledge/tasks/TASK-2026-0034-task-centric-knowledge-upgrade-completion/plan.md`
- task-local migration notes в legacy-задачах
- `knowledge/operations/task-centric-knowledge-upgrade.md`

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- `не ожидаются`

### Границы, которые должны остаться изолированными

- `knowledge/tasks/registry.md` остаётся project data и может меняться только в части новой строки `TASK-2026-0034` и allowlisted sync текущей задачи;
- existing task directories не должны получать silent rewrite narrative-содержимого;
- user-managed sections в `AGENTS.md` вне managed-блока не должны измениться;
- cleanup scope не должен расшириться до реального удаления project data.

### Критический функционал

- `install apply --force` должен пересобрать upgrade-state без потери project data;
- `workflow backfill` должен создавать migration notes и корректно обновлять state по каждому task entry;
- итоговый status должен уйти из `partially-upgraded / dual-readiness`;
- новые или ранее пропущенные legacy entries должны обнаруживаться явно, а не теряться из state-файла.

### Основной сценарий

- открыть `TASK-2026-0034` и синхронизировать ветку/registry;
- прогнать install-governance и зафиксировать актуальный pending set;
- выполнить compatibility-backfill по каждому pending entry;
- перепроверить repo status, doctor и cleanup-plan;
- если verify выявит runtime-regression, локально исправить её и повторить проверки.

### Исходный наблюдаемый симптом

- `task-knowledge task status` возвращает `upgrade_status=partially-upgraded`, `execution_rollout=dual-readiness`, `legacy_pending_count=25`;
- state-файл не синхронизирован с фактическим составом более новых задач и удерживает хотя бы одну уже закрытую задачу как `active`.

## Риски и зависимости

- после пересборки upgrade-state pending count может вырасти, если runtime materialize ранее пропущенные legacy entries; это нужно считать ожидаемым раскрытием фактического scope, а не регрессией;
- текущая задача `TASK-2026-0034` может попасть в repo upgrade-state как `active`; если это произойдёт, её compatibility-backfill нужно выполнить осознанно и документировать явно;
- если любой backfill затронет protected fields historical task-truth, rollout нужно остановить и исправить runtime до продолжения;
- если verify покажет, что `cleanup-plan` больше не пуст, удаление всё равно остаётся отдельным confirm-gated действием.

## Связь с SDD

- `не требуется`

## Проверки

### Что можно проверить кодом или тестами

- `task-knowledge workflow sync --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --task-dir knowledge/tasks/TASK-2026-0034-task-centric-knowledge-upgrade-completion --create-branch --register-if-missing --summary "Довести локальный upgrade-state репозитория task-centric-knowledge до fully-upgraded через controlled compatibility-backfill legacy-задач."`
- `task-knowledge --json install check --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge`
- `task-knowledge --json install apply --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --force`
- `task-knowledge --json install doctor-deps --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge`
- `task-knowledge --json install cleanup-plan --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge`
- `task-knowledge workflow backfill --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --task-dir <task-dir> --scope compatibility`
- `task-knowledge --json task status --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge`
- `python3 -m unittest discover -s tests`
- `git diff --check`
- `bash scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0034-task-centric-knowledge-upgrade-completion/task.md knowledge/tasks/TASK-2026-0034-task-centric-knowledge-upgrade-completion/plan.md knowledge/operations/task-centric-knowledge-upgrade.md`

### Что остаётся на ручную проверку

- `не требуется`

## Шаги

- [x] Создать `TASK-2026-0034`, синхронизировать ветку и запись в `registry.md`.
- [x] Пересобрать governed upgrade-state через install helper и снять фактический pending set.
- [x] Выполнить compatibility-backfill по каждому pending task entry до нулевого pending count.
- [x] Прогнать verify-контур, обновить task-local итог и зафиксировать финальное состояние.

## Критерии завершения

- opened task корректно зарегистрирована и привязана к своей ветке;
- controlled backfill закрывает весь фактический pending set;
- `task-knowledge task status` больше не предупреждает про `legacy_backfill_pending` и `execution_rollout_partial`;
- install/workflow verify-контур зелёный;
- новые пользовательские артефакты проходят локализационный guard.
