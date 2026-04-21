# Стратегическая дорожная карта `task-centric-knowledge`

Для изолированного evidence `SDD_AUDIT` использовать `artifacts/stage-1-audit.md`.
Этот документ агрегирует результаты Этапов 1-4 и поэтому не считается единственным основанием закрытия Этапа 1.

## 1. Решение в одном экране

### Иерархия источников истины

- Канонический стратегический источник для `vNext`: этот локальный артефакт задачи `artifacts/strategy-roadmap.md`.
- Дистрибутивный снимок для пользователей skill-а: `skills-global/task-centric-knowledge/references/roadmap.md`.
- Если между ними возникает расхождение до очередной синхронизации, приоритет у дорожной карты задачи `TASK-2026-0008`.
- `registry.md` не является источником истины по смыслу задачи; он остаётся навигационным cache.

### Короткий ответ на ключевые вопросы

- Как жить дальше:
  развивать систему дальше, но не через прямое наращивание новых возможностей поверх текущего монолита.
- Стоит ли остановиться и переосмыслить всё заново:
  нужен архитектурный redesign ядра и границ, но полный rewrite сейчас не нужен.
- Есть ли готовая система, от которой лучше форкнуться:
  по текущему обзору полноценного близкого аналога нет; разумная стратегия — `borrow ideas`, а не `full fork`.

### Базовое стратегическое решение

- Переписывать с нуля не нужно.
- Не форкаться целиком.
- Выбранный путь: redesign ядра без full rewrite, то есть `own core + modular evolution`.
- Продолжать свой путь как операционная система задач внутри репозитория.
- Следующий цикл посвятить `productization/stabilization`, а не очередному расширению поверхности.

## 2. Почему это решение выглядит правильным

### Что уже реально есть в текущем skill-е

Из локального аудита:

- `TASK-2026-0004` зафиксировала git-aware жизненный цикл, маршрутизацию и безопасный upgrade-переход;
- `TASK-2026-0006` добавила testing contract и `verification-matrix`;
- `TASK-2026-0007` перевела skill в publish-centric зону через delivery units и helper publish-flow;
- installer и managed-block deployment;
- жизненный цикл задачи и git-контур;
- маршрутизация между текущей задачей, подзадачей и новой задачей;
- безопасный путь обновления skill-а;
- testing contract и `verification-matrix`;
- publish-flow через delivery units и `du/...` ветки.

Главные технические носители этой сложности сегодня:

- `skills-global/task-centric-knowledge/scripts/install_skill.py`
- `skills-global/task-centric-knowledge/scripts/task_workflow.py`

Иными словами, `task-centric-knowledge` уже занял собственную нишу: это не просто память, не просто проектный трекер и не просто helper для агента.

### Где начинается риск

- `skills-global/task-centric-knowledge/scripts/task_workflow.py` уже стал монолитным orchestration-центром;
- одно правило часто приходится синхронно менять в `SKILL.md`, `references/*.md`, managed-блоках, `knowledge/tasks/README.md`, шаблонах и тестах;
- skill уже выглядит как framework, но ещё не оформлен как framework с ядром и расширениями.

Именно поэтому следующий этап должен быть не `ещё одна крупная capability`, а `сборка правильной формы`.

### Локальные симптомы Этапа 1 с трассировкой

- Монолитность orchestration-слоя:
  ключевой носитель логики по-прежнему сосредоточен в `skills-global/task-centric-knowledge/scripts/task_workflow.py`.
- Drift между каноническим `task.md` и навигационным `registry.md`:
  симптом поднят в `TASK-2026-0008` и должен закрываться только через helper sync, а не через новый источник истины.
- Нормативное дублирование:
  одно и то же правило распределено между `SKILL.md`, `references/*.md`, managed-блоками, шаблонами `knowledge/tasks/` и тестами.
- Drift metadata относительно фактического scope:
  `skills-global/task-centric-knowledge/agents/openai.yaml` должен успевать за capability, добавленными задачами `TASK-2026-0006` и `TASK-2026-0007`.

### Lessons learned из предыдущих задач как ограничения Этапа 1

