# План задачи TASK-2026-0024.6

## Правило

Для задачи существует только один файл плана: `plan.md`.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0024.6` |
| Parent ID | `TASK-2026-0024` |
| Версия плана | `2` |
| Связь с SDD | `не требуется` |
| Дата обновления | `2026-04-20` |

## Цель

Реализовать минимально достаточный read-only query layer для `Module Core`,
который даёт быструю навигацию по governed modules и verification-derived file anchors
уже до появления полного passport/file-contract слоя.
Этот query layer должен быть основным read-only источником context excerpts
для `ExecutionPacket`, review и failure handoff.
Контракт команд должен быть language-agnostic и полезным для `1С/BSL`.

## Границы

### Входит

- набор команд `module find`, `module show`, `file show`;
- режимы вывода `text/json`;
- политика предупреждений;
- разделение shared/public truth в `module show` и file-local/private truth в `file show`;
- query excerpts для packet assembly и verification review;
- язык-независимые поля запроса;
- связь с unified CLI и существующим task query layer.

### Не входит

- мутационные команды;
- полный паритет с `grace` CLI;
- новый task-routing behavior.

## Планируемые изменения

### Код

- новый runtime `scripts/module_core_runtime/read_model.py`;
- новый transport-layer `scripts/module_core_runtime/query_cli.py`;
- расширение unified CLI в `scripts/task_knowledge_cli.py`.

### Конфигурация / схема данных / именуемые сущности

- новые read-only команды `module find`, `module show`, `file show`;
- стабильный JSON payload для partial rollout `Module Core`;
- явные warning-коды для частичного rollout,
  отсутствующего passport/file-contract слоя и multi-owner/ungoverned случаев.

### Документация

- README CLI;
- нормативный `SKILL.md`;
- task-local карточка и план подзадачи.

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- query layer в текущей поставке обязательно читает `verification.md`;
- query layer готов к последующему чтению module passports, relations и file-local contracts;
- query layer не владеет их source-of-truth;
- query layer не должен ожидать единый package/import формат и обязан работать с `1С/BSL`-совместимыми module/file descriptors.

### Границы, которые должны остаться изолированными

- `task` namespace CLI сохраняет текущий контракт;
- module/file namespace остаётся read-only.

### Критический функционал

- быстрый поиск governed module;
- чтение module shared truth;
- чтение file-local truth через verification-derived anchors и fallback refs;
- сборка read-only excerpts для controlled writer handoff;
- единый CLI contract для проектов на разных языках.

### Основной сценарий

- оператор вызывает `task-knowledge module find <query>`;
- открывает `module show <id>`;
- при необходимости читает `file show <path>`.

### Исходный наблюдаемый симптом

- без query surface новые module artifacts будут трудно использовать на практике.

## Риски и зависимости

- слишком широкий CLI scope раздует подзадачу до full `grace-cli`;
- слишком узкий CLI scope не окупит новый `Module Core`;
- если поля query окажутся language-specific, CLI потеряет универсальность и не покроет `1С/BSL`.

## Связь с SDD

- `не требуется`

## Проверки

### Что можно проверить кодом или тестами

- юнит-тесты `test_module_query_runtime`, `test_module_query_architecture` и `test_task_knowledge_cli`;
- `git diff --check`
- команда локализационной проверки документации

### Что остаётся на ручную проверку

- `не требуется`

## Шаги

- [x] Определить набор команд и параметры.
- [x] Определить режимы вывода и JSON-контракт.
- [x] Определить политику предупреждений для partial governed scope.
- [x] Зафиксировать shared/public vs file-local/private truth в output contract.
- [x] Описать query excerpts для `ExecutionPacket` и verifier.
- [x] Увязать новый namespace с существующим unified CLI.
- [x] Зафиксировать language-neutral query contract, пригодный для `1С/BSL`.
- [x] Добавить unit/CLI tests и архитектурную import-границу runtime-слоя.

## Критерии завершения

- query-layer реализован и покрыт unit/CLI tests;
- `task` namespace CLI не получил регрессий;
- partial rollout-режим явно зафиксирован в коде и документации.
