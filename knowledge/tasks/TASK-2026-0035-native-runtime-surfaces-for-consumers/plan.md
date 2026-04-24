# План задачи TASK-2026-0035

## Правило

Для задачи существует только один файл плана: `plan.md`.
Если задача декомпозируется, каждая подзадача получает свой собственный `plan.md` внутри своей папки.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0035` |
| Parent ID | `—` |
| Версия плана | `2` |
| Связь с SDD | `sdd.md`, этапы 1-4 |
| Дата обновления | `2026-04-24` |

## Цель

Подготовить минимально достаточный native runtime contract и updateable consumer surface в `task-centric-knowledge`, чтобы downstream-потребители могли честно завершить отказ от `.sisyphus`.

## Границы

### Входит

- freeze consumer use-cases, которые не закрываются текущим query/workflow subset;
- проектирование и реализация minimal native runtime surfaces;
- versioned/updateable consumer contract и consumer-owned update rules;
- targeted integration validation на paired downstream consumer-case.

### Не входит

- реализация migration inside consumer repos;
- broad product expansion вне формулы task-centric OS;
- unrelated refactors standalone-репозитория.

## Планируемые изменения

### Код

- расширить runtime/consumer contract, если текущего subset недостаточно;
- при необходимости обновить install/query/workflow/runtime glue и tests;
- зафиксировать versioned embedded-consumer surface.

### Конфигурация / схема данных / именуемые сущности

- определить CLI/JSON runtime/interface contract для consumer repos;
- зафиксировать versioning, manifest shape и consumer-owned update-flow для embedded subset.

### Документация

- вести `task.md`, `plan.md`, `sdd.md`, `artifacts/verification-matrix.md`;
- при необходимости обновить `README.md` и `references/deployment.md`.

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- consumer-facing runtime surface может расширить текущий query/workflow subset;
- contract должен оставаться standalone и не тянуть внешний checkout как обязательную зависимость;
- paired consumer integration должна использовать versioned embedded subset, а не копирование всего репозитория.

### Границы, которые должны остаться изолированными

- нельзя превращать продукт в full orchestration framework;
- нельзя выпускать contract, который лишь переименовывает `.sisyphus` без реальной нормализации модели;
- нельзя ломать install/upgrade governance и project-data safety.

### Критический функционал

- updateable контракт потребления;
- minimal native runtime surfaces для paired consumer;
- воспроизводимая consumer-owned update story для embedded subset.

### Основной сценарий

- downstream consumer своим update script-ом обновляет versioned subset из канонического `task-centric-knowledge` и получает стабильный CLI/JSON contract без внешнего absolute checkout и без ad-hoc patching upstream.

### Исходный наблюдаемый симптом

- paired consumer-case `oh-my-openagent-fork` исторически был `mixed_system`; фактический checkout уже совместим, но upstream не имел зафиксированного `consumer-runtime-v1`, manifest shape и root-boundary для embedded consumers.
- review-замечание 3.1: `task status` в archive/zip срезе без `.git` падал traceback вместо JSON warning и registry summary.
- review-замечание 3.2: `doctor` из project-local runtime mirror смешивал project root consumer-а с source root standalone skill-а и перечислял отсутствующие source-файлы как будто они должны лежать в проекте.

## Риски и зависимости

- легко размыть scope и начать строить слишком большой framework;
- consumer runtime contract может оказаться шире, чем допустимо для standalone формулы продукта;
- без чёткой versioning/sync policy consumer subset быстро разъедется с upstream.

## Связь с SDD

- Этап 1 `sdd.md`: freeze current consumer gap и границу scope.
- Этап 2 `sdd.md`: определить native runtime contract и versioned consumer surface.
- Этап 3 `sdd.md`: реализовать tests/docs/runtime glue.
- Этап 4 `sdd.md`: подтвердить paired consumer applicability и guard against scope creep.

## Проверки

### Что можно проверить кодом или тестами

- `python3 -m unittest discover -s tests`
- `python3 -m unittest tests.test_task_knowledge_cli -v`
- `python3 -m unittest tests.test_task_knowledge_cli tests.test_consumer_runtime_contract tests.test_python_hardening_contracts -v`
- `python3 -m compileall -q scripts tests`
- `task-knowledge --json doctor --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge`
- `task-knowledge --json install check --project-root /home/prog7/РабочееПространство/projects/PetProjects/oh-my-openagent-fork`
- `git diff --check`
- `bash scripts/check-docs-localization.sh README.md references/deployment.md references/consumer-runtime-v1.md knowledge/tasks/TASK-2026-0035-native-runtime-surfaces-for-consumers/task.md knowledge/tasks/TASK-2026-0035-native-runtime-surfaces-for-consumers/plan.md knowledge/tasks/TASK-2026-0035-native-runtime-surfaces-for-consumers/sdd.md knowledge/tasks/TASK-2026-0035-native-runtime-surfaces-for-consumers/artifacts/verification-matrix.md knowledge/tasks/registry.md`

### Что остаётся на ручную проверку

- paired consumer live smoke остаётся во внешней задаче `TASK-2026-0007`.

## Шаги

- [x] Freeze paired consumer gap и минимальный contract surface
- [x] Спроектировать versioned/updateable native runtime contract для consumers
- [x] Реализовать tests/docs/runtime glue для этого contract surface
- [x] Подтвердить paired consumer applicability без scope creep
- [x] Пройти subagent review/fix loop по blocker-ам реализации
- [ ] Завершить delivery unit после локального commit и publish/merge-контуры

## Критерии завершения

- minimal native runtime contract определён и задокументирован;
- consumer subset остаётся updateable и versioned;
- paired consumer-case доказуемо может использовать contract для отказа от `.sisyphus`;
- scope `task-centric-knowledge` остаётся в формуле standalone task OS.
