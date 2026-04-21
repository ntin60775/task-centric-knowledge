# Adoption package по результатам field validation

Этот артефакт фиксирует не теоретический quickstart, а порядок действий,
который был реально проверен на `clean`, `mixed_system` и `compatible/1c`.

Публичная версия пакета синхронизирована в `skills-global/task-centric-knowledge/references/adoption.md`.

## 1. Общий порядок

1. Выполнить `check` для подходящего профиля.
2. Выполнить `install` или `install --force` / `install --existing-system-mode migrate` по классу среды.
3. Сразу после установки прогнать `doctor-deps`.
4. Если среда миграционная или upgrade-среда, показать `migrate-cleanup-plan`, но не выполнять delete без отдельного workflow.
5. Только после этого переходить к task lifecycle и operator CLI.

## 2. Чистая установка

Проверенный набор команд:

```bash
python3 scripts/install_skill.py --project-root /abs/project --mode check --format json
python3 scripts/install_skill.py --project-root /abs/project --mode install
python3 scripts/install_skill.py --project-root /abs/project --mode doctor-deps --format json
python3 scripts/task_query.py --project-root /abs/project status --format json
```

Что подтверждено:

- если `AGENTS.md` отсутствует, installer создаёт `AGENTS.task-centric-knowledge.<profile>.md`, а не пишет новый `AGENTS.md` молча;
- после `install` task-контур ещё пуст, и это честно видно через `task_query status`.

### Bootstrap первой задачи после clean install

Прямой путь:

```bash
python3 scripts/task_workflow.py --project-root /abs/project --task-dir knowledge/tasks/<TASK-ID>-<slug> --create-branch --register-if-missing --summary "..."
```

не является универсально безопасным для самого первого task bootstrap,
если `install` и создание первых task-файлов уже сделали рабочее дерево грязным.
Field validation подтвердила реальный stop-signal helper-а:
`Рабочее дерево грязное; автоматическое переключение task-ветки остановлено.`

Проверенный порядок для первой задачи:

```bash
git checkout -b task/<task-id-lower>-<slug>
mkdir -p knowledge/tasks/<TASK-ID>-<slug>
cp knowledge/tasks/_templates/task.md knowledge/tasks/<TASK-ID>-<slug>/task.md
cp knowledge/tasks/_templates/plan.md knowledge/tasks/<TASK-ID>-<slug>/plan.md
python3 scripts/task_workflow.py --project-root /abs/project --task-dir knowledge/tasks/<TASK-ID>-<slug> --register-if-missing --summary "..."
python3 scripts/task_query.py --project-root /abs/project current-task --format json
python3 scripts/task_query.py --project-root /abs/project task show <TASK-ID> --format json
```

Смысл:

- task-ветка создаётся явно;
- helper больше не пытается переключать ветку на dirty tree;
- helper синхронизирует `task.md`, `registry.md` и branch metadata;
- `current-task` и `task show` сразу проверяют operator UX.

## 3. Миграция `mixed_system`

Проверенный набор команд:

```bash
python3 scripts/install_skill.py --project-root /abs/project --mode check --format json
python3 scripts/install_skill.py --project-root /abs/project --mode install --existing-system-mode migrate
python3 scripts/install_skill.py --project-root /abs/project --mode doctor-deps --format json
python3 scripts/install_skill.py --project-root /abs/project --mode migrate-cleanup-plan --format json
```

Что подтверждено:

- installer materializes `knowledge/MIGRATION-SUGGESTION.md` и не пытается переносить legacy-контуры автоматически;
- `migrate-cleanup-plan` может вернуть `target_count=0`, `count=0` и при этом оставить legacy-контуры в `manual_review`;
- отсутствие auto-delete target-ов в таком сценарии является ожидаемым governance behavior, а не ошибкой.

## 4. Совместимое обновление / `1c`

Проверенный набор команд:

```bash
python3 scripts/install_skill.py --project-root /abs/project --mode check --profile 1c --format json
python3 scripts/install_skill.py --project-root /abs/project --mode install --force --profile 1c
python3 scripts/install_skill.py --project-root /abs/project --mode doctor-deps --profile 1c --format json
python3 scripts/install_skill.py --project-root /abs/project --mode migrate-cleanup-plan --profile 1c --format json
python3 scripts/task_query.py --project-root /abs/project status --format json
python3 scripts/task_query.py --project-root /abs/project current-task --format json
```

Что подтверждено:

- `registry.md` сохраняется как project data даже при `--force`;
- cleanup-plan ограничивается allowlist-артефактами и не трогает task-каталоги;
- для больших `1c`-репозиториев governance/adoption validation можно проводить через sparse-checkout `AGENTS.md + knowledge/**`,
  потому что install/upgrade/read-model не требуют полного продуктового checkout.

## 5. Operator UX, который нужно считать нормой

- на shared `main` в заселённых knowledge-репозиториях `current-task` может возвращать `ambiguous/branch_tie`;
- это нормальный warning-first режим, если на ветке несколько задач с совпадающим `branch=main`;
- legacy `summary_fallback_goal`, `summary_drift`, `registry_row_missing`, `next_step_missing` должны восприниматься как наблюдаемые сигналы качества данных,
  а не как повод молча выбрать задачу за пользователя.
