# Карточка задачи TASK-2026-0024

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0024` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0024` |
| Технический ключ для новых именуемых сущностей | `module-core` |
| Краткое имя | `grace-borrowed-module-core` |
| Человекочитаемое описание | `Открыть post-release трек на точечные module-centric заимствования из GRACE без превращения task-centric-knowledge в полный GRACE framework.` |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `main` |
| Требуется SDD | `да` |
| Статус SDD | `завершено` |
| Ссылка на SDD | `sdd.md` |
| Дата создания | `2026-04-20` |
| Дата обновления | `2026-04-21` |

## Цель

Открыть и структурировать отдельный рабочий трек, который добавит к `task-centric-knowledge` лёгкий `Module Core`-слой:
модульные паспорта,
минимальный dependency-map,
file-local contracts для hot spots,
каталог модульной верификации,
read-only query по модулям и
обновляемый borrowed-layer из актуального GRACE checkout,
versioned upgrade-процесс со старых версий системы и
governance legacy backfill для старых задач
и controlled execution-thread для single-writer делегирования правок
без потери standalone-границы, зафиксированной в `TASK-2026-0021`,
причём весь новый слой обязан быть универсальным по отношению к языку и стеку проекта,
включая явную пригодность для репозиториев на `1С/BSL`.

## Подсказка по статусу

Использовать только одно из значений:

- `черновик`
- `готова к работе`
- `в работе`
- `на проверке`
- `ждёт пользователя`
- `заблокирована`
- `завершена`
- `отменена`

## Git-подсказка

- Поле `Ветка` хранит текущую активную ветку рабочего контекста, а не обязательную долгоживущую task-ветку.
- При открытии верхнеуровневой задачи стартовый контекст обычно синхронизируется в `task/<task-id-lower>-<slug>`.
- Для первой и последующих поставок helper может переводить `Ветка` в delivery-ветку вида `du/<task-id-lower>-uNN-<slug>`.
- Для подзадачи по умолчанию можно указывать ветку родителя, если отдельная ветка или delivery unit не нужны.
- При каждом создании или переключении ветки нужно синхронизировать это поле и строку в `registry.md`.

## Границы

### Входит

- открыть отдельную post-release задачу после `TASK-2026-0021` под module-centric borrowings из GRACE;
- декомпозировать работу на одну cross-cutting подзадачу `source/refresh`, один governance-track `upgrade/backfill` и пять capability-подзадач;
- зафиксировать local-first механизм обновления borrowed-layer из GRACE через source manifest с pinned revision и local checkout override;
- зафиксировать versioned upgrade path старой версии knowledge-системы на новую без потери `project data` и без смешивания upgrade-commit с последующей продуктовой работой;
- зафиксировать умеренную policy для старых task-артефактов:
  закрытые задачи получают только compatibility-backfill и migration-note без переписывания исторического narrative;
  активные и незавершённые задачи допускается доводить до новых правил глубже;
- зафиксировать продуктовую границу, в которой `Module Core` является companion-layer к `Task Core`, а не новой полной заменой `task-centric-knowledge`;
- зафиксировать execution-модель `main orchestrator + parallel read-only scouts + single sequential writer + read-only verifier`;
- зафиксировать, что главный агент владеет task-truth, readiness gate, packet issuance, приёмкой и интеграцией, а writer-subagent получает только ограниченный write-scope;
- зафиксировать repo-native контракты `ExecutionPacket`, `ResultPacket`, `FailureHandoff` и `ExecutionReadiness`;
- зафиксировать language-agnostic требование:
  `Module Core` не должен зависеть от одного семейства языков, синтаксиса или toolchain и обязан быть применим к Python, TypeScript, Go, shell, `1С/BSL` и другим языкам, где проектная память ведётся через файлы;
- подготовить task-local контекст, достаточный для дальнейшей детальной спецификации и самостоятельной реализации каждой подзадачи.

### Не входит