- `TASK-2026-0004` запрещает терять git-aware жизненный цикл, безопасный upgrade-переход и явную маршрутизацию задач.
- `TASK-2026-0006` требует, чтобы стратегический пакет оставался проверяемым через `verification-matrix`, а не превращался в набор мнений без трассировки.
- `TASK-2026-0007` уже вынес publish-flow в отдельный контур и закрыл внешний smoke; следующий цикл не должен тащить host-specific publish-логику обратно в ядро.

## 3. Внешний landscape: что существует рядом

Этот список является каноническим набором внешних ориентиров для `TASK-2026-0008`.
Дистрибутивный снимок в `skills-global/task-centric-knowledge/references/roadmap.md` обязан сохранять тот же набор источников и тот же вывод: ни один источник не является кандидатом на `full fork`, но каждый даёт ограниченные идеи для заимствования.
Для Этапа 1 валидными считаются только официальные первичные материалы; вторичные обзоры допустимы лишь как навигация, но не как основание для стратегического вывода.

### Канонический официальный source-set Этапа 1

- `GitHub Spec Kit`:
  `github.com/github/spec-kit`, `github.github.com/spec-kit`
- `Claude Code`:
  `docs.anthropic.com`
- `Cursor`:
  `docs.cursor.com`
- `memories.sh`:
  `memories.sh`, `memories.sh/docs`
- Память GitHub Copilot / VS Code:
  `code.visualstudio.com`, `docs.github.com`
- База знаний Devin:
  `docs.devin.ai`
- `OpenHands`:
  `docs.openhands.dev`, `docs.all-hands.dev`
- `LangChain Deep Agents`:
  `docs.langchain.com/oss/python/deepagents`
- Агентные workflows GitHub:
  `github.github.com/gh-aw`

### `GitHub Spec Kit`

- Источники:
  `https://github.com/github/spec-kit`,
  `https://github.github.com/spec-kit/index.html`
- Ценность:
  дисциплина `spec -> plan -> tasks -> implement` и исполняемые спецификации.
- Что брать:
  specification layer и фазность перехода от постановки к реализации.
- Почему не форк:
  это feature-spec workflow, а не repo-local task operating model с registry, task lifecycle и managed upgrade.

### `Claude Code`

- Источники:
  `https://docs.anthropic.com/en/docs/claude-code/memory`,
  `https://docs.anthropic.com/en/docs/claude-code/sub-agents`
- Ценность:
  layered memory, project instructions и изолированные subagents.
- Что брать:
  идеи scoped memory и формальный контракт субагентов.
- Почему не форк:
  это agent runtime и prompt/memory model, а не дистрибутив knowledge-системы задач.

### `Cursor`

- Источники:
  `https://docs.cursor.com/en/context/rules`,
  `https://docs.cursor.com/en/context/memories`
- Ценность:
  scoped rules, project memory и совместимость с `AGENTS.md`.
- Что брать:
  совместимость с project rules и предупреждения о drift-е между слоями инструкций.
- Почему не форк:
  это IDE/context layer без task registry, delivery units и install/upgrade governance.

### `memories.sh`

- Источники:
  `https://memories.sh/`,
  `https://memories.sh/docs`
- Ценность:
  local-first модель памяти и разделение памяти на типы.
- Что брать:
  дорожки памяти: `session`, `semantic`, `episodic`, `procedural`.
- Почему не форк:
  это система памяти, а не система ведения задач с `task.md / plan.md / sdd.md / registry.md`.

### Память GitHub Copilot / VS Code

- Источники:
  `https://code.visualstudio.com/docs/copilot/agents/memory`,
  `https://docs.github.com/en/copilot/how-tos/use-copilot-agents/copilot-memory`
- Ценность:
  области памяти и привязка памяти к контексту.
- Что брать:
  явные области памяти и memory с подтверждёнными источниками.
- Почему не форк:
  память, контролируемая вендором, не заменяет git-tracked и человекочитаемый workflow знаний.

### База знаний Devin

- Источник:
  `https://docs.devin.ai/product-guides/knowledge`
- Ценность:
  onboarding на уровне репозитория и извлечение знаний по триггерам.
- Что брать:
  явные триггеры извлечения знаний и различение знаний репозитория и знаний задачи.
- Почему не форк:
  это knowledge overlay, а не операционная модель задачи внутри репозитория.

### `OpenHands`

- Источники:
  `https://docs.openhands.dev/sdk/guides/task-tool-set`,
  `https://docs.all-hands.dev/usage/prompting/microagents-overview`,
  `https://docs.all-hands.dev/openhands/usage/microagents/microagents-repo`
