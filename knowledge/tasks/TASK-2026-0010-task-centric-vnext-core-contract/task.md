# Карточка задачи TASK-2026-0010

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0010` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0010` |
| Технический ключ для новых именуемых сущностей | `vnext-core-contract` |
| Краткое имя | `task-centric-vnext-core-contract` |
| Человекочитаемое описание | `Нормативный vNext-core contract и DDD-карта для task-centric-knowledge` |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `task/task-2026-0010-task-centric-vnext-core-contract` |
| Требуется SDD | `да` |
| Статус SDD | `завершено` |
| Ссылка на SDD | `sdd.md` |
| Дата создания | `2026-04-12` |
| Дата обновления | `2026-04-13` |

## Цель

Превратить стратегическое описание из `TASK-2026-0008` в один короткий нормативный `vNext-core contract`,
который однозначно фиксирует полный агрегат `Task Core`, источник истины, переходы состояний,
ownership по файлам и правило локального хранения доказательных артефактов задачи.

## Границы

### Входит

- формализация полного агрегата `Task Core`: `Task`, `Subtask`, `Delivery Unit`, `Verification Matrix`, `Task Artifact`, `Decision`, `Worklog Entry`, `Handoff`;
- фиксация DDD-карты контекстов `Task Core`, `Read Model / Reporting`, `Publish Integration`, `Memory`, `Packaging / Governance`, `Profiles`;
- явное правило `task.md` как источника истины и `registry.md` как навигационного cache;
- фиксация канонической summary-тройки `TASK-ID + Краткое имя + Человекочитаемое описание`;
- фиксация статусной модели задач и delivery units;
- фиксация evidence governance и cleanup-governance как части ядра;
- синхронизация skill-level snapshot и managed-шаблонов с утверждённым core contract.

### Не входит

- модульная декомпозиция `task_workflow.py`;
- реализация операторских read-команд `status / current-task / task show`;
- host-specific publish adapters и memory implementation details;
- полевой rollout на внешние репозитории.

## Контекст

- источник постановки: Track 1 из `TASK-2026-0008`;
- базовый стратегический источник: `../TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/strategy-roadmap.md`;
- связанный SDD-источник: `../TASK-2026-0008-task-centric-knowledge-roadmap-vnext/sdd.md`;
- канонический результат этой задачи: `artifacts/vnext-core-contract.md`;
- downstream-потребители: `TASK-2026-0011`, `TASK-2026-0012`, `TASK-2026-0013`, `TASK-2026-0014`.

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Доменная модель | Нормализуются канонические сущности, объекты-значения и переходы состояний `Task Core` |
| Документация | Создаётся первичный `vNext-core contract`, обновляются `task.md`, `plan.md`, `sdd.md`, verification matrix и skill-level snapshot |
| Managed knowledge-система | Обновляются `README.md` и шаблоны `knowledge/tasks/` в assets и затем refresh-ятся в текущем репозитории |
| Тестовый контракт | Проверки installer/templates фиксируют новые core-инварианты |
| Runtime helper | `нет`, кроме проверки, что новый contract не требует немедленной runtime-декомпозиции |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/`
- канонический core contract: `artifacts/vnext-core-contract.md`
- файл плана: `plan.md`
- файл SDD: `sdd.md`
- матрица проверки: `artifacts/verification-matrix.md`
- стратегический источник: `knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/strategy-roadmap.md`
- дистрибутивный snapshot: `skills-global/task-centric-knowledge/references/roadmap.md`

## Контур публикации

Delivery unit для нормативной задачи не потребовался.

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | — | `—` | `—` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |

## Текущий этап

Задача завершена как contract-first delivery:
создан `artifacts/vnext-core-contract.md`, синхронизированы task-local артефакты,
обновлены `SKILL.md`, `references/roadmap.md`, managed `README.md` и шаблоны `knowledge/tasks/`,
после чего выполнены unit-проверки, installer refresh/check, `git diff --check` и локализационный guard.

## Стратегия проверки

### Покрывается кодом или тестами

- `rg -n "Task Core|Read Model / Reporting|Publish Integration|Memory|Packaging / Governance|Profiles" knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md skills-global/task-centric-knowledge/references/roadmap.md`
- `rg -n "Task Artifact|Decision|Worklog Entry|Handoff|Verification Matrix|Delivery Unit" knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md`
- `rg -n "task.md|registry.md|TASK-ID|Краткое имя|Человекочитаемое описание|plan -> confirm|project data|artifacts/" knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md skills-global/task-centric-knowledge/SKILL.md skills-global/task-centric-knowledge/assets/knowledge/tasks/README.md`
- `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main --mode install --force`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main --mode check`
- `git diff --check`
- `scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/task.md knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/plan.md knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/sdd.md knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/verification-matrix.md skills-global/task-centric-knowledge/SKILL.md skills-global/task-centric-knowledge/references/roadmap.md skills-global/task-centric-knowledge/assets/knowledge/tasks/README.md skills-global/task-centric-knowledge/assets/knowledge/tasks/_templates/task.md skills-global/task-centric-knowledge/assets/knowledge/tasks/_templates/plan.md skills-global/task-centric-knowledge/assets/knowledge/tasks/_templates/sdd.md skills-global/task-centric-knowledge/assets/knowledge/tasks/_templates/artifacts/verification-matrix.md knowledge/tasks/README.md knowledge/tasks/_templates/task.md knowledge/tasks/_templates/plan.md knowledge/tasks/_templates/sdd.md knowledge/tasks/_templates/artifacts/verification-matrix.md`

### Остаётся на ручную проверку

- `не требуется`

## Критерии готовности

- существует один короткий канонический документ `artifacts/vnext-core-contract.md`;
- DDD-карта и ownership boundaries не противоречат `TASK-2026-0008`;
- полный агрегат `Task Core` зафиксирован без двусмысленности;
- источники истины, task summary, статусная модель и evidence governance закреплены воспроизводимо;
- skill-level snapshot и managed-шаблоны дают тот же ответ по core-инвариантам, что и task-local contract;
- verification matrix переведена в `covered` по всем обязательным инвариантам.

## Итоговый список ручных проверок

- `не требуется`

## Итог

В рамках `TASK-2026-0010` создан первичный нормативный документ `artifacts/vnext-core-contract.md`,
который фиксирует полный агрегат `Task Core`, DDD-карту контекстов, source of truth, ownership по файлам,
каноническую task summary, статусную модель задач и delivery units, а также evidence / cleanup governance.

Дополнительно синхронизированы производные носители:
`SKILL.md`, `references/roadmap.md`, managed `README.md` и шаблоны `knowledge/tasks/`.
После refresh managed-файлов в текущем репозитории и прохождения проверок эта задача переведена в `завершена`.
