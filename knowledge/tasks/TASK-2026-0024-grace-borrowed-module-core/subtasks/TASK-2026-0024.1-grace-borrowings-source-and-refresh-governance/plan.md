# План задачи TASK-2026-0024.1

## Правило

Для задачи существует только один файл плана: `plan.md`.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0024.1` |
| Parent ID | `TASK-2026-0024` |
| Версия плана | `2` |
| Связь с SDD | `не требуется` |
| Дата обновления | `2026-04-20` |

## Цель

Спроектировать устойчивый local-first механизм обновления borrowed-layer из GRACE,
который задаёт источник,
scope заимствований
и preview/apply governance
для всех следующих capability-поставок `Module Core`.
В том же foundation-слое нужно описать borrowed execution vocabulary,
который позволит главным агентам выдавать single-writer `ExecutionPacket`
без превращения продукта в full GRACE orchestration framework.
Механизм должен описывать borrowings language-agnostic образом,
включая сценарии для `1С/BSL`.

## Границы

### Входит

- путь и формат source manifest;
- статус borrowed-layer и отпечаток refresh-плана;
- карта `upstream source -> local targets`;
- пространство имён CLI `borrowings`;
- правила локального override checkout path;
- соответствие `GRACE operational packets -> repo-native ExecutionPacket / ResultPacket / FailureHandoff / ExecutionReadiness`;
- правила controller-only `refresh-apply` для borrowed assets;
- правила language-neutral описания borrowed surface.

### Не входит

- реализация `knowledge/modules/`;
- module query и module verification catalog;
- network fetch как обязательный сценарий.

## Планируемые изменения

### Код

- `task-knowledge borrowings status|refresh-plan|refresh-apply`;
- runtime helper `borrowings_runtime` для manifest parser, checkout status, fingerprinted preview и guarded apply.

### Конфигурация / схема данных / именуемые сущности

- `skills-global/task-centric-knowledge/borrowings/grace/source.json`
- `skills-global/task-centric-knowledge/borrowings/grace/README.md`
- packet vocabulary в документации borrowed-layer без обязательного XML-runtime;
- разрешённые refresh-действия: `create`, `update`, `noop`.

### Документация

- task-local docs подзадачи;
- README для borrowed-layer.

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- borrowed helper живёт отдельно от `Task Core` read-model;
- refresh не должен менять task-routing и task-query.

### Границы, которые должны остаться изолированными

- source manifest описывает borrowings, а не product state задачи;
- local checkout override не превращается в обязательную настройку для всех пользователей;
- refresh apply работает только по preview-утверждённому scope.
- source manifest не должен требовать язык-специфичного parser-а для определения применимости borrowings.
- borrowed packet vocabulary не даёт writer-subagent прав на task-truth и shared governance docs.

### Критический функционал

- reusable source-of-truth для borrowings;
- безопасный refresh-governance;
- repo-native packet vocabulary для controlled execution;
- независимость от устаревающих локальных путей;
- language-agnostic borrowed mapping, пригодный для `1С/BSL`.

### Основной сценарий

- оператор смотрит `borrowings status`;
- получает `refresh-plan` для pinned upstream revision;
- применяет `refresh-apply` только к preview-подтверждённому scope.

### Исходный наблюдаемый симптом

- старый absolute path на upstream checkout уже невалиден, а borrowed mechanism отсутствует.

## Риски и зависимости

- если manifest окажется слишком абстрактным, capability-подзадачи не смогут на него опираться;
- если refresh не будет fingerprinted, потом появится drift между plan и apply;
- если manifest будет выражать borrowings через language-specific assumptions, он не станет универсальным foundation для `Module Core`.

## Связь с SDD

- `не требуется`

## Проверки

### Что можно проверить кодом или тестами

- unit-тесты parser-а manifest и отпечатка refresh-плана;
- проверки CLI `borrowings status|refresh-plan|refresh-apply`;
- `git diff --check`

### Что остаётся на ручную проверку

- `не требуется`

## Шаги

- [x] Описать структуру source manifest и borrowed mapping.
- [x] Определить `borrowings status` и `refresh-plan`.
- [x] Определить `refresh-apply` и scope protection.
- [x] Зафиксировать local override и fallback без сети.
- [x] Описать соответствие borrowed GRACE packet ideas и repo-native execution vocabulary.
- [x] Зафиксировать language-agnostic borrowed mapping, совместимый с `1С/BSL`.
- [x] Закрыть подзадачу после финального ревью результатов и проверок.

## Реализованный CLI contract

- `task-knowledge --json borrowings status --project-root /abs/project --source grace [--checkout /abs/path]`
- `task-knowledge --json borrowings refresh-plan --project-root /abs/project --source grace [--checkout /abs/path]`
- `task-knowledge --json borrowings refresh-apply --project-root /abs/project --source grace --plan-fingerprint <sha256> --yes [--checkout /abs/path]`

`status` работает без checkout и возвращает warning.
`refresh-plan` требует локальный git checkout на `pinned_revision`.
`refresh-apply` заново строит plan и блокируется при fingerprint drift.

## Критерии завершения

- manifest schema и refresh-governance описаны без двусмысленностей;
- packet vocabulary можно использовать в `TASK-2026-0024.5` и `TASK-2026-0024.6` без новых продуктовых решений;
- следующий implementer может добавить runtime и CLI без дополнительных продуктовых решений.
