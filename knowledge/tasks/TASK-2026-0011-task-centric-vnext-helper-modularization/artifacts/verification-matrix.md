# Матрица проверки по задаче TASK-2026-0011

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0011` |
| Связанный SDD | `../sdd.md` |
| Версия | `2` |
| Дата обновления | `2026-04-13` |

## Канонические инварианты

| Invariant ID | Описание | План проверки | Статус |
|--------------|----------|---------------|--------|
| `INV-0011-01` | Domain logic отделена от markdown I/O | `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'` (`test_task_workflow_markdown.py`, `test_task_workflow_registry.py`, `test_task_workflow_architecture.py`) | `covered` |
| `INV-0011-02` | `sync` сохраняет поведение | `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_workflow.py` | `covered` |
| `INV-0011-03` | Publish-flow не теряет совместимость | `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'` (`test_task_workflow.py`, `test_task_workflow_publish.py`) | `covered` |
| `INV-0011-04` | `task_workflow.py` остаётся тонким entrypoint | `python3 skills-global/task-centric-knowledge/scripts/task_workflow.py --help`, `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'` | `covered` |
| `INV-0011-05` | Новый import graph не создаёт циклов | `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'` (`test_task_workflow_architecture.py`) | `covered` |
| `INV-0011-06` | File-based import surface остаётся совместимым | `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_workflow.py` | `covered` |

## Правило завершения

- Задача не считается завершённой, пока все инварианты не переведены в `covered` или явно не маркированы как ручной остаток.
- Review не заменяет эту матрицу.
