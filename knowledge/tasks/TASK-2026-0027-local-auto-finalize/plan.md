# План задачи TASK-2026-0027

## Правило

Для задачи существует только один файл плана: `plan.md`.
Если задача декомпозируется, каждая подзадача получает свой собственный `plan.md` внутри своей папки.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0027` |
| Parent ID | `—` |
| Версия плана | `1` |
| Связь с SDD | `sdd.md` |
| Дата обновления | `2026-04-21` |

## Цель

Добавить local-only finalize flow, который закрывает ожидаемый локальный git-контур задачи: делает task-scoped commit, merge в base-ветку и checkout base-ветки либо возвращает подробный blocker-report без мутаций.

## Границы

### Входит

- finalize action в workflow CLI;
- runtime-предпроверки безопасного финализационного контекста;
- обновление task metadata после успешного finalize;
- тесты и документация.

### Не входит

- `push`, PR/MR, remote auth и сетевые публикации;
- очистка уже влитых веток;
- автоматический выбор между несколькими несвязанными задачами или ветками без явного task-контекста.

## Планируемые изменения

### Код

- добавить finalize runtime поверх `task_workflow_runtime`;
- расширить unified CLI и legacy workflow facade;
- внедрить structured payload для success/blocker outcome;
- при необходимости расширить git helper-функции безопасными локальными операциями commit/merge/checkout.

### Конфигурация / схема данных / именуемые сущности

- ввести новый workflow action `finalize` и его текстовый/JSON contract;
- синхронизировать `task.md`/`registry.md` на base-ветку после успешного локального finalize.

### Документация

- обновить `README.md`, `SKILL.md`, `references/task-workflow.md`;
- зафиксировать контракт и покрытие в task-local артефактах.

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- finalize CLI остаётся в `task_workflow_runtime` и может опираться только на существующие git/task helpers без протаскивания forge/publish semantics в обязательный local path.

### Границы, которые должны остаться изолированными

- local finalize не должен требовать remote, host adapter или auth;
- publish-flow и finalize-flow не должны сливаться в одну неразличимую state-machine;
- helper не должен выполнять destructive history actions.

### Критический функционал

- безопасный stop-report без мутаций при невалидном finalize-контексте;
- успешный локальный finalize с корректным переходом на base-ветку.

### Основной сценарий

- оператор запускает finalize из task-ветки завершённой задачи;
- helper валидирует контекст, коммитит изменения, вливает task-ветку в base и переключается на base;
- task metadata синхронизируется с итоговым локальным состоянием.

### Исходный наблюдаемый симптом

- helper прямо не умеет `finalize-task` и документирован как инструмент без auto-finalize локального git-контура.

## Риски и зависимости

- риск смешать finalize с publish-flow и случайно пообещать сетевые действия;
- риск некорректно выбрать commit scope или base-ветку;
- риск сломать historical/shared-branch сценарии и текущий task read-model.

## Связь с SDD

- SDD обязателен, потому что задача меняет workflow contract, вводит новый stateful runtime path и требует явного invariant set;
- этапы и audit-gates описаны в `sdd.md`;
- покрытие инвариантов должно быть доказано через `artifacts/verification-matrix.md`.

## Проверки

### Что можно проверить кодом или тестами

- `python3 -m unittest discover -s tests`
- целевые finalize unit-тесты на success и blocker paths
- `python3 scripts/task_knowledge_cli.py workflow --help`
- `python3 scripts/task_knowledge_cli.py workflow finalize --help`
- `bash scripts/check-docs-localization.sh`
- `git diff --check`

### Что остаётся на ручную проверку

- при необходимости дополнительная field validation на реальном внешнем репозитории с локальным merge в `main`

## Шаги

- [x] Зафиксировать finalize contract, инварианты и blocker matrix в task-local артефактах.
- [x] Реализовать runtime и CLI surface для local auto-finalize.
- [x] Доказать поведение тестами и обновить reference-документацию.

## Критерии завершения

- новый finalize surface реализован и покрыт тестами;
- docs и task-артефакты не расходятся с runtime;
- при успехе helper делает local finalize, при блокере возвращает явную причину и дальнейшие варианты.
