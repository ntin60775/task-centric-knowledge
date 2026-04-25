# Матрица проверки по задаче TASK-2026-0035

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0035` |
| Связанный SDD | `../sdd.md` |
| Версия | `1` |
| Дата обновления | `2026-04-25` |

## 1. Канонические инварианты

| Invariant ID | Описание | Источник истины | Где может сломаться |
|--------------|----------|-----------------|---------------------|
| `INV-01` | Upstream даёт minimal native runtime contract сверх текущего query/workflow subset | `sdd.md`, разделы 1-4 | runtime glue, docs, tests |
| `INV-02` | Consumer contract остаётся updateable и versioned для embedded consumption | `sdd.md`, разделы 2-4 | sync metadata, deployment/update docs |
| `INV-03` | Решение не раздувает продукт за пределы standalone thesis | `sdd.md`, разделы 2, 8 | архитектурные решения, docs, scope control |
| `INV-04` | Paired downstream case может использовать upstream contract для отказа от `.sisyphus` | `sdd.md`, разделы 1, 6 | field-validation against `oh-my-openagent-fork` |

## 2. Матрица покрытия

| Invariant ID | Сценарий нарушения или переход | Автопроверка / команда | Статус покрытия | Примечание |
|--------------|--------------------------------|------------------------|-----------------|------------|
| `INV-01` | Upstream не фиксирует public consumer contract сверх query/workflow subset | `python3 -m unittest tests.test_task_knowledge_cli tests.test_consumer_runtime_contract tests.test_python_hardening_contracts -v` | `covered` | `consumer-runtime-v1`, manifest shape и stable CLI/JSON surface закреплены тестами/docs |
| `INV-02` | Новый surface нельзя обновлять как versioned embedded subset без внешнего checkout | `python3 -m unittest tests.test_consumer_runtime_contract tests.test_python_hardening_contracts -v`; `task-knowledge --json doctor --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/task-centric-knowledge` | `covered` | Update ownership остаётся у consumer script; upstream фиксирует version/manifest/root-boundary |
| `INV-03` | Решение выходит за рамки standalone task OS или добавляет чужой sync framework | `python3 -m unittest tests.test_consumer_runtime_contract -v`; `git diff --check` | `covered` | Новый `task-knowledge consumer sync-*` surface не добавлен |
| `INV-04` | Paired consumer-case не может использовать новый contract без root `.sisyphus` | `task-knowledge --json install check --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/oh-my-openagent-fork`; paired read-only audit | `covered` | Фактический checkout compatible; live smoke остаётся в downstream task |
| `INV-01` | Archive/zip срез без `.git` ломает `task status` traceback-ом вместо read-only summary | `python3 -m unittest tests.test_task_knowledge_cli -v`; `python3 scripts/task_knowledge_cli.py --json task status --project-root /tmp/tck-nogit-1777034137405595199` | `covered` | JSON возвращает `current_task.task=null`, `reason=git_unavailable`, `warning=git_context_unavailable` |
| `INV-02` | Project-local runtime mirror выдаёт отсутствующие standalone source-файлы проекта как doctor-проблемы | `python3 -m unittest tests.test_task_knowledge_cli -v` | `covered` | `doctor` и install-assets команды возвращают единый `source_root_unavailable` blocker и `source_root_valid=false`; consumer-owned `assets/` и `references/` не ломают embedded mode |

## 3. Остаточный риск и ручной остаток

- Live downstream smoke остаётся в paired consumer task и не дублируется здесь.
- Будущий общий upstream sync CLI для embedded consumers намеренно не входит в текущий contract surface.

## 4. Правило завершения

- Задача не должна уходить в ревью, пока обязательные инварианты не связаны с фактически прогнанными проверками.
- Review не заменяет verification matrix.