- Ценность:
  repository customization, microagents и возобновляемые подзадачи.
- Что брать:
  machine-executable subtask flow и packaging микроправил.
- Почему не форк:
  это слой orchestration/tooling, а не task-centric knowledge-дистрибутив со своими managed assets.

### `LangChain Deep Agents`

- Источники:
  `https://docs.langchain.com/oss/python/deepagents/index`,
  `https://docs.langchain.com/oss/python/deepagents/long-term-memory`,
  `https://docs.langchain.com/oss/python/deepagents/human-in-the-loop`
- Ценность:
  planning, subagents, filesystem-backed memory и разделение между memory, skills, HITL и backend policies.
- Что брать:
  backend/policy separation и дисциплину writable/read-only memory.
- Почему не форк:
  это agent harness, а не готовый repo-local task workflow-дистрибутив.

### Агентные workflows GitHub

- Источники:
  `https://github.github.com/gh-aw/`,
  `https://github.github.com/gh-aw/reference/memory/`,
  `https://github.github.com/gh-aw/introduction/how-they-work/`
- Ценность:
  память в git, мышление через package/version/lock и воспроизводимость.
- Что брать:
  package-слой, lock/governance и воспроизводимость для зависимостей skill-а и адаптеров.
- Почему не форк:
  это GitHub Actions-oriented execution framework, а не repo-local task operating model.

### Решения Этапа 2 по открытым вопросам

На `2026-04-12` вопросы Этапа 1 закрыты и больше не считаются открытыми для выбора траектории.
Ниже зафиксирован пакет стратегического решения, с которым закрывается `DECISION_AUDIT`.

#### Какие заимствования обязательны сейчас, а какие откладываются

| Ориентир | Решение Этапа 2 | Что именно переносится |
|----------|-----------------|------------------------|
| `GitHub Spec Kit` | `обязательно сейчас` | дисциплина `spec -> plan -> tasks -> implement` как стратегический шаблон перехода от постановки к delivery-задачам |
| `Cursor` | `обязательно сейчас` | совместимость с project rules и явное предупреждение о drift между слоями инструкций |
| Память GitHub Copilot / VS Code | `обязательно сейчас` | правило, что repo/task memory не подменяет `task.md` и не становится вторым источником истины |
| `Claude Code` | `отложить` | scoped memory и контракт субагентов как будущий слой памяти и orchestration |
| `memories.sh` | `отложить` | taxonomy `session / semantic / episodic / procedural` для будущих memory lanes |
| Devin | `отложить` | onboarding-триггеры и извлечение знаний на уровне репозитория |
| `OpenHands` | `отложить` | machine-executable subtask flow и packaging микроправил |
| `LangChain Deep Agents` | `отложить` | backend/policy separation и дисциплина writable/read-only memory |
| Агентные workflows GitHub | `отложить` | package-слой, lock/governance и воспроизводимость зависимостей skill-а |

#### Где проходит минимальная граница между `core contract` и первой волной декомпозиции

В ближайший `vNext-core` входят:

- канонические сущности `task`, `subtask`, `delivery unit`, `verification matrix`, `task artifact`;
- правило, что `task.md` остаётся источником истины, а `registry.md` — только навигационным кэшем;
- правила маршрутизации, базовые git-инварианты и локальное хранение доказательных артефактов задачи;
- минимальный install/upgrade contract без host-specific и memory-specific поведения.

В первую волну модульной декомпозиции, но не в `core contract`, уходят:

- `domain model`, `markdown io`, `registry sync`, `git ops`;
- `publish flow`, `forge adapters`, `read model / reporting`;
- `memory lanes`, `packaging/governance` и profile-specific расширения.

#### Какие локальные симптомы считаются блокерами, а какие остаются управляемым долгом

Блокеры следующего цикла:

- отсутствие короткого канонического описания ядра и границ владения;
- drift между `task.md` и `registry.md`, если helper не остаётся единственной точкой синхронизации;
- drift между task-local стратегией и skill-level snapshot;
- change amplification из-за нормативного дублирования без первичного стратегического источника.

Управляемый технический долг следующего цикла:

