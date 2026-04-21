# План задачи TASK-2026-0024.2

## Правило

Для задачи существует только один файл плана: `plan.md`.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0024.2` |
| Parent ID | `TASK-2026-0024` |
| Версия плана | `1` |
| Связь с SDD | `не требуется` |
| Дата обновления | `2026-04-21` |

## Цель

Спроектировать `knowledge/modules/` как shared/public truth о governed modules,
который дополняет task-level память и позволяет модулю жить через несколько задач и поставок.
Паспорт должен стать shared/public truth для module-level execution:
публичный контракт, управляемые файлы, verification refs,
relation excerpts и краткая readiness-сводка доступны orchestration-layer,
но task-local truth остаётся в `Task Core`.
Schema модульного паспорта должна быть language-agnostic и применимой к `1С/BSL`.

## Границы

### Входит

- README, registry и template для module passports;
- обязательные поля паспорта;
- поля, нужные для сборки execution packet:
  управляемые файлы, verification ref, relation ref, file-local policy ref;
- language-neutral определение `module`, `owned surface` и `public contract`;
- пилотный управляемый срез;
- правила связи module passport с task-local артефактами.

### Не входит

- граф зависимостей;
- query-контур CLI;
- локальная разметка файлов.

## Планируемые изменения

### Код

- installer / read-model support для `knowledge/modules/`;
- parser и merge-слой для `module.md`, `verification.md` и `registry.md`;
- query fallback для `passport_governed` и `verification_evidence_only`.

### Конфигурация / схема данных / именуемые сущности

- `knowledge/modules/README.md`
- `knowledge/modules/registry.md`
- `knowledge/modules/_templates/module.md`

### Документация

- task-local артефакты подзадачи и родителя;
- обновление `SKILL.md` и `README.md`.

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- модульные паспорта не трогают routing задач и не становятся product state owner.

### Границы, которые должны остаться изолированными

- `task.md` остаётся владельцем task lifecycle;
- module passport хранит только модульную инженерную правду;
- registry модулей остаётся навигацией, а не местом произвольных заметок.
- schema не может зависеть от package manager, import graph или языка со строгой файловой модульностью.
- module passport не хранит private helper churn и не подменяет file-local contracts.

### Критический функционал

- стабильная модульная память;
- читаемая общая публичная истина;
- shared context для `ExecutionPacket`;
- воспроизводимый managed-root;
- единый формат для Python/TS/Go и `1С/BSL`.

### Основной сценарий

- инженер открывает module registry;
- находит governed module;
- читает его паспорт и понимает назначение, границы и связи без подъёма старых задач.

### Исходный наблюдаемый симптом

- модульная память сейчас привязана к конкретным task-артефактам и плохо переживает несколько независимых задач.

## Риски и зависимости

- если passport schema будет слишком тяжёлой, adoption резко подорожает;
- если schema будет слишком бедной, следующий query layer не на что опереть;
- если schema будет неявно ориентирована только на package-centric языки, `1С/BSL` выпадет из общего контракта.

## Связь с SDD

- `не требуется`

## Проверки

### Что можно проверить кодом или тестами

- тесты query runtime: `python3 -m unittest skills-global.task-centric-knowledge.tests.test_module_query_runtime`
- тесты installer: `python3 -m unittest skills-global.task-centric-knowledge.tests.test_install_skill`
- тесты unified CLI: `python3 -m unittest skills-global.task-centric-knowledge.tests.test_task_knowledge_cli`
- архитектурные тесты runtime и installer: `python3 -m unittest skills-global.task-centric-knowledge.tests.test_module_query_architecture skills-global.task-centric-knowledge.tests.test_install_skill_architecture`
- `git diff --check`

### Что остаётся на ручную проверку

- `не требуется`

## Шаги

- [x] Определить структуру `knowledge/modules/`.
- [x] Определить обязательные поля module passport.
- [x] Добавить execution-readiness summary и ссылки на verification/file-local policy.
- [x] Зафиксировать language-agnostic определение модуля, включая `1С/BSL`.
- [x] Выбрать первый governed scope для pilot-модулей.
- [x] Зафиксировать связь passport <-> task-local artifacts.

## Критерии завершения

- `knowledge/modules/` описан достаточно конкретно для последующей реализации;
- pilot scope и schema реализованы без новых продуктовых решений.
