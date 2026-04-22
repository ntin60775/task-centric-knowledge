# Матрица проверки по задаче TASK-2026-0029

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0029` |
| Связанный SDD | `../sdd.md` |
| Версия | `1` |
| Дата обновления | `2026-04-22` |

## 1. Канонические инварианты

| Invariant ID | Описание | Источник истины | Где может сломаться |
|--------------|----------|-----------------|---------------------|
| `INV-01` | `registry.md` и `subtasks/...` материализуют только фактически открытые подзадачи. | `AGENTS.md`, `knowledge/tasks/README.md`, `knowledge/tasks/registry.md` | нормативные формулировки task-flow и жизненного цикла |
| `INV-02` | Черновой порядок будущих подзадач и предварительные ID могут жить в `plan.md` или `task.md` родителя без отдельного каталога и registry-строки. | `AGENTS.md`, `knowledge/tasks/README.md` | правила маршрутизации и разделы про подзадачи |
| `INV-03` | Статус `черновик` применяется только к уже открытой задаче или подзадаче. | `knowledge/tasks/_templates/task.md` | шаблон task-card и подсказка по статусу |

## 2. Матрица покрытия

| Invariant ID | Сценарий нарушения или переход | Автопроверка / команда | Статус покрытия | Примечание |
|--------------|--------------------------------|------------------------|-----------------|------------|
| `INV-01` | В правилах остаётся возможность регистрировать draft-подзадачи без открытия каталога. | `task-knowledge task status --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge` | `covered` | `TASK-2026-0029` корректно открыт и read-model видит только фактический task-контур |
| `INV-02` | Документация не различает planning и opening, forcing premature materialization. | `python3 -m unittest discover -s tests` | `covered` | Полный suite прошёл: `Ran 194 tests ... OK` |
| `INV-03` | Шаблон `task.md` оставляет двусмысленность вокруг `черновик`. | `bash scripts/check-docs-localization.sh AGENTS.md knowledge/tasks/README.md knowledge/tasks/registry.md knowledge/tasks/_templates/task.md knowledge/tasks/TASK-2026-0029-subtask-open-on-start/task.md knowledge/tasks/TASK-2026-0029-subtask-open-on-start/plan.md knowledge/tasks/TASK-2026-0029-subtask-open-on-start/sdd.md knowledge/tasks/TASK-2026-0029-subtask-open-on-start/artifacts/verification-matrix.md` | `covered` | Guard должен остаться зелёным после финальной синхронизации статусов |

## 3. Остаточный риск и ручной остаток

- `нет`

## 4. Правило завершения

- Задача не считается завершённой, пока все три инварианта не переведены в `covered`.