- немедленная реализация `Module Core` в этом ходе;
- превращение skill-а в contract-first XML framework уровня GRACE;
- unrestricted multi-agent editing, multiwriter waves и отдельная orchestration-платформа;
- выдача writer-subagent прав на `task.md`, `plan.md`, `sdd.md`, `registry.md` или shared governance-документы;
- обязательная repo-wide semantic markup разметка всех файлов;
- проектирование capability только под языки с богатыми import-graph или AST и игнорирование `1С/BSL` / file-centric кодовых баз;
- массовое переписывание закрытых исторических задач так, как будто новая версия системы существовала в момент их выполнения;
- автосетевой fetch или silent refresh borrowed-layer без явного `plan -> apply`;
- удалённая публикация, `push` и PR/MR в рамках открытия этого рабочего трека.

## Контекст

- источник постановки: запрос пользователя от `2026-04-20` открыть задачу по доработке, спланировать общие подзадачи по пяти borrowed-capability и продумать механизм обновления заимствований из оригинального репозитория;
- связанная бизнес-область: post-release развитие `task-centric-knowledge` как standalone task-centric operating system с companion module-centric слоем;
- ограничения и зависимости: решение `TASK-2026-0021` сохраняет базовую траекторию `standalone`, допускает `adapter` как резерв и запрещает превращать продукт в `свой GRACE`;
- дополнительное продуктовое ожидание пользователя: новая система должна быть полностью универсальной для любых языков и явным образом охватывать `1С/BSL`, а не только Python/TypeScript-проекты;
- дополнительное продуктовое ожидание пользователя: новая версия должна включать upgrade-процесс со старых версий системы и policy по обновлению старых задач без подмены их исторического source-of-truth;
- дополнительное продуктовое ожидание пользователя: правки может выполнять субагент, но только один и строго последовательно; главный агент остаётся orchestrator/controller, приёмщиком и владельцем истины по задаче;
- исходный наблюдаемый симптом / лог-маркер: для ветки `main` нет активной новой задачи под post-release module-centric borrowings, а старые артефакты ссылаются на устаревший абсолютный путь GRACE checkout;
- основной контекст сессии: `новая верхнеуровневая задача после TASK-2026-0021`

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | Будущие изменения ожидаются в `scripts/task_knowledge_cli.py`, runtime query/helper-модулях, installer/managed refresh-контуре и execution/readiness helper-слое skill-а с language-agnostic contract, не привязанным к конкретному parser/runtime |
| Конфигурация / схема данных / именуемые сущности | Появится companion-слой `Module Core`, source manifest borrowed-layer, `ExecutionPacket`, `ResultPacket`, `FailureHandoff`, `ExecutionReadiness`, versioned upgrade/backfill policy и новые read-only CLI-команды с форматом, пригодным для разных языков, включая `1С/BSL` |
| Интерфейсы / формы / страницы | Операторский CLI `task-knowledge` получит module/query и borrowings/status-refresh команды |
| Интеграции / обмены | Borrowed-layer будет опираться на GRACE upstream как внешний источник, но через pinned manifest и local-first refresh-governance без допущения, что upstream-паттерны работают только для одного стека; upgrade-контур будет опираться на существующий installer governance |
| Документация | `task.md`, `plan.md`, `sdd.md`, `artifacts/verification-matrix.md` этой задачи, task-local карточки подзадач и будущие `SKILL.md` / `references/*.md` изменения с явной фиксацией language-agnostic границы и migration/backfill policy |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0024-grace-borrowed-module-core/`
- файл плана: `plan.md`
- файл SDD: `sdd.md`
- файл verification matrix: `artifacts/verification-matrix.md`
- граница продукта и решение `standalone / adapter / pivot`: `knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/artifacts/v1-product-thesis.md`
- безопасный upgrade старой версии: `skills-global/task-centric-knowledge/references/upgrade-transition.md`
- модель `GRACE + task-layer` для 1С-легаси: `knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/artifacts/grace-task-layer-1c-model.md`
- стратегический source-of-truth по `borrow ideas`: `knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/strategy-roadmap.md`
- канонический контракт `Task Core`: `skills-global/task-centric-knowledge/references/core-model.md`
- актуальный локальный GRACE checkout: `/home/prog7/РабочееПространство/work/AI/git-update-only/grace-marketplace/`
- пользовательские материалы: сообщения пользователя от `2026-04-20`
- связанные коммиты / PR / ветки: `task/task-2026-0024-grace-borrowed-module-core`
- связанные операции в `knowledge/operations/`, если есть: `нет`

## Контур публикации

Delivery unit для текущего открытия рабочего трека пока не требуется.

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | — | `—` | `—` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |

## Текущий этап

Задача завершена.
Цепочка `TASK-2026-0024.1 -> 24.5 -> 24.6 -> 24.7 -> 24.2 -> 24.3 -> 24.4`
полностью закрыта,
task-local docs синхронизированы с фактическим rollout-состоянием,
а финальный review-fix устранил оставшийся knowledge-drift
между read-model, verification matrix и верхнеуровневой карточкой.
`Module Core` зафиксирован как language-agnostic companion-layer,
borrowings/readiness/query/relations/file-local/governance surface реализованы,
и обязательных implementable шагов внутри `TASK-2026-0024` больше не осталось.
Независимая задача `TASK-2026-0001` по-прежнему не входит
в execution/governance-цепочку этого трека
и остаётся parked backlog вне данной задачи,
если не появится отдельный внешний приоритет.

## Стратегия проверки

### Покрывается кодом или тестами

- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules status --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules current-task --format json`
- `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'`
- `python3 skills-global/task-centric-knowledge/scripts/task_workflow.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules --task-dir knowledge/tasks/TASK-2026-0024-grace-borrowed-module-core --register-if-missing --format json`
- `git diff --check`
- команда проверки локализации: `bash scripts/check-docs-localization.sh`