- отсутствие полной memory model;
- отсутствие production-ready parity между GitHub и GitLab;
- отсутствие развитой операторской read-модели сверх минимального `status/current-task/task show`;
- отсутствие package/lock governance как отдельного технического слоя.

#### Какие формулировки обязаны перейти в skill-level snapshot

В `skills-global/task-centric-knowledge/references/roadmap.md` обязательно переходят без искажений:

- иерархия источников истины: task-local roadmap выше skill-level snapshot;
- единый внешний source-set;
- `continue own path`;
- `borrow ideas`;
- `do not fork`;
- `do not rewrite now`;
- `redesign ядра без full rewrite`;
- `own core + modular evolution`.

В task-local roadmap остаются как расширенное обоснование:

- классификация блокеров и управляемого технического долга;
- подробная матрица заимствований `сейчас / отложить`;
- объяснение, почему skill-level snapshot не должен копировать весь evidence Этапа 1.

## 4. Вывод по форку и заимствованию

### Не хватает полного аналога

Ни одна из найденных систем не покрывает одновременно:

- дружественную к git и человеко-читаемую память задачи;
- канонические артефакты `task.md / plan.md / sdd.md`;
- правила маршрутизации `текущая задача / подзадача / новая задача`;
- управляемое installer-развёртывание в проект;
- безопасную эволюцию и обновление;
- publish-flow через delivery units.

### Поэтому решение такое

Итоговый пакет стратегического решения Этапа 2:

- `continue own path`: да
- `borrow ideas`: да
- `do not fork`: да
- `do not rewrite now`: да
- `redesign ядра без full rewrite`: да
- `own core + modular evolution`: да

## 5. Конечная цель `vNext`

### Формулировка

Конечная цель `vNext`:

`task-centric-knowledge` должен стать модульной операционной системой задач внутри репозитория, в которой:

- ядро описывает каноническую доменную модель задачи;
- нормативный источник истины централизован;
- orchestration и publish-flow вынесены в отдельные слои;
- память и интеграции подключаются как расширяемые контуры;
- installer и путь обновления остаются безопасными и предсказуемыми.

### Что обязано остаться в ядре

- канонические сущности:
  `task`, `subtask`, `delivery unit`, `verification matrix`, `task artifact`;
- источник истины по файлам и статусам;
- сводка задачи:
  `TASK-ID`, `Краткое имя`, `Человекочитаемое описание` из `task.md`;
- правила маршрутизации;
- базовые git-инварианты;
- локальное хранение доказательных артефактов задачи;
- минимальный install/upgrade contract.

### Что должно стать отдельными слоями

- `memory model`
- `execution/orchestration`
- `publish/integration`
- `packaging/governance`

## 6. Предлагаемая форма архитектуры

### DDD-карта контекстов

`Task Core` — основной ограниченный контекст.
Его корень агрегата — `Task`, который владеет `Subtask`, `Delivery Unit`, `Verification Matrix`, `Task Artifact`, решениями, worklog и handoff.

`Read Model / Reporting` — прикладной контур поверх `Task Core`.
Он строит `status`, `current-task` и `task show`, но не становится источником истины.

`Publish Integration` — интеграционный ограниченный контекст для адаптеров forge-хостингов и delivery units.
Он не должен протаскивать host-specific правила в core.

`Memory` — расширяемый ограниченный контекст.
Он может добавлять memory lanes, но не конкурирует с `task.md`.

`Packaging / Governance` — install, check, upgrade, doctor и migration cleanup.
Он отвечает за безопасную поставку skill-а и не удаляет project data без `plan -> confirm`.

`Profiles` — профильные надстройки.
Они расширяют формулировки и шаблоны, но не меняют семантику ядра.

### Слой 1. `core contract`

Один короткий канонический документ уровня `vNext-core`, который фиксирует:

- сущности;
- источник истины;
- разрешённые переходы состояний;
- владение по файлам;
- владение локальными доказательными артефактами задачи;
- минимальные обязательные инварианты.

Этот слой должен стать первичным нормативным источником, чтобы уменьшить эффект change amplification.

#### Что Этап 3 обязан зафиксировать уже сейчас

