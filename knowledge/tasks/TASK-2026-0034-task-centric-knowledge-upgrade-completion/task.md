# Карточка задачи TASK-2026-0034

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0034` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0034` |
| Технический ключ для новых именуемых сущностей | `upgrade-completion` |
| Краткое имя | `task-centric-knowledge-upgrade-completion` |
| Человекочитаемое описание | `Довести локальный upgrade-state репозитория task-centric-knowledge до fully-upgraded через controlled compatibility-backfill legacy-задач.` |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `main` |
| Требуется SDD | `нет` |
| Статус SDD | `не требуется` |
| Ссылка на SDD | `—` |
| Дата создания | `2026-04-23` |
| Дата обновления | `2026-04-23` |

## Цель

Завершить governed upgrade текущего репозитория `task-centric-knowledge`:
пересобрать managed upgrade-state из актуального skill-source,
применить explicit compatibility-backfill ко всем pending legacy-задачам
и перевести репозиторий из состояния `partially-upgraded / dual-readiness`
в каноническое `fully-upgraded / single-writer`
без потери `project data` и без silent rewrite historical task-truth.

## Подсказка по статусу

Использовать только одно из значений:

- `черновик`
- `готова к работе`
- `в работе`
- `на проверке`
- `ждёт пользователя`
- `заблокирована`
- `завершена`
- `отменена`

`черновик` относится только к уже открытой задаче или подзадаче.
Будущие кандидаты в подзадачи до фактического открытия нужно держать в `plan.md` или `task.md` родителя, а не оформлять как отдельную сущность.

## Git-подсказка

- Поле `Ветка` хранит текущую активную ветку рабочего контекста, а не обязательную долгоживущую task-ветку.
- При открытии верхнеуровневой задачи стартовый контекст обычно синхронизируется в `task/<task-id-lower>-<slug>`.
- Для первой и последующих поставок helper может переводить `Ветка` в delivery-ветку вида `du/<task-id-lower>-uNN-<slug>`.
- Для подзадачи по умолчанию можно указывать ветку родителя, если отдельная ветка или delivery unit не нужны.
- При каждом создании или переключении ветки нужно синхронизировать это поле и строку в `registry.md`.

## Границы

### Входит

- governed upgrade-последовательность `install check -> install apply --force -> doctor-deps -> cleanup-plan`;
- controlled compatibility-backfill для всех pending entries в `knowledge/operations/task-centric-knowledge-upgrade.md`;
- создание отсутствующих task-local migration notes;
- актуализация repo upgrade-state до фактического состава legacy-задач текущего репозитория;
- task-local документация этой задачи и локализационная проверка новых артефактов.

### Не входит

- `push`, PR/MR и любые сетевые публикации;
- удаление путей через cleanup-confirm, если safe-delete scope по-прежнему пустой;
- переписывание narrative-секций historical task-артефактов;
- новые product capability вне upgrade/backfill governance.

## Контекст

