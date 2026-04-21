# SDD по задаче TASK-2026-0011

## Паспорт SDD

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0011` |
| Статус | `завершено` |
| Версия | `3` |
| Дата обновления | `2026-04-13` |

## 1. Проблема и цель

### Проблема

`task_workflow.py` концентрирует в себе доменную модель, markdown-форматирование, git-операции, publish-flow и CLI orchestration.
Это затрудняет изменение правил, локализацию регрессий и перенос тестов на уровень домена.

### Цель

Разрезать helper на модули ответственности так, чтобы:

- доменные правила были отделены от I/O;
- git/publish-операции были изолированы от markdown-логики;
- CLI entrypoint стал тонкой композицией;
- regression behavior для текущих команд сохранился;
- file-based import `scripts/task_workflow.py` остался совместимым для тестов и внешних импортёров.

## 2. Целевой runtime-разрез

Новый runtime живёт в пакете `scripts/task_workflow_runtime/`.
Точный состав модулей:

- `models.py`
  - `StepResult`, `DeliveryUnit`, `DeliveryUnitVersion`, `PublicationSnapshot`;
  - общие константы, normalizers, `default_branch_name`, `default_delivery_branch_name`, `extract_delivery_branch_index`.
- `git_ops.py`
  - `run_git`, `run_command`, `current_git_branch`, `worktree_is_clean`, `dirty_paths`, `branch_exists`, `has_remote`, `remote_url`, определение forge-host, выбор базовой ветки и создание или переиспользование delivery-ветки.
- `task_markdown.py`
  - разбор, рендеринг и обновление publish-таблицы delivery units;
  - чтение и обновление полей `task.md`;
  - извлечение сводки из `Человекочитаемого описания` и `## Цель`.
- `registry_sync.py`
  - `preflight_registry_summary`, ранжирование по свежести и истории, связанные refs, слияние delivery metadata, `update_registry` и preflight контекста задачи.
- `forge.py`
  - `ForgeAdapter`, `GitHubAdapter`, `GitLabAdapter`, `resolve_forge_adapter` и разбор URL или ссылок публикации.
- `sync_flow.py`
  - orchestration только для `sync_task`.
- `publish_flow.py`
  - orchestration только для `run_publish_flow`.
- `cli.py`
  - разбор аргументов, dispatch, `print_text_report`, `main`.

## 3. Правило import graph и ownership

Разрешённый граф зависимостей:

- `models.py` не зависит от локальных runtime-модулей;
- `git_ops.py` зависит только от stdlib и `models.py`;
- `task_markdown.py` зависит только от stdlib и `models.py`;
- `registry_sync.py` зависит только от `models.py`, `git_ops.py`, `task_markdown.py`;
- `forge.py` зависит только от `models.py`, `git_ops.py`;
- `sync_flow.py` зависит только от `models.py`, `git_ops.py`, `task_markdown.py`, `registry_sync.py`;
- `publish_flow.py` зависит только от `models.py`, `git_ops.py`, `task_markdown.py`, `registry_sync.py`, `forge.py`;
- `cli.py` зависит только от `sync_flow.py` и `publish_flow.py`;
- `scripts/task_workflow.py` зависит только от `task_workflow_runtime` и не содержит бизнес-логики.

Недопустимо:

- обратный импорт из `models.py` в orchestration-слой;
- прямой вызов `subprocess` из `sync_flow.py`, `publish_flow.py` или `cli.py` вне `git_ops.py` и `forge.py`;
- возврат markdown или registry policy обратно в facade `task_workflow.py`.

## 4. Полный invariant set

- `INV-0011-01`: доменная логика не зависит от markdown-представления строк таблиц;
- `INV-0011-02`: `sync` и publish-flow сохраняют существующее поведение;
- `INV-0011-03`: branch-aware и preflight-сценарии остаются покрыты тестами;
- `INV-0011-04`: `task_workflow.py` перестаёт быть единственным носителем политики;
- `INV-0011-05`: новый import graph не создаёт циклических зависимостей между слоями;
- `INV-0011-06`: facade `scripts/task_workflow.py` сохраняет CLI flags, text/json payload и file-based import surface для `sync_task`, `run_publish_flow`, `DeliveryUnit`, `PublicationSnapshot`, `DELIVERY_ROW_PLACEHOLDER`, `update_task_file_with_delivery_units`.

## 5. Этапы реализации и проверки

### Этап 1. Freeze baseline

- зафиксировать поведенческий baseline текущего helper-а;
- перевести задачу на отдельную ветку и синхронизировать task metadata;
- зафиксировать module map и compatibility surface в task-local документах.
- Verify: `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_workflow.py`

### Этап 2. Split core

- вынести runtime в пакет `scripts/task_workflow_runtime/`;
- оставить в `scripts/task_workflow.py` только bootstrap, re-export и вызов `main()`;
- сохранить semantics `sync`, `publish`, `merge`, `close` без расширения scope.
- Verify: `python3 skills-global/task-centric-knowledge/scripts/task_workflow.py --help`

### Этап 3. Harden regression

- добавить модульные тесты по markdown, registry, publish и architecture слоям;
- оставить black-box regression через file-based import entrypoint;
- подтвердить совместимость publish/sync сценариев и отсутствие циклов.
- Verify: `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'`
- Verify: `git diff --check`
- Verify: `scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0011-task-centric-vnext-helper-modularization/task.md knowledge/tasks/TASK-2026-0011-task-centric-vnext-helper-modularization/plan.md knowledge/tasks/TASK-2026-0011-task-centric-vnext-helper-modularization/sdd.md knowledge/tasks/TASK-2026-0011-task-centric-vnext-helper-modularization/artifacts/verification-matrix.md`

### Фактически подтверждённый итог

- baseline black-box regression сохранён и расширен до полного discover-набора `62` тестов;
- facade-entrypoint оставлен тонким и совместимым с patch seam `resolve_forge_adapter`;
- runtime split закрыт без циклов по import graph и без расширения продуктового scope.

## 6. Критерии приёмки

1. Основные зоны ответственности helper-а выделены в отдельные модули.
2. `task_workflow.py` выполняет роль тонкого facade-entrypoint и не содержит доменной/publish-логики.
3. Test-suite подтверждает отсутствие регрессий и сохраняет зелёный baseline как минимум на текущих `44` black-box сценариях.
4. Новый разрез снижает change amplification и остаётся без циклов по import graph.
5. Совместимость file-based import surface не нарушена.

## 7. Стоп-критерии

1. Разрез модулей вводит циклы зависимостей.
2. Для сохранения совместимости приходится дублировать старую логику в нескольких местах.
3. Regression-набор перестаёт надёжно покрывать publish/sync.
4. Facade-entrypoint начинает втягивать обратно orchestration или markdown policy.