### Остаётся на ручную проверку

- `не требуется`

## Критерии готовности

- открыта отдельная верхнеуровневая задача с branch-aware task-контуром после `TASK-2026-0021`;
- созданы семь подзадач, каждая с собственным task-local контекстом и ясной ролью в общем рабочем треке `Module Core`;
- механизм borrowed refresh зафиксирован как local-first `Pin + Local` подход, а не как хрупкая ссылка на один абсолютный путь;
- versioned upgrade и legacy-backfill policy описаны как отдельный governed контур без реткона закрытых задач;
- новая задача не спорит с границей `standalone + adapter as reserve`, а использует её как базовое ограничение;
- все capability описаны как language-agnostic surface, совместимая в том числе с `1С/BSL`, а не как Python/TypeScript-only слой;
- execution-layer описан как controller-guided single-writer model, где writer-subagent не меняет task-truth и shared governance;
- в `registry.md` отражены задача и все значимые подзадачи.

## Итоговый список ручных проверок

- `не требуется`

## Итог

В рамках текущего хода открыта новая верхнеуровневая задача `TASK-2026-0024`
как post-release трек на точечные module-centric заимствования из GRACE.
Контур задачи сразу декомпозирован в гибридную структуру:
одна cross-cutting подзадача под source/refresh-governance,
одна governance-подзадача под versioned upgrade и legacy backfill,
и пять capability-подзадач под `Module Core`.

Это сохраняет продуктовую формулу `task-centric-knowledge` как standalone task-centric OS,
а финальный review-fix зафиксировал завершение всего верхнеуровневого трека:
устранён остаточный knowledge-drift по статусу задачи,
verification matrix переведена в фактически покрытое состояние,
и read-model больше не ссылается на уже реализованную подзадачу
как на отсутствующую capability.
но создаёт формальный backlog для companion-слоя,
который можно реализовывать поэтапно и обновлять из upstream GRACE
без повторного стратегического спора о pivot в full framework.
Дополнительный обязательный инвариант этого трека:
`Module Core` проектируется как язык-независимая система инженерной памяти,
пригодная для file-centric репозиториев на `1С/BSL`
наравне с Python/TypeScript/Go-кодовыми базами.
Дополнительный governance-инвариант:
переход старых версий и старых задач на новую модель должен быть versioned и безопасным,
но не должен переписывать задним числом исторический narrative завершённых задач.
Дополнительный execution-инвариант:
заимствования из GRACE должны усиливать контролируемое делегирование через execution packet,
readiness gate и failure handoff,
но не должны превращать `task-centric-knowledge` в parallel multiwriter framework.
