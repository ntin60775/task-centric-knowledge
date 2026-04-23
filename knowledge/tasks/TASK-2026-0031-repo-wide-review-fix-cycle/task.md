# Карточка задачи TASK-2026-0031

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0031` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0031` |
| Технический ключ для новых именуемых сущностей | `repo-wide-review-fix-cycle` |
| Краткое имя | `repo-wide-review-fix-cycle` |
| Человекочитаемое описание | `Прогнать repo-wide цикл экспертного ревью и исправления дефектов по всему проекту task-centric-knowledge до clean verdict.` |
| Справочный режим | `нет` |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `main` |
| Требуется SDD | `да` |
| Статус SDD | `завершено` |
| Ссылка на SDD | `knowledge/tasks/TASK-2026-0031-repo-wide-review-fix-cycle/sdd.md` |
| Дата создания | `2026-04-23` |
| Дата обновления | `2026-04-23` |

## Цель

Провести полный review-fix цикл по всему репозиторию, устранять реальные дефекты итеративно и завершить задачу только после clean verdict от экспертных review-pass и полного локального verify-контура.

## Наблюдаемые симптомы

- Пользователь запросил repo-wide expert review-fix pass по всему проекту после закрытия `TASK-2026-0030`.
- На `main` активная задача неоднозначна, поэтому для нового цикла требуется отдельный task-контур и собственная task-ветка.
- Предыдущая review-hardening задача уже закрыла известные timeout/runtime holes, но для всего проекта ещё не выполнялся новый независимый полный review-pass по всем подсистемам.

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

- `python3 -m unittest discover -s tests -v` — пройдено, `221 tests`, `OK`.
- `/usr/bin/bash -lc 'for path in tests/test_*.py; do ...; done'` — пройдено, все `tests/test_*.py` запускаются изолированно.
- `python3 -m compileall -q scripts tests` — пройдено.
- `python3 scripts/task_query.py --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/task-centric-knowledge task show TASK-2026-0004 --format json` — пройдено, warnings очищены после `note-only` backfill.
- `python3 scripts/task_query.py --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/task-centric-knowledge task show TASK-2026-0006 --format json` — пройдено, warnings очищены после `note-only` backfill.
- `python3 scripts/task_query.py --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/task-centric-knowledge task show TASK-9999-404 --format json` — пройдено, возвращается точный `task_not_found`.
- `git diff --check` — пройдено.
- `bash scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0031-repo-wide-review-fix-cycle/task.md knowledge/tasks/TASK-2026-0031-repo-wide-review-fix-cycle/plan.md knowledge/tasks/TASK-2026-0031-repo-wide-review-fix-cycle/sdd.md knowledge/tasks/TASK-2026-0031-repo-wide-review-fix-cycle/artifacts/verification-matrix.md knowledge/tasks/registry.md knowledge/operations/task-centric-knowledge-upgrade.md knowledge/tasks/TASK-2026-0004-task-centric-knowledge-git-flow/artifacts/migration/task-centric-knowledge-upgrade.md knowledge/tasks/TASK-2026-0006-task-centric-testing-contract/artifacts/migration/task-centric-knowledge-upgrade.md` — пройдено.

### Остаётся на ручную проверку

- `не требуется`
