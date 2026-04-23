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
| Ветка | `main` |
| Требуется SDD | `да` |
| Статус SDD | `подготовлен` |
| Ссылка на SDD | `knowledge/tasks/TASK-2026-0030-project-review-hardening/sdd.md` |
| Дата создания | `2026-04-22` |
| Дата обновления | `2026-04-23` |

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

Локальный finalize выполнен: task-ветка влита в base-ветку, рабочий контекст переведён на base-ветку, `push` остаётся отдельным шагом.
## Стратегия проверки

### Покрывается кодом или тестами

- `python3 -m compileall -q scripts tests` — пройдено.
- `python3 -m unittest discover -s tests -v` — пройдено, `194` теста за `27.207s`.
- `python3 scripts/task_knowledge_cli.py --help` — пройдено.
- `python3 scripts/task_query.py --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/task-centric-knowledge current-task --format json` — пройдено; `TASK-2026-0030` резолвится по ветке `task/task-2026-0030-project-review-hardening`.
- `python3 scripts/task_query.py --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/task-centric-knowledge status --format json` — пройдено; сохранились ожидаемые repo-wide warnings upgrade-governance (`legacy_backfill_pending`, `execution_rollout_partial`).
- `git diff --check` — пройдено.
- `bash scripts/check-docs-localization.sh` — пройдено; wrapper не нашёл созданных агентом документов или UI-текстов для дополнительной проверки.

### Остаётся на ручную проверку

- `не требуется` — итоговый diff и timeout-границы helper-ов проверены при локальной интеграции.
