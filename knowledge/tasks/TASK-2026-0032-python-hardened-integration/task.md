# Карточка задачи TASK-2026-0032

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0032` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0032` |
| Технический ключ для новых именуемых сущностей | `python-hardened-integration` |
| Краткое имя | `python-hardened-integration` |
| Человекочитаемое описание | `Интегрировать доработки из task-centric-knowledge-python-hardened.zip в основной репозиторий, прогнать review-fix цикл до clean verdict и закрыть результат в main.` |
| Справочный режим | `нет` |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `main` |
| Требуется SDD | `да` |
| Статус SDD | `в работе` |
| Ссылка на SDD | `knowledge/tasks/TASK-2026-0032-python-hardened-integration/sdd.md` |
| Дата создания | `2026-04-23` |
| Дата обновления | `2026-04-23` |

## Цель

Взять внешний hardened snapshot проекта из архива, безопасно интегрировать только полезные доработки в основной репозиторий, повторять expert review-fix цикл до отсутствия реальных дефектов и завершить работу закрытой задачей в `main`.

## Наблюдаемые симптомы

- Пользователь передал внешний архив `/home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge-python-hardened.zip` и потребовал не останавливаться на первом fix-pass.
- Архив содержит отдельный git snapshot с собственным `.git/` и веткой `task/task-2026-0031-python-hardening`, поэтому интеграцию нельзя делать вслепую поверх текущего `main`.
- Для такого потока нужен отдельный task-контур: на `main` текущая задача неоднозначна, а доработки требуют собственного verify и merge lifecycle.

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

- `python3 -m unittest discover -s tests -v` — пройдено, `227 tests`, `OK`.
- `python3 -m compileall -q scripts tests` — пройдено.
- `python3 -m unittest tests.test_cli_golden_contracts -v` — пройдено.
- `python3 -m unittest tests.test_python_hardening_contracts -v` — пройдено.
- `python3 -m unittest tests.test_module_query_runtime -v` — пройдено.
- `python3 -m unittest tests.test_file_local_contracts_runtime -v` — пройдено.
- `python3 -m unittest tests.test_git_ops_runtime -v` — пройдено.
- `python3 -m unittest tests.test_install_skill_governance -v` — пройдено.
- `python3 -m unittest tests.test_task_workflow -v` — пройдено.
- `PYTHONPATH=scripts python3 -m task_knowledge --help` — пройдено.
- `make install-local PYTHON="<tmpvenv>/bin/python" USER_BIN="<tmpvenv>/bin"` + `task-knowledge --help` + `python -m task_knowledge --help` — пройдено в clean venv через fallback wrapper + `.pth`.
- `git diff --check` — пройдено.
- `bash scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0032-python-hardened-integration knowledge/tasks/registry.md` — пройдено.
- `python3 scripts/task_knowledge_cli.py task status --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge` — пройдено, `TASK-2026-0032` резолвится как текущая задача.

### Остаётся на ручную проверку

- `не требуется`
