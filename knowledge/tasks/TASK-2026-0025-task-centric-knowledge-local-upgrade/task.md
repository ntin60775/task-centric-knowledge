# Карточка задачи TASK-2026-0025

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0025` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0025` |
| Технический ключ для новых именуемых сущностей | `knowledge-upgrade` |
| Краткое имя | `task-centric-knowledge-local-upgrade` |
| Человекочитаемое описание | `Обновить managed knowledge-систему этого репозитория до текущей версии skill-а task-centric-knowledge без потери project data.` |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `main` |
| Требуется SDD | `нет` |
| Статус SDD | `не требуется` |
| Ссылка на SDD | `—` |
| Дата создания | `2026-04-20` |
| Дата обновления | `2026-04-21` |

## Цель

Локально обновить managed-ресурсы `task-centric-knowledge` в текущем репозитории
до актуальной версии,
сформировать состояние перехода репозитория эпохи `module-core-v1`,
сохранив `project data`, существующие task-каталоги и пользовательские разделы вне managed-блока `AGENTS.md`.

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

## Git-подсказка

- Поле `Ветка` хранит текущую активную ветку рабочего контекста, а не обязательную долгоживущую task-ветку.
- При открытии верхнеуровневой задачи стартовый контекст обычно синхронизируется в `task/<task-id-lower>-<slug>`.
- Для первой и последующих поставок helper может переводить `Ветка` в delivery-ветку вида `du/<task-id-lower>-uNN-<slug>`.
- Для подзадачи по умолчанию можно указывать ветку родителя, если отдельная ветка или delivery unit не нужны.
- При каждом создании или переключении ветки нужно синхронизировать это поле и строку в `registry.md`.

## Границы

### Входит

- локальная диагностика `check` и `doctor-deps` для текущего project-root;
- обновление managed knowledge-файлов и managed-блока `AGENTS.md` через `install --force`;
- фиксация и устранение CLI-regression, если post-upgrade verify-контур ломается на штатной governance-команде;
- проверка, что `knowledge/tasks/registry.md` и уже существующие каталоги задач не потеряли project data;
- materialization `knowledge/operations/task-centric-knowledge-upgrade.md` и фиксация pending legacy-backfill как repo-level состояния;
- проверка cleanup-governance через `migrate-cleanup-plan`;
- локализационная проверка новых task-артефактов этой задачи.

### Не входит

- публикация изменений в remote, `push` и PR/MR;
- массовое переписывание существующих task-артефактов как части новой версии;
- controlled compatibility-backfill legacy-задач;
- реализация новых capability вне verify/governance-контура upgrade.

## Контекст

