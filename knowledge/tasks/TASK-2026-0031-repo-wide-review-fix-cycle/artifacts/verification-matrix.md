# Матрица верификации TASK-2026-0031

| Инвариант | Сценарий нарушения | Проверка/команда | Статус покрытия |
|-----------|--------------------|------------------|-----------------|
| `INV-01` | Repo-wide review находит medium/high defect, но задача закрывается без исправления или without evidence. | Review-pass от Dalton и Confucius; повторные clean verdict после финального fix-pass. | covered |
| `INV-02` | После fix-pass install/workflow/query/module/borrowings/release layer выдаёт misleading diagnostic или behavioural regression. | `python3 -m unittest discover -s tests -v`; targeted regressions в `test_module_query_runtime.py`, `test_install_skill_governance.py`, `test_release_contract.py`, `test_task_query.py`. | covered |
| `INV-03` | Исправления ломают общий regression-контур, импорт или синтаксис. | `python3 -m compileall -q scripts tests`; `python3 -m unittest discover -s tests -v`; `python3 -m unittest discover -s tests -p 'test_task_query_architecture.py' -v`. | covered |
| `INV-04` | Standalone test/CLI surface зависит от побочного контекста и не запускается изолированно. | `/usr/bin/bash -lc 'for path in tests/test_*.py; do ...; done'`; standalone `test_task_workflow_markdown.py`; standalone `test_task_workflow_publish.py`. | covered |
| `INV-05` | `task.md` / `plan.md` / `sdd.md` / `verification-matrix.md` расходятся с фактическим verify и финальным branch-state. | `python3 scripts/task_query.py --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/task-centric-knowledge task show TASK-2026-0004 --format json`; `python3 scripts/task_query.py --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/task-centric-knowledge task show TASK-2026-0006 --format json`; final sync task-local docs. | covered |
