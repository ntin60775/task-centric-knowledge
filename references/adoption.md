# Пакет внедрения и проверенный старт

Этот документ описывает не теоретический onboarding, а порядок действий,
проверенный на трёх классах сред в `TASK-2026-0014`:

- `clean/generic`
- `mixed_system/generic`
- `compatible/1c`

Если перед применением playbook нужно быстро восстановить семантику ядра,
source-of-truth и допустимые warning-first сценарии,
используй `references/core-model.md` как первичный дистрибутивный contract.

## 1. Когда использовать этот playbook

- когда нужно развернуть `task-centric-knowledge` в новом проекте;
- когда нужно обновить совместимую knowledge-систему в существующем проекте;
- когда нужно мигрировать смешанную или чужую систему хранения;
- когда нужно понять, чего ожидать от `status/current-task` на shared `main`.

## 2. Общий validated порядок

```bash
python3 scripts/install_skill.py --project-root /abs/project --mode check
python3 scripts/install_skill.py --project-root /abs/project --mode install
python3 scripts/install_skill.py --project-root /abs/project --mode doctor-deps
```

Для `mixed_system`:

```bash
python3 scripts/install_skill.py --project-root /abs/project --mode install --existing-system-mode migrate
python3 scripts/install_skill.py --project-root /abs/project --mode migrate-cleanup-plan
```

Для `compatible/1c`:

```bash
python3 scripts/install_skill.py --project-root /abs/project --mode check --profile 1c
python3 scripts/install_skill.py --project-root /abs/project --mode install --force --profile 1c
python3 scripts/install_skill.py --project-root /abs/project --mode doctor-deps --profile 1c
python3 scripts/install_skill.py --project-root /abs/project --mode migrate-cleanup-plan --profile 1c
```

## 3. Чистая установка: чего ожидать

- если `AGENTS.md` отсутствует, installer создаёт `AGENTS.task-centric-knowledge.<profile>.md`, а не редактирует новый `AGENTS.md` молча;
- после `install` task-контур может быть ещё пустым, и это нормально;
- `task_query status` в этот момент должен честно вернуть `current_task_unresolved/no_tasks`.

Проверка:

```bash
python3 scripts/task_query.py --project-root /abs/project status --format json
```

## 4. Первый task bootstrap после clean install

Прямой запуск:

```bash
python3 scripts/task_workflow.py --project-root /abs/project --task-dir knowledge/tasks/<TASK-ID>-<slug> --create-branch --register-if-missing --summary "..."
```

не является универсально безопасным для самой первой задачи,
если `install` и создание первых task-файлов уже сделали рабочее дерево грязным.
Field validation подтвердила stop-signal helper-а на dirty tree.

Validated порядок для первой задачи:

```bash
git checkout -b task/<task-id-lower>-<slug>
mkdir -p knowledge/tasks/<TASK-ID>-<slug>
cp knowledge/tasks/_templates/task.md knowledge/tasks/<TASK-ID>-<slug>/task.md
cp knowledge/tasks/_templates/plan.md knowledge/tasks/<TASK-ID>-<slug>/plan.md
python3 scripts/task_workflow.py --project-root /abs/project --task-dir knowledge/tasks/<TASK-ID>-<slug> --register-if-missing --summary "..."
python3 scripts/task_query.py --project-root /abs/project current-task --format json
python3 scripts/task_query.py --project-root /abs/project task show <TASK-ID> --format json
```

Смысл этого порядка:

- ветка создаётся явно и больше не зависит от helper-переключения на dirty tree;
- helper синхронизирует `task.md`, `registry.md` и branch metadata;
- read-model сразу проверяет, что задача видна оператору.

## 5. Миграция `mixed_system`

Ожидаемое поведение:

- installer создаёт `knowledge/MIGRATION-SUGGESTION.md`;
- старые контуры хранения не переносятся автоматически;
- `migrate-cleanup-plan` может вернуть `target_count=0` и при этом показать legacy-контуры в `manual_review`.

Это не ошибка: governance специально не удаляет чужие или смешанные контуры молча.

## 6. Совместимое обновление / `1c`

Ожидаемое поведение:

- `--force` обновляет managed-шаблоны;
- `knowledge/tasks/registry.md` остаётся project data;
- `migrate-cleanup-plan` ограничивается allowlist-артефактами вроде `knowledge/MIGRATION-SUGGESTION.md`.

Для больших `1c`-репозиториев governance/adoption validation допускает sparse-checkout
`AGENTS.md + knowledge/**` на обычной файловой системе.
Полный checkout bulky-репозитория не обязателен для проверки install/upgrade/read-model UX
и может быть неоптимален в `tmpfs`.

## 7. Operator UX на shared `main`

Если в репозитории уже много задач с `branch=main`, команды:

```bash
python3 scripts/task_query.py --project-root /abs/project status --format json
python3 scripts/task_query.py --project-root /abs/project current-task --format json
```

могут вернуть `ambiguous/branch_tie` и поднять legacy warnings (`summary_drift`, `registry_row_missing`, `next_step_missing`).

Это ожидаемое warning-first поведение read-model:

- CLI не выбирает задачу молча;
- ambiguity считается сигналом оператору, а не runtime-регрессией.

Для parent/subtask на общей ветке действует более точное правило:
если все branch-кандидаты являются одним parent aggregate,
`current-task` и `status` выбирают родительскую задачу.
Если dirty-scope указывает на конкретную подзадачу, read-model выбирает её через `branch+dirty`.
