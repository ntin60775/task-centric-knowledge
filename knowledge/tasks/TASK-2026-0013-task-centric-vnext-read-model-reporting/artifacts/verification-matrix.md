# Матрица проверки по задаче TASK-2026-0013

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0013` |
| Связанный SDD | `../sdd.md` |
| Версия | `5` |
| Дата обновления | `2026-04-13` |

## Канонические инварианты

| Invariant ID | Описание | Проверка | Статус |
|--------------|----------|----------|--------|
| `INV-0013-01` | Task-oriented output всегда содержит каноническую summary-связку | `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_query.py` | `covered` |
| `INV-0013-02` | Read-model не становится источником истины | `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_query_architecture.py`, `git diff --check` | `covered` |
| `INV-0013-03` | `current-task` корректно различает `resolved|ambiguous|unresolved` и в resolved-сценарии показывает этап, следующий шаг и блокеры | `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_query.py` | `covered` |
| `INV-0013-04` | `status` показывает ambiguity, drift и health warnings | `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_query.py`, `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules status --format json` | `covered` |
| `INV-0013-05` | `task show` раскрывает карточку задачи без новой доменной логики | `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_query.py`, `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules task show TASK-2026-0013` | `covered` |
| `INV-0013-06` | malformed delivery rows и missing selector не роняют CLI и поднимаются как warning/error payload | `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_query.py` | `covered` |
| `INV-0013-07` | legacy fallback и `next_step_missing` дают наблюдаемые warnings с regression coverage | `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_query.py` | `covered` |
| `INV-0013-08` | publish-контур поднимает warnings для `planned`-unit в финальной задаче и для неканоничных `host` / `publication_type` / `cleanup` | `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_query.py` | `covered` |
| `INV-0013-09` | duplicate `TASK-ID` и publish-строки с неверным числом колонок не теряются молча и дают наблюдаемый ambiguity/warning signal | `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_query.py` | `covered` |

## Проверки уровня задачи

- `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_query.py`
- `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_query_architecture.py`
- `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules status --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules current-task --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules task show TASK-2026-0013`

## Правило завершения

- Задача не считается завершённой, пока все инварианты не переведены в `covered`.
- Review не заменяет эту матрицу.
