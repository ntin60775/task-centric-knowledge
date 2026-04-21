# Матрица проверки по задаче TASK-2026-0021

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0021` |
| Связанный SDD | `../sdd.md` |
| Версия | `1` |
| Дата обновления | `2026-04-14` |

## 1. Канонические инварианты

| Invariant ID | Описание | Источник истины | Где может сломаться |
|--------------|----------|-----------------|---------------------|
| `INV-01` | Repo-wide knowledge metadata синхронизированы по summary/status/branch там, где drift устраним без изменения смысла задач | `task.md`, `knowledge/tasks/registry.md`, `task_query status` | legacy task-карточки, строки реестра |
| `INV-02` | `task-centric-knowledge v1` описан как конечный продукт с бинарными release-gates | `task.md`, `sdd.md`, `artifacts/v1-product-thesis.md` | release-definition снова расползается в roadmap |
| `INV-03` | Решение относительно `grace-marketplace` выражено как явная product boundary | `artifacts/v1-product-thesis.md` | сравнение остаётся расплывчатым или идеологическим |
| `INV-04` | Standalone-линия `task-centric-knowledge` не дублирует GRACE как full contract-first framework | `artifacts/v1-product-thesis.md`, `references/roadmap.md`, `grace-marketplace/README.md` | scope продукта снова разрастается |
| `INV-05` | Текущий runtime skill-а остаётся воспроизводимо здоровым после knowledge-sync | unit-tests, `install_skill.py --mode check`, `task_query status` | скрытая регрессия helper/read-model |

## 2. Матрица покрытия

| Invariant ID | Сценарий нарушения или переход | Автопроверка / команда | Статус покрытия | Примечание |
|--------------|--------------------------------|------------------------|-----------------|------------|
| `INV-01` | `status` продолжает поднимать устранимые legacy warnings после sync | `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main status --format json` | `covered` | После sync read-model возвращает `warnings: []` |
| `INV-02` | release-v1 снова описан как бесконечная стратегия без критериев | `rg -n "release-gate|рабочая система|v1" knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/task.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/sdd.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/artifacts/v1-product-thesis.md` | `covered` | Gates и product-formula зафиксированы |
| `INV-03` | нет чёткого решения `standalone / adapter / pivot` | `rg -n "standalone|adapter|pivot|GRACE" knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/artifacts/v1-product-thesis.md` | `covered` | Пользователь подтвердил `standalone` как базовую релизную траекторию; `adapter` оставлен резервным follow-up |
| `INV-04` | scope `task-centric-knowledge` дублирует GRACE | `rg -n "task-centric operating system|contract-first engineering framework|не делать" knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/artifacts/v1-product-thesis.md` | `covered` | В артефакте зафиксирована жёсткая граница продукта |
| `INV-05` | knowledge-sync ломает runtime или installer contract | `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'` | `covered` | `Ran 107 tests ... OK` |
| `INV-05` | knowledge-sync ломает install/check governance | `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main --mode check` | `covered` | `ok=True`, `existing_system_classification=compatible` |
| `INV-05` | knowledge-sync вносит форматные дефекты | `git diff --check` | `covered` | Форматных дефектов нет |

## 3. Остаточный риск и ручной остаток

- `не требуется`

## 4. Правило завершения

- Задача может считаться завершённой, потому что release-thesis теперь даёт явное решение относительно GRACE: базовая траектория `standalone`, резервная траектория `adapter`, запрет на превращение продукта в `свой GRACE`.
- Review не заменяет матрицу и не должен быть первым местом, где обнаруживается product ambiguity.