- `Task Core` владеет `task.md`, `plan.md`, `sdd.md` и `artifacts/` как каноническим локальным контуром задачи;
- task summary всегда собирается из `TASK-ID`, `Краткого имени` и `Человекочитаемого описания` в `task.md`;
- `registry.md` и любая CLI read-модель остаются производными проекциями и не могут переопределять смысл задачи;
- `Publish Integration`, `Memory`, `Packaging / Governance` и `Profiles` расширяют ядро, но не получают право обходить канонические переходы `Task Core`;
- cleanup-governance наследует правило `plan -> confirm` и не удаляет project data без раскрытого scope;
- локальное хранение evidence является частью ядра, а не только repo-level дисциплиной.

#### Что сознательно остаётся вне выбора Этапа 3

- не выбирается transport layer CLI: отдельный бинарь, subcommands существующего helper-а или thin wrapper;
- не фиксируется фактическая file-level декомпозиция runtime-модулей;
- не принимается решение по GitLab parity, memory implementation details и package/lock governance;
- не открываются delivery-задачи реализации до закрытия `ARCHITECTURE_AUDIT`.

### Слой 2. `runtime modules`

Разделить текущий helper минимум на:

- `domain model`
- `markdown io`
- `registry sync`
- `git ops`
- `publish flow`
- `адаптеры forge-хостингов`
- `cli`

Цель не в косметическом разделении по файлам, а в отделении политики от транспорта.

### Слой 3. `memory lanes`

Добавить поверх ядра явную модель памяти:

- `project truths`
- `task-local state`
- `episodic history`
- `procedural workflows`

Это не должно ломать существующие `knowledge/tasks/`, а должно дополнять их.

### Слой 4. `adapter surfaces`

Сделать расширяемые интерфейсы для:

- адаптеров forge-хостингов;
- бэкендов памяти;
- hooks для агентной оркестрации;
- профильных overlays.

### Слой 5. `packaging and governance`

Добавить для skill-а более формальную модель версии и совместимости:

- поверхность совместимости;
- ворота обновления;
- возможно lock/manifest для managed assets и adapter capabilities.

### CLI UX как read-модель

Следующий цикл должен включать не только внутренние helper-команды, но и явный операторский слой запросов и отчётности.
Этот слой является read-моделью и прикладным контуром поверх `Task Core`, а не отдельным доменным источником истины.

Минимальная поверхность:

- `status`
- `current-task`
- `task show`
- `doctor deps`
- `migrate cleanup`

Базовые UX-правила:

- любой task-oriented вывод показывает `TASK-ID`, `краткое имя` и человекочитаемое описание;
- `status` отвечает состоянием knowledge-системы в одном экране;
- `current-task` даёт короткий ответ `что сейчас активно и что делать дальше`;
- `doctor deps` различает обязательные, условно-обязательные, опциональные и `not-applicable` зависимости;
- cleanup после миграции не выполняется без явного шага `confirm`.

#### Минимальный публичный контракт команд

- `status` обязан показывать активную ветку, состояние `knowledge/`, активную задачу или warning о неоднозначности, сводку по статусам задач, открытые delivery units и диагностические предупреждения по консистентности knowledge-контура;
- `current-task` обязан возвращать заголовок задачи, текущий этап, ветку, ключевые подзадачи, ближайший следующий шаг и текущие блокеры или ручной остаток;
- `task show` обязан раскрывать карточку задачи с parent/status/priority/branch, целью, текущим этапом, связанными файлами, publish-контуром и коротким verify-блоком;
- `doctor deps` обязан разделять зависимости по классам и явно показывать, что блокирует `core/local mode`, а что блокирует только `publish/integration`;
- `migrate cleanup plan` обязан раскрывать абсолютные пути, `TARGETS`, `TARGET_COUNT`, `COUNT` и точную команду или эквивалент действий;
- `migrate cleanup confirm` обязан повторно показать тот же scope и отказаться от расширения удаления относительно ранее показанного плана.

## 7. Фазовая дорожная карта

### Фаза 0. Ворота стабилизации

Результат:

- закрыт внешний smoke для `TASK-2026-0007`;
- `skills-global/task-centric-knowledge/agents/openai.yaml` синхронизирован с реальным scope;
- сформулирован список текущих нормативных источников и дубликатов;
- собран минимальный список операторских CLI-ожиданий и обязательных полей вывода.

Ворота перехода:

- publish-flow подтверждён хотя бы минимальным внешним smoke;
- нет крупных расхождений между интерфейсным описанием skill-а и фактическими capability.

Что подготавливает дальше:

