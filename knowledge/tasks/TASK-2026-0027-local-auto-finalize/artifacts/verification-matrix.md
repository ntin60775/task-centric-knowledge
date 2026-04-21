# Матрица проверки по задаче TASK-2026-0027

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0027` |
| Связанный SDD | `../sdd.md` |
| Версия | `1` |
| Дата обновления | `2026-04-21` |

## 1. Канонические инварианты

| Invariant ID | Описание | Источник истины | Где может сломаться |
|--------------|----------|-----------------|---------------------|
| `INV-01` | При blocker condition finalize не мутирует git и возвращает явный stop-report. | `sdd.md`, finalize runtime | Неполные preflight checks, частичный commit/checkout/merge |
| `INV-02` | При success path helper делает локальный commit, merge в base и checkout base без `push`. | `sdd.md`, workflow runtime | Git helper sequencing, CLI dispatch |
| `INV-03` | После success path task metadata синхронизируется с итоговым локальным branch-state. | `task.md`, `registry.md`, finalize runtime | Metadata update после merge |
| `INV-04` | Remote/publish контур остаётся необязательным и не блокирует local finalize сам по себе. | `references/task-workflow.md`, finalize runtime | Ненужная зависимость от host adapters |
| `INV-05` | Открытые delivery units, base-branch ambiguity и чужой dirty diff дают blocker-report. | `sdd.md`, finalize runtime | Недостаточные guard conditions |

## 2. Матрица покрытия

| Invariant ID | Сценарий нарушения или переход | Автопроверка / команда | Статус покрытия | Примечание |
|--------------|--------------------------------|------------------------|-----------------|------------|
| `INV-01` | Finalize запускается в невалидном контексте и должен остановиться без мутаций. | `python3 -m unittest discover -s tests` | `covered` | Покрыто blocker-path тестами на open delivery units и branch guards |
| `INV-02` | Finalize success path выполняет commit/merge/checkout. | `python3 -m unittest discover -s tests` | `covered` | Покрыто sandbox-safe git fixture тестом success path |
| `INV-03` | После finalize task truth и registry указывают на base-ветку. | `python3 -m unittest discover -s tests` | `covered` | Проверяется assertions по `task.md` и `registry.md` после finalize |
| `INV-04` | Local finalize не требует remote/auth и не трогает publish adapters. | `python3 -m unittest discover -s tests` | `covered` | Покрыто direct runtime и unified CLI finalize tests |
| `INV-05` | Открытые delivery units и dirty чужой diff блокируют finalize. | `python3 -m unittest discover -s tests` | `covered` | Покрыто explicit blocker-code проверкой на open delivery units |

## 3. Остаточный риск и ручной остаток

- Возможна дополнительная field validation на внешнем репозитории для подтверждения live UX вне sandbox.

## 4. Правило завершения

- Задача не должна уходить в ревью, пока success и blocker paths finalize не доказаны тестами и не отражены в docs.
