# План задачи TASK-2026-0024

## Правило

Для задачи существует только один файл плана: `plan.md`.
Если задача декомпозируется, каждая подзадача получает свой собственный `plan.md` внутри своей папки.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0024` |
| Parent ID | `—` |
| Версия плана | `3` |
| Связь с SDD | `sdd.md`, `artifacts/verification-matrix.md` |
| Дата обновления | `2026-04-21` |

## Цель

Подготовить и запустить отдельный рабочий трек `Module Core`,
в котором точечные module-centric capability заимствуются из GRACE
без смены продуктовой роли `task-centric-knowledge` и
с локально обновляемым borrowed-layer через pinned source manifest.
Новый слой должен быть language-agnostic и одинаково применим
к репозиториям на Python, TypeScript, Go, shell и `1С/BSL`.
Одновременно должен быть описан versioned переход со старых версий системы
и умеренная policy по legacy task backfill.
Дополнительно контур должен принять repo-native execution-модель:
главный агент остаётся controller и владельцем task-truth,
read-only scouts работают параллельно,
а ровно один writer-subagent выполняет последовательный write-pass по точному `ExecutionPacket`.

## Границы

### Входит

- открыть отдельную задачу и семь подзадач для `Module Core` track;
- описать общую архитектурную рамку borrowed-layer и refresh-governance;
- описать versioned upgrade path и policy legacy task backfill;
- зафиксировать очередность capability-подзадач и их границы;
- заранее определить, какие будущие артефакты и CLI-команды должны появиться;
- встроить в существующие подзадачи execution-thread:
  `ExecutionPacket`, `ResultPacket`, `FailureHandoff`, `ExecutionReadiness`;
- зафиксировать single-writer ownership:
  writer может менять код, конфиги, тесты и локальные repo-docs только в granted scope,
  но не `task.md`, `plan.md`, `sdd.md`, `registry.md` и shared governance-истину;
- зафиксировать, что все будущие схемы, маркеры, query-контракты и verification records не могут зависеть от конкретного языка или AST-модели и должны быть пригодны для `1С/BSL`;
- увязать новую работу с ранее подтверждёнными решениями `TASK-2026-0008` и `TASK-2026-0021`.

### Не входит

- непосредственная реализация `knowledge/modules/`, новых CLI-команд и локальной разметки файлов в этом ходе;
- массовое обновление `SKILL.md`, `references/*.md` и тестов под новый слой;
- массовый реткон закрытых задач под narrative новой версии системы;
- открытие отдельной новой подзадачи под orchestration вместо вшивания execution-thread в текущие `24.1`, `24.5`, `24.6`, `24.7`;
- full GRACE XML platform, multiwriter waves и отдельная orchestration-платформа;
- network fetch, sync с GitHub и любые publish-действия.

## Планируемые изменения

### Код

- кодовые изменения в этом ходе не требуются; будущий scope ожидается в `scripts/task_knowledge_cli.py`, runtime query/helper-модулях и installer/managed refresh-контуре.

### Конфигурация / схема данных / именуемые сущности

- создаётся новая task-local декомпозиция под `Module Core`;
- фиксируется будущий source manifest borrowed-layer с полями `origin_url`, `pinned_revision`, `local_checkout_override`;
- фиксируется будущая migration/backfill policy с классификацией legacy задач по степени допустимого обновления;
- фиксируется будущий managed-root `knowledge/modules/`.
- фиксируется repo-native vocabulary:
  `ExecutionPacket`, `ResultPacket`, `FailureHandoff`, `ExecutionReadiness`.

### Документация

- `task.md`, `plan.md`, `sdd.md`, `artifacts/verification-matrix.md` задачи `TASK-2026-0024`;
- `task.md` и `plan.md` семи подзадач;
- последующая реализация должна обновить `SKILL.md`, `references/core-model.md`, `references/roadmap.md` и README skill-а.
- downstream-карта должна дополнительно обновить `references/upgrade-transition.md` и `references/deployment.md`,
  чтобы новая execution-модель внедрялась через versioned rollout/backfill.

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- в этом ходе не меняются;
- будущая реализация должна вводить `Module Core` как companion-слой поверх уже существующего `Task Core`, без права перезаписывать его source-of-truth.
- будущая реализация не должна требовать language-specific parser-а как обязательной предпосылки и должна сохранять работоспособность на file-centric кодовых базах, включая `1С/BSL`.
- upgrade/backfill слой не должен подменять исторический смысл завершённых задач и обязан отделять compatibility-sync от narrative rewrite.

### Границы, которые должны остаться изолированными

- `Task Core` остаётся владельцем `task.md`, `registry.md`, статусов задачи и publish lifecycle;
- главный агент остаётся владельцем постановки, readiness gate, packet issuance, приёмки и task-local truth;
- writer-subagent не получает права менять task-local source-of-truth и shared governance docs;
- borrowed-layer из GRACE должен быть one-way и governed, без неявного обратного sync;
- локальная разметка файлов разрешена только для governed hot spots и не становится обязательной для всего репозитория;
- каталог модульной верификации не заменяет task-local `artifacts/verification-matrix.md`, а только переиспользуется ею.
- ни один capability-track не может предполагать, что модуль определяется только через импортируемые пакеты, стандартные namespace или syntax-aware tooling;
- `1С/BSL` и другие языки с иной структурой файлов/модулей должны поддерживаться через те же общие контракты `Module Core`.
- закрытые исторические задачи допускают только compatibility-backfill и migration-note;
- активные и незавершённые задачи допускается доводить до новых правил глубже, если это не разрушает их текущий рабочий контур.

### Критический функционал

- новая задача и подзадачи дают implement-ready контекст для следующей волны post-release работ;
- execution-thread даёт implement-ready контракт для controlled subagent work:
  `main orchestrator + parallel read-only scouts + single sequential writer + read-only verifier`;
- механизм refresh borrowed-layer не зависит от одного устаревающего абсолютного пути;
- versioned upgrade path не смешивается с borrowed refresh и с capability delivery;
- все пять borrowed-capability разведены по отдельным подзадачам и не смешиваются в один «большой GRACE-track».
- language-agnostic контракт не требует отдельных продуктовых fork-веток под разные языки и применим в том числе к `1С/BSL`.

### Основной сценарий

- оператор или агент читает `TASK-2026-0024`, видит границы `Module Core` и находит следующую подзадачу;
- реализация начинается с `TASK-2026-0024.1`, где вводится source/refresh governance;
- затем первой поднимается `TASK-2026-0024.5`,
  которая фиксирует readiness gate,
  выдержку верификации
  и `FailureHandoff`
  как обязательный вход в controlled writer-pass;
- после неё поднимается `TASK-2026-0024.6`,
  чтобы execution packet,
  модульная верификация
  и file-local truth читались через единый read-only query layer;
- затем поднимается `TASK-2026-0024.7`,
  где rollout новой execution-модели,
  версионированный переход
  и legacy backfill уже опираются на конкретный verification/query-контур,
  а не на абстрактные будущие сущности;
- только после стабилизации цепочки `24.5 -> 24.6 -> 24.7`
  возвращаются отложенные capability-подзадачи `24.2 -> 24.3 -> 24.4`,
  чтобы schema passports,
  модель связей
  и file-local contracts фиксировалась уже поверх готового execution/governance контура,
  не ломая standalone-формулу продукта.

### Исходный наблюдаемый симптом

- post-release backlog под borrowed `Module Core` отсутствует как отдельная task-сущность;
- старые артефакты фиксируют связь с GRACE, но реальный checkout уже переехал, и это требует устойчивого refresh-механизма.
- у новой волны пока нет явной policy, как переводить старые версии системы и старые задачи на новый слой без потери историчности.

## Риски и зависимости

- если borrowed-layer будет описан слишком широко, задача конфликтует с продуктовой границей `TASK-2026-0021`;
- если refresh-механизм привязать к одному checkout path, он быстро устареет и снова создаст knowledge-drift;
- если capability-подзадачи не будут разведены по scope, следующая реализация быстро превратится в full framework track.
- если схемы будут завязаны на Python/TypeScript-style модули, система потеряет универсальность и не сможет честно поддерживать `1С/BSL`.
- если legacy backfill будет смешан с переписыванием narrative закрытых задач, система потеряет историческую достоверность;
- если upgrade и backfill не будут формализованы, новая версия окажется неполной для реального внедрения.
- если execution-thread не будет встроен в текущие подзадачи, `Module Core` останется пассивной памятью и не даст безопасного single-writer делегирования;
- если writer-subagent сможет менять task-truth, главный агент потеряет роль controller и приёмщика.

## Связь с SDD

- Этап 1: зафиксировать boundary между `Task Core` и `Module Core`, а также invariant set borrowed-layer;
- Этап 2: описать refresh-governance и source manifest как первый обязательный слой;
- Этап 3: описать versioned upgrade path и policy legacy task backfill;
- Этап 4: определить capability-состав `Module Core` и минимальные интерфейсы;
- Этап 5: определить verify-контур, readiness gate и failure handoff, через которые новая модель доказывается тестами и CLI-проверками;
- Этап 6: синхронизировать downstream-карту для `SKILL.md`, README и reference docs;
- матрица покрытия: `artifacts/verification-matrix.md`.

## Проверки

### Что можно проверить кодом или тестами

- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules status --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules current-task --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_workflow.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules --task-dir knowledge/tasks/TASK-2026-0024-grace-borrowed-module-core --register-if-missing --format json`
- `git diff --check`
- команда проверки локализации: `bash scripts/check-docs-localization.sh`

### Что остаётся на ручную проверку

- `не требуется`

## Шаги

- [x] Открыть отдельную верхнеуровневую задачу после `TASK-2026-0021`.
- [x] Зафиксировать гибридную декомпозицию: `source/refresh` + `upgrade/backfill governance` + пять capability-подзадач.
- [x] Описать в task-local артефактах local-first механизм borrowed refresh из GRACE.
- [x] Зафиксировать policy `2`: закрытые задачи только compatibility-backfill, активные допускается доводить до новых правил глубже.
- [x] Подготовить implement-ready контекст для дальнейшей детализации каждой подзадачи.
- [x] Вшить GRACE borrowings в repo-native execution-thread без открытия новой подзадачи.
- [x] Синхронизировать подзадачи `24.1`, `24.5`, `24.6`, `24.7` как связанную цепочку controlled execution.
- [x] Детализировать `TASK-2026-0024.1` как source/refresh и borrowed packet vocabulary foundation.
- [x] Детализировать и реализовать `TASK-2026-0024.5` как readiness gate, verification excerpt и failure handoff.
- [x] Детализировать и реализовать `TASK-2026-0024.6` как query-layer для shared/public и file-local/private truth.
- [x] Детализировать и реализовать `TASK-2026-0024.7` как governed upgrade/backfill track для legacy и execution-policy rollout.
- [x] После стабилизации execution/governance-цепочки вернуться к `TASK-2026-0024.2` и определить managed-root `knowledge/modules/` поверх уже зафиксированных verification/query контрактов.
- [x] Затем поднять `TASK-2026-0024.3` и определить lightweight dependency map уже относительно согласованной passport/query модели связей.
- [x] Затем поднять `TASK-2026-0024.4` и зафиксировать file-local contracts после того, как их anchors и excerpts уже привязаны к `24.5` и `24.6`.
- [x] Закрыть верхнеуровневую задачу `TASK-2026-0024` и синхронизировать task-local read-model после финального review-fix.

### Явно зафиксированный порядок backlog

1. Сначала `TASK-2026-0024.2`
2. Затем `TASK-2026-0024.3`
3. Цепочка capability-подзадач `24.2 -> 24.3 -> 24.4` завершена
4. Верхнеуровневая задача `TASK-2026-0024` закрыта после финального review-fix и verify-pass

Отдельная задача `TASK-2026-0001` не входит в этот внутренний порядок
и остаётся parked backlog после завершения цепочки `24.2 -> 24.3 -> 24.4`,
если не возникнет внешний срочный приоритет.

## Критерии завершения

- top-level backlog под `Module Core` существует как самостоятельная задача;
- все подзадачи созданы и зарегистрированы;
- стратегия `Pin + Local` для borrowed refresh отражена в задаче и SDD;
- versioned upgrade и legacy task backfill policy отражены в задаче и SDD;
- открытая задача не нарушает ранее зафиксированную standalone-границу продукта;
- открытая задача явно удерживает language-agnostic требование и не уходит в language-specific контракт.
- execution-thread описан как `main orchestrator + single sequential writer`, а не как unrestricted multiagent editing;
- downstream-карта будущих изменений в `SKILL.md`, README и reference docs зафиксирована.