- открывает короткий вход в `vNext-core`, не споря заново о publish-flow, smoke-gate и исходном scope skill-а;
- фиксирует, что GitLab parity, memory-layer и runtime cleanup остаются вне ядра до завершения стабилизации.

### Фаза 1. Заморозка контракта ядра

Результат:

- создан короткий документ `vNext-core`;
- определены канонические сущности и их переходы состояний;
- определены ограниченные контексты, корень агрегата и границы владения;
- выбран первичный нормативный источник;
- зафиксировано, что относится к ядру, а что нет.
- зафиксировано, какие поля запросов и отчётности обязан отдавать любой task-oriented CLI.
- зафиксировано, что все доказательные артефакты хранятся внутри каталога задачи или явно ссылаются из него.

Ворота перехода:

- любое ключевое правило можно однозначно трассировать в один первичный источник;
- новые изменения больше не требуют менять смысл одного правила в 5-7 местах без центральной опоры.

Что подготавливает дальше:

- открывает отдельный candidate delivery-track на `vNext-core contract`;
- переводит модульную декомпозицию helper-а из архитектурного поиска в реализацию уже зафиксированной границы ядра.

### Фаза 2. Внутренняя модульная декомпозиция

Результат:

- `task_workflow.py` разрезан на модули;
- markdown I/O, доменная логика и git/publish-адаптеры отделены друг от друга;
- тесты начинают проверять доменную модель отдельно от текстового оформления;
- появляется read-модель для `status`, `current-task` и `task show`, не привязанная к mutate-командам.

Ворота перехода:

- основная доменная логика тестируется без тотальной привязки к строковым снимкам;
- monolith helper больше не является единственным носителем всей политики.

Что подготавливает дальше:

- открывает отдельные tracks на `doctor / cleanup governance` и `read model / reporting`, потому что у них появляется собственный runtime-слой;
- превращает change amplification из системного риска в локализуемый технический долг по отдельным модулям.

### Фаза 3. Слои расширения

Результат:

- появляется отдельная memory model;
- оформлены adapter surfaces;
- профильные расширения и интеграции не лезут в core напрямую.

Ворота перехода:

- memory и host integrations можно добавлять без очередного роста центрального монолита;
- новая capability подключается как слой, а не как ещё один special-case внутри core.

Что подготавливает дальше:

- позволяет отдельно решать, когда открывать memory-layer, а когда ограничиваться `core + publish + reporting`;
- ограничивает будущие integrations adapter surfaces, а не разовыми исключениями внутри `Task Core`.

### Фаза 4. Упаковка, обновление и внедрение

Результат:

- формализованы compatibility rules и upgrade story;
- есть migration notes и reference repo patterns;
- skill готов к следующему масштабированию без ручного шаманства;
- `doctor deps` и `migrate cleanup plan/confirm` становятся частью стандартного install/upgrade UX.

Ворота перехода:

- upgrade path воспроизводим и проверяем;
- пользователю понятно, какой слой он берёт: core only, core + publish, core + memory и так далее;
- оператор получает понятные ответы на запросы `status` и `current-task`, а cleanup после миграции остаётся подтверждаемым.

Что подготавливает дальше:

- переводит `task-centric-knowledge` из эволюции одного локального skill-а в воспроизводимый продукт для внешних репозиториев;
- создаёт базу для следующего цикла улучшений только через полевую валидацию, а не через интуитивное расширение монолита.

## 8. Следующая волна candidate delivery-tracks

Эта очередь intentionally остаётся стратегической.
Ни один пункт ниже ещё не является почти готовым `task.md`; каждый фиксирует только назначение, границы и ожидаемый выход следующего цикла.

### Track 1. `vNext-core contract`

Назначение:

- закрепить короткий нормативный документ ядра и DDD-карту без смешивания с runtime helper-логикой.

Границы:

- входит: канонические сущности, переходы состояний, источник истины, правило локального хранения evidence;
- не входит: file-level decomposition, host adapters, `doctor deps`, transport layer CLI.

Ожидаемый выход:

- один первичный нормативный документ ядра и явная карта контекстов, на которые смогут опираться все последующие задачи.

### Track 2. Модульная декомпозиция helper-а

Назначение:

- вынести доменную модель, markdown I/O, sync, git/publish-операции и CLI-слой из одного orchestration-монолита.

