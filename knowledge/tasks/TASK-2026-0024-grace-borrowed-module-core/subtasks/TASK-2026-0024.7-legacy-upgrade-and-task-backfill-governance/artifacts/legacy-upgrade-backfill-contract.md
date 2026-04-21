# Контракт legacy upgrade и compatibility-backfill

## Назначение

Этот артефакт фиксирует реализованный governed-контур для `TASK-2026-0024.7`:

- репозиторное состояние upgrade/backfill;
- explicit compatibility-backfill вместо implicit sync-магии;
- различение `active`, `closed historical` и `reference`;
- rollout execution-политики от `legacy` к `single-writer`.

## Канонические сущности

### Репозиторное состояние upgrade/backfill

Канонический путь:

- `knowledge/operations/task-centric-knowledge-upgrade.md`

Канонический паспорт:

- поле `Система`
- поле `Эпоха совместимости`
- поле `Статус upgrade`
- поле `Execution rollout`
- поле `Последняя задача перехода`
- поле `Дата обновления`

Каноническая таблица `Legacy tasks`:

- колонка `TASK-ID`
- колонка `Класс`
- колонка `Статус backfill`
- колонка `Migration note`
- колонка `Решение`

### Эпохи совместимости

- эпоха `legacy-v1` означает, что совместимая старая knowledge-система ещё не переведена в governed Module Core rollout.
- эпоха `module-core-v1` означает, что repo уже материализовал новый governed upgrade-state и перешёл на новую эпоху.

### Repo-level статусы

- статус `legacy-compatible` означает, что repo ещё в `legacy-v1`.
- статус `partially-upgraded` означает, что repo уже в `module-core-v1`, но есть хотя бы одна `pending` legacy-задача или rollout ещё не `single-writer`.
- статус `fully-upgraded` означает, что repo уже в `module-core-v1`, pending backlog исчерпан, rollout=`single-writer`.

### Статусы rollout execution-контура

- режим `legacy` означает, что Module Core не участвует в writer gate.
- режим `dual-readiness` означает, что governed read-model и readiness уже доступны, но legacy/backfill backlog ещё не исчерпан.
- режим `single-writer` означает, что writer-pass опирается на governed `ExecutionReadiness`, `VerificationExcerpt` и `FailureHandoff`.

## Классификация задач

- `active` — задача не в финальном статусе.
- `closed historical` — задача в статусе `завершена` или `отменена` и не имеет marker `Справочный режим = reference`.
- `reference` — задача явно помечена полем `Справочный режим = reference`.

Любое другое значение `Справочный режим` считается неканоническим и поднимает warning `reference_mode_invalid`.

## Управляемый compatibility-backfill

### Обычный sync

Обычный `workflow sync` не меняет policy из `TASK-2026-0024.7.1`:

- historical safe-sync остаётся registry-only режимом;
- protected fields закрытых задач не переписываются;
- ordinary sync не превращается в migration/backfill режим.

### Явный backfill

Новый governed вход:

- через unified CLI: `task-knowledge workflow backfill --project-root /abs/project --task-dir /abs/project/knowledge/tasks/TASK-... --scope compatibility`
- через facade-скрипт: `python3 scripts/task_workflow.py --project-root /abs/project --task-dir /abs/project/knowledge/tasks/TASK-... --backfill-scope compatibility`

Поведение по классам:

- `active`:
  - создаётся task-local migration note;
  - repo upgrade-state переводит строку задачи в `compatibility-backfilled`;
  - затем допускается controlled `sync_task` для allowlisted summary/branch metadata.
- `closed historical`:
  - создаётся только task-local migration note;
  - repo upgrade-state переводит строку задачи в `note-only`;
  - `task.md` не меняет protected fields и narrative.
- `reference`:
  - task-local файлы не мутируются автоматически;
  - repo upgrade-state переводит строку задачи в `manual-reference`.

## Task-local migration note задачи

Канонический путь:

- `<task-dir>/artifacts/migration/task-centric-knowledge-upgrade.md`

Канонические поля note:

- поле `Эпоха до`
- поле `Эпоха после`
- поле `Класс legacy`
- поле `Основание/задача`
- поле `Дата обновления`

Обязательные секции:

- раздел `Что обновлено`
- раздел `Что не трогалось`

## Диагностика и read-only отчётность

### Поля install/check/doctor payload

Во все install/governance payload'ы добавлены:

- поле `compatibility_epoch`
- поле `upgrade_status`
- поле `execution_rollout`
- поле `legacy_pending_count`
- поле `reference_manual_count`

### Warning-коды `task status`

`task status` поднимает:

- `legacy_backfill_pending` — в repo upgrade-state ещё есть `pending`;
- `reference_backfill_manual` — есть строки `manual-reference`;
- `execution_rollout_partial` — repo уже не в `legacy-compatible`, но rollout ещё не `single-writer`.

## Инварианты

- repo upgrade-state не подменяет `Task Core` source-of-truth;
- ordinary sync и explicit backfill остаются разными режимами;
- `closed historical` не получает narrative rewrite;
- `reference` определяется только явной пометкой;
- `manual-reference` не считается pending backlog;
- `fully-upgraded` допустим при наличии `manual-reference` и `note-only`, если больше нет `pending`.

## Проверки реализации

- `python3 -m unittest skills-global/task-centric-knowledge/tests/test_install_skill.py`
- `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_query.py`
- `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_workflow.py`
- `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_knowledge_cli.py`
