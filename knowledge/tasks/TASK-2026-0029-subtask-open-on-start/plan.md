# План задачи TASK-2026-0029

## Правило

Для задачи существует только один файл плана: `plan.md`.
Если задача декомпозируется, каждая подзадача получает свой собственный `plan.md` внутри своей папки.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0029` |
| Parent ID | `—` |
| Версия плана | `2` |
| Связь с SDD | `sdd.md` |
| Дата обновления | `2026-04-22` |

## Цель

Уточнить task-flow так, чтобы будущие подзадачи могли существовать как черновой порядок в родительском `plan.md` или `task.md`,
а в `registry.md` и файловой структуре появлялись только реально открытые подзадачи.

## Границы

### Входит

- открытие task-local контура `TASK-2026-0029`;
- обновление нормативных формулировок в `AGENTS.md`;
- синхронизация snapshot-правил в `knowledge/tasks/README.md`;
- уточнение вводного правила в `knowledge/tasks/registry.md`;
- уточнение подсказки статуса в `knowledge/tasks/_templates/task.md`.

### Не входит

- изменение CLI, read-model или helper-синхронизации;
- отдельный backlog-реестр draft-подзадач;
- массовая миграция существующих задач.

## Планируемые изменения

### Код

- `нет`

### Конфигурация / схема данных / именуемые сущности

- policy `Subtask` получает явное правило delayed materialization;
- `registry.md` получает явную трактовку как cache только для открытых задач и подзадач.

### Документация

- `AGENTS.md`
- `knowledge/tasks/README.md`
- `knowledge/tasks/registry.md`
- `knowledge/tasks/_templates/task.md`
- task-local артефакты `knowledge/tasks/TASK-2026-0029-subtask-open-on-start/`

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- `нет`

### Границы, которые должны остаться изолированными

- runtime helper-ы и тестовая логика не меняются;
- delivery-unit contract и publish-flow не меняются;
- historical task data не переписываются задним числом.

### Критический функционал

- нормативные документы не противоречат друг другу по моменту materialization подзадачи;
- `registry.md` не описывается как место резервирования draft-ID;
- шаблон `task.md` не оставляет двусмысленность вокруг статуса `черновик`.

### Основной сценарий

- пользователь планирует будущие подзадачи в родительской задаче и может перечислить их порядок или предварительные ID в `plan.md`/`task.md`;
- пока отдельный подконтур не открыт, не создаются `subtasks/...` и строка в `registry.md`;
- в момент фактического открытия подзадачи materialize её каталог, `task.md`, `plan.md` и registry-строка;
- статус `черновик` используется уже после открытия подзадачи как сущности.

### Исходный наблюдаемый симптом

- `не требуется`

## Риски и зависимости

- если оставить термин `создавать подзадачу` без разграничения момента открытия, двусмысленность сохранится;
- если уточнение появится только в одном документе, skill-level snapshot останется рассинхронизированным;
- если формулировка будет слишком узкой и привяжет открытие только к началу кодинга, она сломает исследовательские и handoff-подзадачи.

## Связь с SDD

- каноническая спецификация этапов, инвариантов и критериев находится в `sdd.md`;
- покрытие инвариантов фиксируется в `artifacts/verification-matrix.md`;
- первичный нормативный snapshot практических правил синхронизируется через `knowledge/tasks/README.md`, а производные документы: `AGENTS.md`, `knowledge/tasks/registry.md`, `knowledge/tasks/_templates/task.md`.

## Проверки

### Что можно проверить кодом или тестами

- `python3 -m unittest discover -s tests`
- `task-knowledge task status --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge`
- `git diff --check`
- `bash scripts/check-docs-localization.sh AGENTS.md knowledge/tasks/README.md knowledge/tasks/registry.md knowledge/tasks/_templates/task.md knowledge/tasks/TASK-2026-0029-subtask-open-on-start/task.md knowledge/tasks/TASK-2026-0029-subtask-open-on-start/plan.md knowledge/tasks/TASK-2026-0029-subtask-open-on-start/sdd.md knowledge/tasks/TASK-2026-0029-subtask-open-on-start/artifacts/verification-matrix.md`

### Что остаётся на ручную проверку

- `не требуется`

## Шаги

- [x] Открыть `TASK-2026-0029`, завести task-local артефакты и зарегистрировать задачу.
- [x] Синхронизировать формулировки в `AGENTS.md`, `knowledge/tasks/README.md`, `knowledge/tasks/registry.md` и `knowledge/tasks/_templates/task.md`.
- [x] Прогнать проверки, закрыть verification matrix и обновить task-local статусы под итоговое состояние.

## Критерии завершения

- policy открытия подзадачи зафиксирована без двусмысленности;
- managed snapshot и agent rules дают одинаковый ответ о моменте materialization подзадачи;
- release/template contract и локализационный guard проходят успешно.
