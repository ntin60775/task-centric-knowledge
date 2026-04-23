# Карточка задачи TASK-2026-0033

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0033` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0033` |
| Технический ключ для новых именуемых сущностей | `repo-wide-review-rerun` |
| Краткое имя | `repo-wide-review-rerun` |
| Человекочитаемое описание | `Повторить полный repo-wide review-fix цикл по всему проекту task-centric-knowledge после интеграции python-hardened snapshot и закрыть только clean verdict.` |
| Справочный режим | `нет` |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `main` |
| Требуется SDD | `да` |
| Статус SDD | `в работе` |
| Ссылка на SDD | `knowledge/tasks/TASK-2026-0033-repo-wide-review-rerun/sdd.md` |
| Дата создания | `2026-04-23` |
| Дата обновления | `2026-04-23` |

## Цель

После интеграции `TASK-2026-0032` заново прогнать repo-wide review-fix цикл по всему репозиторию, повторять его до отсутствия реальных дефектов и закрыть задачу только после полного verify-контура и local finalize.

## Наблюдаемые симптомы

- Пользователь потребовал повторить review-fix цикл заново уже после интеграции python-hardened доработок.
- В репозитории появилась новая packaging/CLI/runtime поверхность, поэтому старый clean verdict `TASK-2026-0031` больше не покрывает весь актуальный код.
- Текущая рабочая ветка уже выделена под новый цикл, но task-контур ещё не был materialize и синхронизирован в knowledge-системе.

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

- Первый expert review-pass от `Volta` и `Pasteur` нашёл четыре реальных defect-а: managed `install-local`, workflow JSON discriminator, top-level governed files и canonical CLI `prog/help`.
- Повторный expert review-pass от `Volta` и `Pasteur` после fix-пакета вернул clean verdict без новых findings.
- `python3 -m unittest discover -s tests -v` — пройдено, `232 tests`, `OK`.
- `/usr/bin/bash -lc 'for path in tests/test_*.py; do python3 -m unittest discover -s tests -p "$(basename "$path")" -v || exit 1; done'` — пройдено, все `tests/test_*.py` запускаются изолированно.
- `python3 -m compileall -q scripts tests` — пройдено.
- `python3 -m unittest tests.test_python_hardening_contracts tests.test_task_knowledge_cli tests.test_file_local_contracts_runtime tests.test_module_query_runtime -v` — пройдено.
- `HOME="$(mktemp -d /tmp/tck-managed-home-XXXXXX)" make install-local USER_BIN="$(mktemp -d /tmp/tck-managed-bin-XXXXXX)"` — пройдено, managed-Python bootstrap уходит в wrapper path без `PEP 668` сбоя.
- `task-knowledge --help` и `PYTHONPATH=scripts python3 -m task_knowledge --help` — пройдены, оба entrypoint-а показывают `usage: task-knowledge`.
- `python3 scripts/task_knowledge_cli.py --json workflow publish start --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --task-dir /tmp/does-not-exist --purpose x` — проверено, failure payload снова содержит `command=workflow` и `action=start`.
- `python3 scripts/task_knowledge_cli.py doctor --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge` — пройдено, `Core/local blockers: 0`.
- `git diff --check` — пройдено.
- `bash scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0033-repo-wide-review-rerun knowledge/tasks/registry.md` — пройдено.

### Остаётся на ручную проверку

- `не требуется`
