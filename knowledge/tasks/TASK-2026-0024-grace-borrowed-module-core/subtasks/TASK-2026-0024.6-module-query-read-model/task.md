# Карточка задачи TASK-2026-0024.6

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0024.6` |
| Parent ID | `TASK-2026-0024` |
| Уровень вложенности | `1` |
| Ключ в путях | `TASK-2026-0024.6` |
| Технический ключ для новых именуемых сущностей | `module-query` |
| Краткое имя | `module-query-read-model` |
| Человекочитаемое описание | `Добавить read-only команды `task-knowledge module find/show` и `file show` для навигации по `Module Core` и локальному слою file-local contracts.` |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `main` |
| Требуется SDD | `нет` |
| Статус SDD | `не требуется` |
| Ссылка на SDD | `—` |
| Дата создания | `2026-04-20` |
| Дата обновления | `2026-04-20` |

## Цель

Добавить к unified CLI новый read-only контур,
через который можно быстро находить governed modules,
читать их shared/public truth
и смотреть file-local/private truth
без выхода за рамки task-centric модели продукта.
Query-layer должен быть основным read-only способом собрать context для `ExecutionPacket`
и проверить результат через shared/public и file-local/private excerpts.
Query-layer должен одинаково обслуживать разные языки,
включая `1С/BSL`.

## Границы

### Входит

- определить команды `task-knowledge module find`, `task-knowledge module show`, `task-knowledge file show`;
- определить входы, режимы вывода и JSON-контракт;
- определить связи query layer с passports, relation model, verification excerpts и file-local contracts;
- определить `module show --with verification` как источник shared/public verification excerpt;
- определить `file show --contracts --blocks` как источник file-local/private anchors;
- определить language-neutral query fields и фильтры без привязки к одному синтаксису или типу module path;
- определить политику предупреждений и поведение при неполном governed scope.

### Не входит

- mutate-команды для modules;
- расширение task-routing CLI;
- full parity с текущим `grace` CLI по всей surface.

## Контекст

- источник постановки: borrowed-идея fast query/navigation layer по модулям и file-local truth;
- связанная область: read-only операторская навигация по `Module Core`;
- ограничения и зависимости: новый query layer должен дополнять, а не смешивать `task status/current/show` с module-layer;
- дополнительное ожидание: `module show` и `file show` должны быть полезны и для `1С/BSL`-структур, где модульность часто выражается через файлы, подсистемы и контракты, а не через import graph;
- исходный наблюдаемый симптом / лог-маркер: без query surface новые passports, relations и file-local contracts будут плохо доступны оператору и агенту;
- основной контекст сессии: `capability-подзадача Module Core`

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | unified CLI и runtime query modules |
| Конфигурация / схема данных / именуемые сущности | новые команды и JSON payload для `module` / `file` |
| Интерфейсы / формы / страницы | read-only module/file query surface |
| Интеграции / обмены | связь с passports, dependency map, verification catalog и file-local contracts |
| Документация | README CLI, `SKILL.md`, reference docs и task-local описание query behavior |

## Связанные материалы

- родительская задача: `knowledge/tasks/TASK-2026-0024-grace-borrowed-module-core/`
- текущий unified CLI: `skills-global/task-centric-knowledge/README.md`
- существующий task query layer: `skills-global/task-centric-knowledge/scripts/task_query.py`
- reference для `grace` CLI: `/home/prog7/РабочееПространство/work/AI/git-update-only/grace-marketplace/README.md`

## Текущий этап

Подзадача реализована.
В unified CLI добавлены команды `task-knowledge module find`,
`task-knowledge module show` и `task-knowledge file show`.
Реализован новый runtime `module_core_runtime/read_model.py`
и transport-layer `module_core_runtime/query_cli.py`,
которые работают в partial rollout-режиме:
берут `verification.md` как первый live-source,
возвращают стабильный JSON/text contract
и поднимают явные warning'и,
если `module.md`, relation layer
или file-local contracts ещё не внедрены.
Следующий шаг родительской цепочки — `TASK-2026-0024.7`.

## Стратегия проверки

### Покрывается кодом или тестами

- юнит-тесты `test_module_query_runtime`, `test_module_query_architecture` и `test_task_knowledge_cli`
- `git diff --check`
- команда проверки локализации: `bash scripts/check-docs-localization.sh`

### Остаётся на ручную проверку

- `не требуется`

## Критерии готовности

- module/file commands определены;
- режимы вывода и JSON-контракт однозначны;
- `module show` и `file show` явно разделяют shared/public и file-local/private truth;
- query output пригоден для сборки `ExecutionPacket` и read-only verification;
- query-contract не предполагает Python/TypeScript-only структуру и пригоден для `1С/BSL`;
- новый слой не мешает существующему `task` namespace CLI.

## Итоговый список ручных проверок

- `не требуется`

## Итог

Реализован минимально достаточный read-only query layer для `Module Core`.
В `task-knowledge` появились отдельные namespace `module` и `file`,
не затрагивающие существующий `task` contract.

`module find` ищет по `MODULE-ID`, slug, ref и governed files,
поддерживает фильтры по `ExecutionReadiness`
и `source_state`.
`module show` отдаёт shared/public truth, readiness,
verification excerpt и provider-state warning'и.
`file show` работает через project-relative или абсолютный путь,
возвращает owner modules, verification-derived anchors
и ссылки на `FailureHandoff`
и стабильные пустые `contract_markers` / `blocks`
до реализации `TASK-2026-0024.4`.

Принят rollout-режим самостоятельной поставки:
query-layer ship'ится раньше `24.2` и `24.4`
и поэтому обязан работать через partial-mode,
а не блокироваться до появления passport-layer и file-local contracts.
