# План задачи TASK-2026-0010

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0010` |
| Parent ID | `—` |
| Версия плана | `2` |
| Связь с SDD | `sdd.md`, `artifacts/verification-matrix.md`, `artifacts/vnext-core-contract.md` |
| Дата обновления | `2026-04-13` |

## Цель

Зафиксировать первичный `vNext-core contract`, который уменьшает change amplification,
даёт один нормативный источник для `Task Core`
и позволяет следующим execution-задачам опираться на него без повторного стратегического выбора.

## Границы

### Входит

- отдельный канонический файл `artifacts/vnext-core-contract.md`;
- полный агрегат `Task Core`, DDD-карта контекстов и ownership по файлам;
- каноническая summary-тройка и статусная модель;
- evidence governance и cleanup-governance как часть ядра;
- синхронизация skill-level snapshot и managed-шаблонов с утверждённым contract.

### Не входит

- file-level modularization helper-а;
- реализация `doctor deps` и `migrate cleanup plan/confirm`;
- реализация `status / current-task / task show`;
- field-validation и adoption package.

## Планируемые изменения

### Документация

- создать `artifacts/vnext-core-contract.md` как единственный нормативный source по модели ядра;
- переписать `task.md`, `plan.md`, `sdd.md` и `artifacts/verification-matrix.md` задачи вокруг нового contract;
- синхронизировать `skills-global/task-centric-knowledge/SKILL.md` и `skills-global/task-centric-knowledge/references/roadmap.md`;
- обновить managed `README.md` и шаблоны `knowledge/tasks/` так, чтобы они повторяли core-инварианты без конкурирующего источника истины.

### Runtime и тесты

- не менять `scripts/task_workflow.py` и `scripts/install_skill.py`, если новый contract не выявит прямого противоречия;
- обновить text-regression проверки installer/templates под новый core vocabulary;
- refresh-нуть managed-файлы текущего репозитория штатным installer-ом и прогнать regression-проверки.

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- `нет`, задача документирует ядро и managed-тексты, а не меняет runtime-модульность.

### Границы, которые должны остаться изолированными

- `registry.md` остаётся только навигационным cache;
- `references/roadmap.md`, `SKILL.md`, `knowledge/tasks/README.md` и шаблоны остаются производными snapshot-слоями;
- соседние tracks `TASK-2026-0011` ... `TASK-2026-0014` не переоткрываются внутри этой задачи.

### Критический функционал

- в репозитории должен появиться один и только один канонический документ ядра;
- полный агрегат `Task Core` и допустимые переходы состояний должны быть перечислены явно;
- skill-level и managed-носители должны повторять тот же ответ по source-of-truth и evidence governance.

### Основной сценарий

- открыть task-ветку и синхронизировать task-контекст;
- создать `artifacts/vnext-core-contract.md`;
- выровнять task-local пакет и дистрибутивные документы;
- refresh-нуть managed-файлы текущего репозитория;
- доказать verification matrix фактически прогнанными командами.

### Исходный наблюдаемый симптом

- `не требуется`

## Риски и зависимости

- слишком подробный contract превратится в вторую roadmap вместо короткого нормативного слоя;
- слишком короткий contract не даст достаточно жёсткого входа для `TASK-2026-0011` ... `TASK-2026-0014`;
- синхронизация только task-local артефактов без refresh managed-шаблонов оставит скрытый drift.

## Связь с SDD

- Этап 1: создать канонический `artifacts/vnext-core-contract.md` и зафиксировать полный агрегат, source-of-truth, state model и governance-инварианты.
- Этап 2: синхронизировать производные skill-level и managed-носители без расширения scope в соседние tracks.
- Этап 3: refresh-нуть managed-файлы, закрыть verification matrix и перевести задачу в финальное состояние.
- Матрица покрытия: `artifacts/verification-matrix.md`.

## Проверки

### Что можно проверить кодом или тестами

- `rg -n "Task Core|Read Model / Reporting|Publish Integration|Memory|Packaging / Governance|Profiles" knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md skills-global/task-centric-knowledge/references/roadmap.md`
- `rg -n "Task Artifact|Decision|Worklog Entry|Handoff|Verification Matrix|Delivery Unit" knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md`
- `rg -n "task.md|registry.md|TASK-ID|Краткое имя|Человекочитаемое описание|plan -> confirm|project data|artifacts/" knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md skills-global/task-centric-knowledge/SKILL.md skills-global/task-centric-knowledge/assets/knowledge/tasks/README.md`
- `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main --mode install --force`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main --mode check`
- `git diff --check`
- `scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/task.md knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/plan.md knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/sdd.md knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/verification-matrix.md skills-global/task-centric-knowledge/SKILL.md skills-global/task-centric-knowledge/references/roadmap.md skills-global/task-centric-knowledge/assets/knowledge/tasks/README.md skills-global/task-centric-knowledge/assets/knowledge/tasks/_templates/task.md skills-global/task-centric-knowledge/assets/knowledge/tasks/_templates/plan.md skills-global/task-centric-knowledge/assets/knowledge/tasks/_templates/sdd.md skills-global/task-centric-knowledge/assets/knowledge/tasks/_templates/artifacts/verification-matrix.md knowledge/tasks/README.md knowledge/tasks/_templates/task.md knowledge/tasks/_templates/plan.md knowledge/tasks/_templates/sdd.md knowledge/tasks/_templates/artifacts/verification-matrix.md`

### Что остаётся на ручную проверку

- `не требуется`

## Шаги

- [x] Синхронизировать task-ветку и registry для `TASK-2026-0010`.
- [x] Создать `artifacts/vnext-core-contract.md` и зафиксировать полный агрегат `Task Core`.
- [x] Переписать task-local пакет задачи вокруг нового contract.
- [x] Синхронизировать `SKILL.md`, `references/roadmap.md` и managed-шаблоны.
- [x] Refresh-нуть managed-файлы текущего репозитория штатным installer-ом.
- [x] Прогнать verification matrix, unit-тесты, installer check, `git diff --check` и локализационный guard.

## Критерии завершения

- `artifacts/vnext-core-contract.md` принят как первичный нормативный слой;
- verification matrix закрывает все обязательные инварианты ядра;
- skill-level snapshot и managed-шаблоны согласованы с task-local contract;
- следующие задачи могут ссылаться на этот contract без повторного стратегического выбора.
