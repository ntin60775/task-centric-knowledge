# План задачи TASK-2026-0024.5

## Правило

Для задачи существует только один файл плана: `plan.md`.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0024.5` |
| Parent ID | `TASK-2026-0024` |
| Версия плана | `2` |
| Связь с SDD | `не требуется` |
| Дата обновления | `2026-04-20` |

## Цель

Реализовать каталог модульной верификации,
который позволит переиспользовать доказательные проверки между задачами
и одновременно сохранить task-local ownership по invariant coverage.
Каталог также должен стать источником `ExecutionReadiness`,
`VerificationExcerpt` и `FailureHandoff` для controlled single-writer execution.
Каталог должен быть пригоден для разных способов проверки,
включая сценарии `1С/BSL`.

## Границы

### Входит

- формат module verification record;
- verification excerpts для query;
- readiness gate перед writer-pass;
- failure handoff при расхождении evidence и contract;
- reuse policy в task-local matrix;
- language-neutral taxonomy проверок и evidence;
- правила manual residual на уровне модуля и задачи.

### Не входит

- замена task-local verification matrix;
- полный `verification-plan.xml`;
- обязательный rollout на все модули сразу.

## Планируемые изменения

### Код

- отдельный runtime `Module Core` для parser/readiness/excerpt/handoff;
- helper-слой без привязки к конкретному CLI namespace;
- unit-тесты на parser, `ExecutionReadiness`, `VerificationExcerpt` и `FailureHandoff`.

### Конфигурация / схема данных / именуемые сущности

- отдельный verification-артефакт `knowledge/modules/<MODULE-ID>-<slug>/verification.md`;
- additive managed assets для модульного companion-layer;
- фиксированная taxonomy гейтов, типов проверок и видов evidence без language-specific special-case режима.

### Документация

- task-local фиксация storage choice и reuse policy;
- managed README по `knowledge/modules/`;
- template `verification.md` с каноническими секциями и таблицами.

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- verification catalog хранится отдельным артефактом и зависит от `verification_ref` в module passport, но не владеет task state;
- verification model не может предполагать один язык, один тестовый раннер или один формат команды.
- readiness gate не может автоматически закрывать задачу или выдавать writer-у task-truth ownership.

### Границы, которые должны остаться изолированными

- task-local matrix остаётся владельцем task-specific invariants;
- module verification содержит reusable проверки, но не закрывает задачи автоматически;
- `module.md` хранит только `verification_ref` и краткую readiness summary, а не весь verification payload;
- CLI `module show --with verification` остаётся scope `24.6`, а не этой подзадачи.

### Критический функционал

- повторное использование канонических module checks;
- безопасный gate перед single-writer execution;
- failure handoff с contract/evidence/anchor;
- уменьшение дублирования verification между задачами;
- единый verification contract для Python/TS и `1С/BSL`;
- additive install rollout без поломки совместимости предыдущей knowledge-системы.

### Основной сценарий

- инженер или агент читает `verification.md` governed module;
- runtime вычисляет `ExecutionReadiness` и `VerificationExcerpt`;
- task-local matrix ссылается на `verification_ref#SCN-*` / `#CHK-*`,
  но сохраняет ownership по своим инвариантам и фактическому `covered`.

### Исходный наблюдаемый симптом

- verification сегодня сильна на уровне задачи, но мало переиспользуется между задачами.

## Риски и зависимости

- слишком агрессивный reuse может размыть task-local ownership;
- слишком слабый reuse не даст пользы;
- если verification taxonomy окажется language-specific, модульная верификация не станет универсальной;
- если storage снова смешается с passport, `24.2` и `24.6` получат тяжёлую и конфликтную shared/public схему.

## Связь с SDD

- `не требуется`

## Проверки

### Что можно проверить кодом или тестами

- unit-тесты verification runtime
- unit-тесты install/compatibility контура
- `git diff --check`
- команда локализационной проверки документации

### Что остаётся на ручную проверку

- `не требуется`

## Шаги

- [x] Определить формат module verification record.
- [x] Зафиксировать отдельный storage `verification.md` и `verification_ref` вместо вложенной секции в passport.
- [x] Определить excerpts для query layer.
- [x] Определить `ExecutionReadiness` и gate statuses `ready|blocked|partial`.
- [x] Определить `FailureHandoff` для передачи verifier -> controller -> writer.
- [x] Описать reuse policy в task-local matrix.
- [x] Развести ownership module-level и task-level verification.
- [x] Добавить runtime и unit-тесты для parser/readiness/excerpt/handoff.
- [x] Добавить additive managed assets для `knowledge/modules`.

## Критерии завершения

- verification catalog описан и реализован достаточно конкретно для последующей реализации `24.6`;
- separate-artifact storage choice больше не требует нового продуктового решения;
- installer и unit-тесты доказывают additive rollout без регрессии совместимости.