Границы:

- входит: разрез по зонам ответственности и перенос unit-тестов на модульный уровень;
- не входит: изменение стратегического курса, смена публичных intent-имен, расширение publish-host parity.

Ожидаемый выход:

- `task_workflow.py` перестаёт быть единственным носителем политики, а доменная логика становится тестируемой отдельно от строковых снимков.

### Track 3. `doctor / cleanup governance`

Назначение:

- превратить install/upgrade-диагностику и cleanup после миграции в отдельный safety-oriented контур.

Границы:

- входит: классы зависимостей, блокирующие слои, `plan -> confirm`, scope-lock и migration diagnostics;
- не входит: удаление project data без явного плана, массовый upgrade tooling или полевой adoption package.

Ожидаемый выход:

- оператор получает предсказуемый `doctor deps` и подтверждаемый `migrate cleanup`, не конкурирующие с `Task Core`.

### Track 4. `Read model / reporting`

Назначение:

- оформить query/reporting layer поверх `Task Core`, не превращая его в новый источник истины.

Границы:

- входит: `status`, `current-task`, `task show`, task-oriented read-модель и предупреждения о неоднозначности;
- не входит: изменение канонической сводки задачи, перенос смыслов из `task.md` в registry/read-model, runtime-мутирующие команды.

Ожидаемый выход:

- появляется прикладной слой ежедневного operator UX, который читает ядро, но не владеет им.

### Track 5. Полевая валидация

Назначение:

- проверить продуктовую форму skill-а на внешних репозиториях до нового витка расширения.

Границы:

- входит: reference repo patterns, quickstart/adoption package, журнал friction и возврат в roadmap только подтверждённых улучшений;
- не входит: спекулятивные улучшения без полевой проверки, расширение product scope ради гипотетических кейсов.

Ожидаемый выход:

- следующий цикл развития определяется реальными friction-сигналами, а не локальной интуицией разработчика.

Подтверждённые сигналы по `TASK-2026-0014`:

- clean install требует явного bootstrap-порядка первой задачи:
  если `install` и первые task-файлы уже сделали дерево dirty, `task_workflow.py --create-branch` останавливается корректно;
  валидированный путь сейчас — ручная `task/...` ветка и затем `--register-if-missing`;
- для больших `1c`-репозиториев governance/adoption validation нужно проводить вне `tmpfs`
  или через sparse-checkout `AGENTS.md + knowledge/**`; полный checkout не является обязательным для такого класса проверки;
- на shared `main` read-model должен оставаться warning-first:
  ambiguity и legacy drift-сигналы — это ожидаемый operator feedback, а не повод молча выбирать задачу.

### Чего пока не делать

- Не добавлять новые большие capability прямо в текущий helper-монолит.
- Не открывать memory-layer до завершения `vNext-core contract`, декомпозиции helper-а и read-model/governance tracks.
- Не перепридумывать всю систему как universal agent platform.
- Не уходить в full fork от внешней системы.

## 9. Стоп-критерии для самой roadmap

- Если после `Фазы 1` ядро всё ещё нельзя описать коротко и однозначно, значит текущая модель переусложнена и нужен более жёсткий redesign.
- Если после `Фазы 2` модульность не снижает change amplification, значит разрез выбрали неправильно.
- Если после `Фазы 2` следующая волна снова требует добавлять capability прямо в текущий helper-монолит, roadmap нужно пересмотреть до старта реализации.
- Если `memory model` начинает конкурировать с `task.md` за роль источника истины, развитие нужно останавливать и упрощать.
- Если skill-level snapshot начинает расходиться с task-local roadmap по фазам, воротам или очереди следующей волны, любой новый track должен быть остановлен до повторной синхронизации.
- Если внешняя система внезапно появится и действительно покроет почти весь ваш контракт, вопрос форка нужно открыть заново уже на новом фактическом основании.

## 10. Итоговая позиция

`task-centric-knowledge` уже слишком самобытен, чтобы его было рационально заменить чужой системой целиком.
Но он ещё недостаточно оформлен, чтобы без остановки продолжать наращивать функциональность.

Правильный следующий ход:

- остановить экспансию поверхности;
- стабилизировать ядро;
- разрезать монолит;
- заимствовать хорошие идеи извне;
- только потом снова ускоряться.
