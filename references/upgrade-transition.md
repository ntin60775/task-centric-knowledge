# Безопасное обновление старой версии навыка

## Цель перехода

Обновление старой версии `task-centric-knowledge` на новую должно:

- не ломать уже созданные task-данные;
- не плодить дубликаты managed-блоков и managed-файлов;
- сохранять смысл и структуру существующих задач;
- ясно фиксироваться в локальном git как отдельный момент перехода.

## Что считать защищёнными данными проекта

При обновлении нельзя молча портить или перезаписывать:

- существующие каталоги `knowledge/tasks/<TASK-ID>-<slug>/`;
- `task.md`, `plan.md`, `sdd.md`, `worklog.md`, `decisions.md`, `handoff.md` внутри уже созданных задач;
- `knowledge/tasks/registry.md` как project data;
- `knowledge/modules/registry.md` как project data;
- пользовательские разделы вне managed-блока в `AGENTS.md`.

## Локальный порядок обновления

1. Открыть задачу или подзадачу именно под переход версии.
2. Работать сначала только в локальном git.
3. Убедиться, что рабочее дерево не содержит несвязанных изменений.
4. Убедиться, что глобальная live-copy обновлена и проверена:

```bash
make verify-global-install
```

5. Запустить проектную проверку от verified live-copy:

```bash
task-knowledge install check --project-root /abs/project --source-root ~/.agents/skills/task-centric-knowledge
```

6. Если проект совместим и нужен именно upgrade managed-ресурсов, выполнить:

```bash
task-knowledge install apply --project-root /abs/project --source-root ~/.agents/skills/task-centric-knowledge --force
task-knowledge install verify-project --project-root /abs/project --source-root ~/.agents/skills/task-centric-knowledge --force
```

7. Проверить, что:

- `registry.md` не потерял project data;
- существующие каталоги задач не изменились вне ожидаемого scope;
- managed-блок в `AGENTS.md` не продублировался;
- повторный запуск не создаёт повторных блоков и повторных артефактов;
- installer не сообщил `symlink` или managed-path outside project.

8. После install/force прогнать diagnostics:

```bash
task-knowledge install doctor-deps --project-root /abs/project --source-root ~/.agents/skills/task-centric-knowledge
```

`doctor-deps` должен явно показать, что блокирует `core/local mode`, а что относится только к `publish/integration`.
Начиная с эпохи `module-core-v1` diagnostics также показывают поля:

совместимости `compatibility_epoch`, `upgrade_status`, `execution_rollout`,
а также счётчики `legacy_pending_count` и `reference_manual_count`.

Для совместимой legacy-репы без materialized upgrade-state ожидаемое начальное состояние:

- поле `compatibility_epoch` имеет значение `legacy-v1`
- поле `upgrade_status` имеет значение `legacy-compatible`
- поле `execution_rollout` имеет значение `legacy`
9. Если переход оставил installer-generated миграционные хвосты, сначала показать cleanup-plan:

```bash
task-knowledge install cleanup-plan --project-root /abs/project
```

Проверить, что auto-delete scope ограничен только ожидаемыми артефактами (`knowledge/MIGRATION-SUGGESTION.md` и/или `AGENTS.task-centric-knowledge.<profile>.md`) и не затрагивает `project data`.
Если по allowlist-пути лежит symlink, каталог или другой неожиданный тип объекта, такой путь должен уйти в `manual_review`, а не в `safe_delete`.
10. Только после этого, если план корректен, выполнить confirm-команду из самого плана:

```bash
task-knowledge install cleanup-confirm --project-root /abs/project --confirm-fingerprint <sha256> --yes
```

Если fingerprint, `TARGETS`, `TARGET_COUNT` или `COUNT` изменились, cleanup нужно остановить и заново показать план.

## Как разносить переход в git

Переход должен быть явно виден в локальном git.

Рекомендуемый порядок:

1. Отдельный task-scoped commit только под upgrade-переход.
2. В этом commit должны лежать только изменения, которые относятся к обновлению skill-а, managed-ресурсов, migration-note, тестов и playbook-а перехода.
3. Последующие рабочие изменения делать отдельными commit-ами, а не смешивать с моментом перехода.

Именно этот отдельный upgrade-commit считается точкой перехода версии в git.

## Repo upgrade-state и эпохи совместимости

Новая governed-модель фиксирует upgrade не только через commit,
но и через репозиторное состояние по пути `knowledge/operations/task-centric-knowledge-upgrade.md`.

Канонические эпохи:

- эпоха совместимости `legacy-v1`
- эпоха совместимости `module-core-v1`

Канонические repo-level статусы:

- статус `legacy-compatible`
- статус `partially-upgraded`
- статус `fully-upgraded`

Канонические rollout-статусы:

- rollout-режим `legacy`
- rollout-режим `dual-readiness`
- rollout-режим `single-writer`

Рекомендуемый порядок:

1. До `install --force` проверить, что repo действительно ещё в legacy-compatible состоянии.
2. Выполнить `install --force`.
3. Убедиться, что materialized upgrade-state создан или обновлён.
4. Если в нём есть `pending` строки, не считать переход завершённым.
5. Доводить legacy-задачи через explicit backfill-режим, а не через обычный sync.

## Классы legacy-задач

- `active` — статус не финальный.
- `closed historical` — статус `завершена` или `отменена`, если нет явной reference-пометки.
- `reference` — только задача с явным полем `Справочный режим = reference`.

Эвристически считать historical-задачу справочной запрещено.

## Управляемый backfill

Обычный `workflow sync` и governed backfill — разные режимы.

Обычный sync:

- не становится migration helper;
- сохраняет policy historical safe-sync;
- не трогает protected fields закрытых задач.

Governed backfill выполняется одной из двух команд:

- через unified CLI: `task-knowledge workflow backfill --project-root /abs/project --task-dir /abs/project/knowledge/tasks/TASK-... --scope compatibility`
- через facade-скрипт: `task-knowledge workflow backfill --project-root /abs/project --task-dir /abs/project/knowledge/tasks/TASK-... --scope compatibility`

`--task-dir` может быть относительным или абсолютным, но после `resolve()` обязан оставаться внутри `project_root`. Symlinked task directory, ведущий за пределы проекта, является blocker-ом и не должен мутировать `task.md` или registry.

Результат по классам:

- класс `active` переводится в статус `compatibility-backfilled`
- класс `closed historical` переводится в статус `note-only`
- класс `reference` переводится в статус `manual-reference`

## Заметка о миграции

Для `active` и `closed historical` governed backfill создаёт task-local note
по пути `artifacts/migration/task-centric-knowledge-upgrade.md`.

Этот note фиксирует:

- эпоху до и после;
- класс legacy-задачи;
- что обновлено;
- что не трогалось;
- задачу-основание перехода.

## Как обращаться с remote

- Приоритет у локального git.
- Нельзя предлагать `push`, пока не проверено наличие связанного удалённого репозитория.
- Проверка выполняется через `git remote` или `git remote -v`.
- Если remote нет, работа остаётся локальной и разговор про `push` не поднимается.
- Если remote есть, `push` можно предложить только после того, как локальный переход уже проверен и зафиксирован отдельным commit-ом.

## Стоп-условия

- Обнаружены несвязанные локальные изменения.
- Неясно, какие существующие task-данные будут затронуты.
- Update требует разрушающих git-действий.
- После повторного запуска появляются дубликаты managed-блоков или неоднозначность в целевом состоянии.
- Installer или workflow helper сообщает `symlink`, `blocked-target-symlink`, `blocked-target-outside-root` или `task_dir_outside_project_root`.
