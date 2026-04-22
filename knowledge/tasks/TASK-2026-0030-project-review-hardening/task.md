# Карточка задачи TASK-2026-0030

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0030` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0030` |
| Технический ключ для новых именуемых сущностей | `project-review-hardening` |
| Краткое имя | `project-review-hardening` |
| Человекочитаемое описание | `Ревью проекта, устранение найденных недостатков и стабилизация локального тестового контура task-centric-knowledge.` |
| Справочный режим | `нет` |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `task/task-2026-0030-project-review-hardening` |
| Требуется SDD | `да` |
| Статус SDD | `подготовлен` |
| Ссылка на SDD | `knowledge/tasks/TASK-2026-0030-project-review-hardening/sdd.md` |
| Дата создания | `2026-04-22` |
| Дата обновления | `2026-04-22` |

## Цель

Провести ревью проекта, исправить обнаруженные дефекты и добавить проверки, которые фиксируют устранённые регрессии.

## Наблюдаемые симптомы

- Временные git-репозитории в тестах зависели от глобальной настройки `init.defaultBranch`; при `master` ломались сценарии `current-task`, рассчитанные на `main`.
- Часть subprocess/git-вызовов в тестах и runtime-helper-ах не имела timeout-защиты, поэтому зависший дочерний процесс мог блокировать regression-run.

## Контур публикации

Delivery unit описывает конкретную поставку через ветку и публикацию.
В одном `task.md` допускается `0..N` delivery units.

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | — | `—` | `—` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |

## Текущий этап

Изменения внесены, regression-контур пройден.

## Стратегия проверки

### Покрывается кодом или тестами

- `python3 -m compileall -q scripts tests` — пройдено.
- `python3 -m unittest tests.test_task_query.TaskQueryTests.test_current_task_keeps_ambiguity_for_unrelated_tasks_on_same_branch tests.test_task_query.TaskQueryTests.test_current_task_prefers_non_final_candidates_on_shared_branch tests.test_task_query.TaskQueryTests.test_task_show_supports_current_and_exact_task_id tests.test_task_query.TaskQueryTests.test_task_show_text_reports_missing_task_without_traceback -v` — пройдено, `4` теста.
- `python3 -m unittest discover -s tests -v` — пройдено, `194` теста за `30.763s`.
- `make install-local` — пройдено.
- `$HOME/.local/bin/task-knowledge --help` — пройдено.
- `$HOME/.local/bin/task-knowledge task status --project-root /mnt/data/review_work/task-centric-knowledge` — пройдено; остались существующие предупреждения upgrade-governance (`legacy_backfill_pending`, `execution_rollout_partial`).

### Проверки с ограничением среды

- `bash scripts/check-docs-localization.sh` — завершилась с `code=2` из-за отсутствующего внешнего guard-скрипта `/root/.agents/skills/owned-text-localization-guard/scripts/markdown_localization_guard.py` в текущей среде. Новые Markdown-артефакты задачи вручную оставлены на русском языке.

### Остаётся на ручную проверку

- Проверить итоговый diff перед переносом в целевой репозиторий и убедиться, что timeout-границы `120s` для runtime git/command helper-ов соответствуют локальным ожиданиям эксплуатации.