- источник постановки: пользовательский запрос от `2026-04-21` обновить систему в этом репозитории через skill `task-centric-knowledge`;
- связанная бизнес-область: локальный upgrade knowledge-системы и managed governance;
- ограничения и зависимости: upgrade должен идти отдельным task-scoped переходом, не должен повреждать `project data` и не должен запускать mass backfill legacy-задач без отдельного решения;
- исходный наблюдаемый симптом / лог-маркер: текущий репозиторий сначала классифицировался как `compatible / legacy-compatible`, а после `install --force` перешёл в `module-core-v1 / partially-upgraded / dual-readiness` с `legacy_pending_count=24`;
- основной контекст сессии: `обновление локальной knowledge-системы до актуальной версии skill-а`

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | `scripts/install_skill_runtime/cli.py` и `tests/test_install_skill_governance.py` для фикса text-mode cleanup formatter |
| Конфигурация / схема данных / именуемые сущности | материализованные managed-файлы, managed-блок `AGENTS.md`, `knowledge/operations/task-centric-knowledge-upgrade.md` |
| Интерфейсы / формы / страницы | text-репорт install/governance CLI для `migrate-cleanup-plan` |
| Интеграции / обмены | локальный install/upgrade контур skill-а и repo-level upgrade governance |
| Документация | task-local артефакты `TASK-2026-0025` и состояние перехода репозитория |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0025-task-centric-knowledge-local-upgrade/`
- файл плана: `plan.md`
- файл SDD: `—`
- файл verification matrix: `—`
- состояние перехода репозитория: `knowledge/operations/task-centric-knowledge-upgrade.md`
- безопасный порядок upgrade: `references/upgrade-transition.md`
- skill-источник upgrade: `/home/prog7/.agents/skills/task-centric-knowledge/`
- пользовательские материалы: сообщение пользователя от `2026-04-21`
- связанные коммиты / PR / ветки: `task/task-2026-0025-task-centric-knowledge-local-upgrade`
- связанные операции в `knowledge/operations/`, если есть: `knowledge/operations/task-centric-knowledge-upgrade.md`

## Контур публикации

Delivery unit для локального upgrade пока не требуется.

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | — | `—` | `—` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |

## Текущий этап

Локальный finalize выполнен: task-ветка влита в base-ветку, рабочий контекст переведён на base-ветку, `push` остаётся отдельным шагом.
## Стратегия проверки

### Покрывается кодом или тестами

- `python3 /home/prog7/.agents/skills/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --mode check`
- `python3 /home/prog7/.agents/skills/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --mode install --force`
- `python3 /home/prog7/.agents/skills/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --mode doctor-deps`
- `python3 scripts/install_skill.py --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --mode check`
- `python3 scripts/install_skill.py --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --mode migrate-cleanup-plan`
- `python3 -m unittest tests.test_install_skill_governance.InstallSkillGovernanceTests.test_migrate_cleanup_plan_text_cli_does_not_require_upgrade_fields tests.test_install_skill_governance.InstallSkillGovernanceTests.test_migrate_cleanup_plan_discloses_scope_and_protected_paths`
- `python3 -m unittest discover -s tests`
- `git diff --check`
- `bash scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0025-task-centric-knowledge-local-upgrade/task.md knowledge/tasks/TASK-2026-0025-task-centric-knowledge-local-upgrade/plan.md knowledge/operations/task-centric-knowledge-upgrade.md`

### Остаётся на ручную проверку

- `не требуется`

## Критерии готовности

- managed knowledge-контур обновлён до текущего skill-source;
- состояние перехода репозитория зафиксировало `module-core-v1 / partially-upgraded / dual-readiness`;
- `project data` и существующие task-каталоги не повреждены;
- `migrate-cleanup-plan` работает в text-режиме и не расширяет cleanup scope;
- `legacy_pending_count=24` отражён как осознанный pending-backfill, а не как silent rewrite historical tasks;
- diff не содержит структурных ошибок.

## Итоговый список ручных проверок

- `не требуется`

## Итог

Для текущего репозитория выполнен безопасный upgrade-контур
`check -> install --force -> doctor-deps -> migrate-cleanup-plan`.
Installer обновил managed-scope без повреждения `project data`,
создал `knowledge/operations/task-centric-knowledge-upgrade.md`
и перевёл репозиторий в состояние
`compatibility_epoch=module-core-v1`,
`upgrade_status=partially-upgraded`,
`execution_rollout=dual-readiness`,
`legacy_pending_count=24`.

Во время verify обнаружилась регрессия runtime CLI:
`migrate-cleanup-plan` падал в text-режиме с `KeyError: 'compatibility_epoch'`,
потому что formatter безусловно ожидал upgrade-поля в cleanup payload.
Регрессия исправлена в `scripts/install_skill_runtime/cli.py`,
закрыта регрессионным тестом
`test_migrate_cleanup_plan_text_cli_does_not_require_upgrade_fields`
и подтверждена повторным успешным запуском `migrate-cleanup-plan`.

Cleanup-governance после фикса подтверждён:
`TARGET_COUNT=0`, `COUNT=0`,
safe-delete объектов нет,
а historical задачи оставлены нетронутыми до отдельного controlled backfill.
