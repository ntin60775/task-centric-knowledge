# План задачи TASK-2026-0024.3

## Правило

Для задачи существует только один файл плана: `plan.md`.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0024.3` |
| Parent ID | `TASK-2026-0024` |
| Версия плана | `2` |
| Связь с SDD | `не требуется` |
| Дата обновления | `2026-04-21` |

## Цель

Определить минимальную dependency-модель между governed modules,
которую можно использовать в read-model,
dependency summaries для execution packet
но не превращать в тяжёлый графовый слой уровня GRACE.
Эта модель должна описывать связи без обязательного графа импортов и быть применимой к `1С/BSL`.

## Границы

### Входит

- поля связей;
- канонический владелец описания связей;
- предупреждения о дрейфе;
- выдержки по связям для query-layer и execution packet;
- язык-независимые типы связей для модулей с разной природой зависимости;
- пилотный набор управляемых модулей.

### Не входит

- полный XML-граф;
- автоматическое извлечение всего репозитория;
- сложный язык графовых запросов.

## Планируемые изменения

### Код

- парсер связей и обратная карта в `module_core_runtime/read_model.py`;
- форматтер relation-секции в `module_core_runtime/query_cli.py`;
- unit/CLI-проверки для режимов `ready`, `degraded`, `unavailable`.

### Конфигурация / схема данных / именуемые сущности

- поля связей в `module.md`;
- контракт text/JSON для `module show --with relations`;
- warning-коды `module_relation_*`.

### Документация

- управляемый шаблон `knowledge/modules/_templates/module.md`;
- README модульного слоя и task-local контракт relation-model.

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- relation-model описывает зависимости, но не пытается их полностью вычислять автоматически на первом шаге;
- relation-model допускает ручные контрактные связи там, где язык не даёт надёжного автоматического графа импортов;
- `used_by` вычисляется read-model и не хранится вручную в `module.md`.

### Границы, которые должны остаться изолированными

- истина о графе не должна уехать из human-maintained passports в generated-only output;
- query-layer не должен требовать full graph stack;
- `registry.md` не должен становиться relation-cache.
- `1С/BSL` и другие file-centric языки не должны требовать отдельной relation-модели вне общего контракта.

### Критический функционал

- полезная модульная навигация;
- умеренная стоимость сопровождения relation-model;
- единая семантика связей для Python/TS и `1С/BSL`.

### Основной сценарий

- инженер открывает module passport;
- видит, от чего модуль зависит и кто от него зависит;
- использует это в query и review.

### Исходный наблюдаемый симптом

- без relation-layer модульные паспорта останутся слишком плоскими для навигации.

## Риски и зависимости

- relation-model может стать либо слишком бедной, либо слишком тяжёлой;
- она зависит от формы module passports из `TASK-2026-0024.2`;
- если relation-schema будет опираться только на граф импортов, часть языков, включая `1С/BSL`, останется вне продукта.

## Связь с SDD

- `не требуется`

## Проверки

### Что можно проверить кодом или тестами

- юнит-проверка `python3 -m unittest skills-global.task-centric-knowledge.tests.test_module_query_runtime`
- CLI-проверка `python3 -m unittest skills-global.task-centric-knowledge.tests.test_task_knowledge_cli`
- `git diff --check`

### Что остаётся на ручную проверку

- `не требуется`

## Шаги

- [x] Зафиксировать минимальную relation-schema: только `depends_on` как исходящая связь и вычисляемый `used_by`.
- [x] Определить relation excerpts для packet/query через `module show --with relations`.
- [x] Определить canonical owner relation truth: только `module.md`, без relation-cache в `registry.md`.
- [x] Добавить warning-коды и degraded/unavailable режимы для invalid rows и missing targets.
- [x] Ограничить pilot scope governed modules парой `M-MODULE-VERIFICATION` / `M-MODULE-QUERY` и покрыть это тестами.

## Критерии завершения

- relation model реализована и покрыта unit/CLI tests;
- output contract пригоден для `ExecutionPacket` и не требует full graph stack;
- следующий шаг родительской цепочки однозначно смещён на `TASK-2026-0024.4`.
