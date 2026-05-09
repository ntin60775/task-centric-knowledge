# SDD по задаче TASK-2026-0043

## Паспорт SDD

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0043` |
| Статус | `черновик` |
| Версия | `1` |
| Дата обновления | `2026-05-06` |

## 0. Инварианты и verification matrix

### Полный invariant set

- `INV-01`: `task-knowledge bootstrap` выполняет полный цикл одной командой, без необходимости ручного создания ветки или каталога.
- `INV-02`: `--dry-run` показывает полный план действий (какие файлы будут созданы, какие команды выполнены) без мутации файловой системы или git.
- `INV-03`: На чистом проекте bootstrap создаёт knowledge-систему, делает commit knowledge-файлов, создаёт ветку и первую задачу.
- `INV-04`: На проекте с существующей knowledge-системой (чистой или совместимой) bootstrap либо обновляет её, либо сообщает о несовместимости.
- `INV-05`: Если дерево грязное НЕ knowledge-файлами, bootstrap не коммитит чужие изменения.
- `INV-06`: Если проект не git-репозиторий, bootstrap явно сообщает об этом и останавливается.
- `INV-07`: Профиль `1c` корректно применяется (managed-блок, файлы шаблонов).
- `INV-08`: После успешного bootstrap `task-knowledge task status` возвращает корректный статус.

### Связанные артефакты проверки

- `artifacts/verification-matrix.md`.

## 1. Проблема и цель

### Проблема

Валидированный порядок первого bootstrap после clean install (`references/adoption.md §4`) требует:

```bash
git checkout -b task/<task-id-lower>-<slug>
mkdir -p knowledge/tasks/<TASK-ID>-<slug>
cp knowledge/tasks/_templates/task.md knowledge/tasks/<TASK-ID>-<slug>/task.md
cp knowledge/tasks/_templates/plan.md knowledge/tasks/<TASK-ID>-<slug>/plan.md
python3 scripts/task_workflow.py --project-root /abs/project --task-dir ... --register-if-missing --summary "..."
```

Хотя агент может выполнить эти команды, нет единой команды `bootstrap`, которая сделает всё это атомарно с правильной обработкой dirty tree, существующих систем и edge cases.

### Цель

Единая детерминированная команда `task-knowledge bootstrap` для агента без интерактивных шагов.

## 2. Архитектура и границы

### Bootstrap flow

```
task-knowledge bootstrap --project-root /abs --profile generic [--dry-run] [--first-task-id TASK-2026-0001] [--first-task-name "initial-setup"]
```

1. **Preflight**: проверить git-репозиторий, определить dirty paths.
2. **Install check**: `install check` — валидация проекта.
3. **Install apply**: `install apply --force --existing-system-mode abort` (или `adopt` если система совместима).
4. **Doctor-deps**: `doctor-deps` — проверка зависимостей.
5. **Commit knowledge files**: если дерево грязное только knowledge-файлами → авто-commit с сообщением `task-knowledge bootstrap: initial setup`.
6. **Create first task**: создать каталог задачи из шаблонов.
7. **Workflow sync**: `workflow sync --create-branch --register-if-missing`.

### Обработка dirty tree

| Dirty paths | Действие |
|-------------|----------|
| Только `knowledge/**`, `AGENTS.md` | Авто-commit `task-knowledge bootstrap: initial knowledge setup` |
| Смешанные (knowledge + чужие) | Ошибка: дерево грязное чужими изменениями |
| Чистое дерево | Продолжить без commit |

### Обработка существующей системы

| Классификация | Действие |
|---------------|----------|
| `clean` | Полная установка |
| `compatible` | Обновление managed-файлов (`--force`) |
| `partial_knowledge` | Ошибка: требуется ручное решение (adopt vs migrate) |
| `foreign_system` / `mixed_system` | Ошибка: требуется миграция |

### Что остаётся вне задачи

- Интерактивные wizard.
- Миграция существующих систем хранения.
- Пользовательское содержимое задачи (только шаблоны).

### Допустимые и недопустимые связи

**Допустимые:**
- `bootstrap.py` → `install_runtime` (check, install, doctor_deps).
- `bootstrap.py` → `workflow_runtime` (sync_task).

**Недопустимые:**
- `bootstrap.py` не должен дублировать логику install или workflow.

### Новые зависимости и их обоснование

`нет`

### Наблюдаемые сигналы и диагностические маркеры

`не требуется`

## 3. Изменения данных / схемы / metadata

`нет`

## 4. Новые сущности и интерфейсы

### `task_knowledge/bootstrap.py`

Функции:
- `bootstrap(project_root, *, profile, dry_run, first_task_id, first_task_name) -> dict` — основная функция.
- `_bootstrap_preflight(project_root) -> dict` — preflight проверки.
- `_bootstrap_install(project_root, source_root, profile) -> dict` — install check + apply.
- `_bootstrap_first_task(project_root, task_id, task_name) -> dict` — создание первой задачи.
- `_bootstrap_commit_knowledge(project_root) -> dict` — commit knowledge-файлов.

### CLI подкоманда `bootstrap`

```
task-knowledge bootstrap --project-root PATH [--profile generic|1c] [--dry-run] [--first-task-id ID] [--first-task-name NAME]
```

## 5. Изменения в существующих компонентах

### `src/task_knowledge/cli.py`

- Добавить `_add_bootstrap_command()` в `build_parser()`.
- Добавить `_bootstrap(args)` обработчик.
- Добавить `bootstrap` в `SUPPORTED_COMMANDS`.

### `src/task_knowledge/workflow_runtime/sync_flow.py` (возможно)

- Опционально: добавить параметр `auto_commit_dirty_knowledge` в `sync_task` для автоматического commit-а knowledge-файлов перед sync.

## 6. Этапы реализации и проверки

### Этап 1: Проектирование

- Детализировать bootstrap flow.
- Определить все edge cases (dirty tree, существующая система, нет git, нет прав).
- Verify: ревью SDD, проверка через `semantic-algorithm-design` skill.
- Аудит: `SDD_AUDIT`.

### Этап 2: Реализация bootstrap.py

- Создать `src/task_knowledge/bootstrap.py`.
- Реализовать `bootstrap()` и вспомогательные функции.
- Verify: `python3 -c "from task_knowledge.bootstrap import bootstrap"`.
- Аудит: `IMPLEMENTATION_AUDIT`.

### Этап 3: Интеграция в CLI

- Добавить подкоманду `bootstrap` в `cli.py`.
- Реализовать `--dry-run`, `--profile`.
- Verify: `task-knowledge bootstrap --help`.
- Аудит: `IMPLEMENTATION_AUDIT`.

### Этап 4: Тестирование

- Написать тесты bootstrap в `tests/`.
- Покрыть clean проект, dirty tree, существующую систему, отсутствие git.
- Verify: `python3 -m unittest discover -s tests -v`.
- Аудит: `IMPLEMENTATION_AUDIT`.

### Этап 5: Обновление документации

- `references/adoption.md`: заменить §4 на `task-knowledge bootstrap`.
- `README.md`: добавить пример.
- Verify: `grep "task-knowledge bootstrap" references/adoption.md README.md`.
- Аудит: `IMPLEMENTATION_AUDIT`.

### Финальный этап: Интеграция

- Полный тестовый прогон.
- `make check`.
- Интеграционный тест: bootstrap в `/tmp/test-project`.
- Доказательство покрытия `artifacts/verification-matrix.md`.
- Аудит: `INTEGRATION_AUDIT`.

## 7. Критерии приёмки

1. `task-knowledge bootstrap --project-root /tmp/test --profile generic` выполняет полный bootstrap.
2. После bootstrap: `task-knowledge task status --project-root /tmp/test` возвращает корректный статус.
3. `--dry-run` показывает план без мутации.
4. Dirty tree с не-knowledge файлами вызывает ошибку, а не молчаливый commit.
5. Отсутствие git вызывает явную ошибку.
6. `references/adoption.md` обновлён.
7. Тесты проходят.
8. Все инварианты покрыты.

## 8. Стоп-критерии

1. Bootstrap не может надёжно отличить knowledge-файлы от чужих изменений.
2. Авто-commit создаёт риск потери данных.
3. Существующая система не может быть безопасно обновлена.

## Связь с остальными файлами задачи

- `task.md` — источник истины.
- `plan.md` — исполнимый план.
- `artifacts/verification-matrix.md` — матрица покрытия.
