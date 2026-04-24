# Матрица проверки по задаче TASK-2026-0035

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0035` |
| Связанный SDD | `../sdd.md` |
| Версия | `1` |
| Дата обновления | `2026-04-24` |

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
| `INV-01` | Current subset остаётся только query/workflow и не закрывает consumer gap | `python3 -m unittest discover -s tests` | `planned` | Точный test surface уточнится после materialization contract |
| `INV-02` | Новый surface нельзя обновлять как versioned embedded subset | `task-knowledge --json doctor --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/task-centric-knowledge` | `planned` | Update/sync contract должен быть проверяемым |
| `INV-03` | Решение выходит за рамки standalone task OS | task-local docs review, `git diff --check` | `planned` | Архитектурный guard |
| `INV-04` | Paired consumer-case не может использовать новый contract для отказа от `.sisyphus` | `task-knowledge --json install check --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/oh-my-openagent-fork` | `planned` | Полный consumer effect будет доказан в paired downstream task |

## 3. Остаточный риск и ручной остаток

- До реализации остаётся риск, что consumer runtime gap окажется шире допустимого standalone scope.
- Live downstream smoke остаётся в paired consumer task и не дублируется здесь.

## 4. Правило завершения

- Задача не должна уходить в ревью, пока обязательные инварианты не связаны с фактически прогнанными проверками.
- Review не заменяет verification matrix.