- источник постановки: пользовательский запрос от `2026-04-23` — `$task-centric-knowledge обнови`;
- связанная бизнес-область: governed upgrade и legacy compatibility-backfill внутри standalone-репозитория `task-centric-knowledge`;
- ограничения и зависимости: обновление должно сохранить `knowledge/tasks/registry.md`, managed knowledge-файлы и existing task directories как `project data`;
- исходный наблюдаемый симптом / лог-маркер: `task-knowledge task status` показывает `compatibility_epoch=module-core-v1`, `upgrade_status=partially-upgraded`, `execution_rollout=dual-readiness`, `legacy_pending_count=25`; state-файл не покрывает часть более новых задач и держит `TASK-2026-0031` как `active`, хотя её `task.md` уже закрыт;
- основной контекст сессии: `завершение локального upgrade-state до fully-upgraded`

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | возможно `scripts/task_workflow_runtime/*` или `scripts/install_skill_runtime/*`, если verify выявит реальную регрессию governed backfill/update state |
| Конфигурация / схема данных / именуемые сущности | `knowledge/operations/task-centric-knowledge-upgrade.md`, task-local migration notes, branch/registry metadata при controlled backfill active-задачи |
| Интерфейсы / формы / страницы | CLI text/json surface `task-knowledge install *` и `task-knowledge workflow backfill`, если обнаружится дефект verify-контура |
| Интеграции / обмены | локальный install/governance runtime между install helper и workflow backfill |
| Документация | `knowledge/tasks/TASK-2026-0034-task-centric-knowledge-upgrade-completion/`, migration notes в legacy-задачах, возможно актуализация `knowledge/operations/task-centric-knowledge-upgrade.md` |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0034-task-centric-knowledge-upgrade-completion/`
- файл плана: `plan.md`
- файл SDD: `—`
- файл verification matrix: `—`
- состояние перехода репозитория: `knowledge/operations/task-centric-knowledge-upgrade.md`
- безопасный порядок upgrade: `references/upgrade-transition.md`
- пользовательские материалы: сообщение пользователя от `2026-04-23`
- связанные коммиты / PR / ветки: `task/task-2026-0034-task-centric-knowledge-upgrade-completion`
- связанные операции в `knowledge/operations/`, если есть: `knowledge/operations/task-centric-knowledge-upgrade.md`

## Контур публикации

Delivery unit для локального governed upgrade не требуется.

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | — | `—` | `—` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |

## Текущий этап

Локальный finalize выполнен: task-ветка влита в base-ветку, рабочий контекст переведён на base-ветку, `push` остаётся отдельным шагом.
## Стратегия проверки

### Покрывается кодом или тестами

- `task-knowledge --json task status --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge`
- `task-knowledge --json install check --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge`
- `task-knowledge --json install apply --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --force`
- `task-knowledge --json install doctor-deps --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge`
- `task-knowledge --json install cleanup-plan --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge`
- `task-knowledge workflow backfill --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --task-dir <task-dir> --scope compatibility`
- `python3 -m unittest discover -s tests`
- `git diff --check`
- `bash scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0034-task-centric-knowledge-upgrade-completion/task.md knowledge/tasks/TASK-2026-0034-task-centric-knowledge-upgrade-completion/plan.md knowledge/operations/task-centric-knowledge-upgrade.md`

### Остаётся на ручную проверку

- `не требуется`

## Критерии готовности

- `knowledge/operations/task-centric-knowledge-upgrade.md` отражает фактический набор legacy-задач текущего репозитория;
- все pending legacy entries доведены до `note-only`, `compatibility-backfilled` или `manual-reference`;
- repo-level status перешёл в `fully-upgraded`, а rollout — в `single-writer`;
- historical task-truth не переписан вне allowlisted migration note;
- verify-контур install/backfill не содержит runtime-regressions.

## Итоговый список ручных проверок

- `не требуется`

## Итог

Для текущего репозитория завершён полный governed upgrade-контур:
`install check -> install apply --force -> doctor-deps -> cleanup-plan -> compatibility-backfill`.

`install apply --force` пересобрал repo upgrade-state и раскрыл фактический pending scope:
вместо прежних `25` entries state теперь честно включил `TASK-2026-0028`, `TASK-2026-0032`, `TASK-2026-0033` и текущую `TASK-2026-0034`,
поэтому общий pending set составил `29` задач.

По всем historical entries выполнен `note-only compatibility-backfill`:
созданы task-local migration notes в `artifacts/migration/task-centric-knowledge-upgrade.md`,
а protected narrative и historical metadata не переписывались.
Для текущей активной `TASK-2026-0034` выполнен `compatibility-backfilled` path,
чтобы repo upgrade-state смог дойти до нулевого pending count без скрытых исключений.

Итоговое состояние подтверждено локально:
`compatibility_epoch=module-core-v1`,
`upgrade_status=fully-upgraded`,
`execution_rollout=single-writer`,
`legacy_pending_count=0`,
`reference_manual_count=0`.
`cleanup-plan` сохранил `TARGET_COUNT=0` и `COUNT=0`,
полный `python3 -m unittest discover -s tests` прошёл (`232 tests`, `OK`),
`git diff --check` чист,
а localization guard прошёл по полному Markdown-scope, включая новые migration notes.

Во время verify выявился только один пользовательский doc-drift после managed refresh:
в `knowledge/tasks/README.md` оставалось bare-слово `handoff`.
Оно переведено в русскоязычный user-facing текст,
при этом машинно-значимый literal `handoff.md` сохранён.
