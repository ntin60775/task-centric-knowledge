# Дорожная карта развития `task-centric-knowledge`

## 0. Канонический источник

- Канонический стратегический источник для `vNext`: `knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/strategy-roadmap.md`.
- Канонический дистрибутивный snapshot модели ядра: `references/core-model.md`.
- Канонический нормативный источник для модели `Task Core` должен жить в отдельном task-local contract-документе Track 1, а не размазываться между roadmap, README и шаблонами.
- Этот файл является дистрибутивным снимком той же стратегии для пользователей skill-а.
- Для вопросов фазности, gate-ов и очереди track-ов приоритет остаётся у `TASK-2026-0008`.
- Для operator-level вопросов source-of-truth, ownership по файлам, state-machine и evidence / cleanup governance приоритет у `references/core-model.md`, синхронизированного с `TASK-2026-0010`.
- Для вопросов агрегата `Task Core`, source-of-truth, ownership по файлам, state-machine и evidence / cleanup governance приоритет у утверждённого task-local core contract.
- Если дорожная карта задачи и этот reference-файл временно расходятся, до следующей синхронизации приоритет у дорожной карты задачи.

## 1. Короткий ответ на главный вопрос

### Как жить дальше

Жить дальше не через хаотичное добавление новых правил, а через явное разделение навыка на слои:

- контракт ядра для модели задачи, маршрутизации, артефактов и инвариантов;
- `local automation` для install/check/open/sync/doctor без сетевых обещаний;
- `publish adapters` для GitHub/GitLab и других forge-хостингов как опционального слоя;
- профили и примеры для доменно-специфичных формулировок вроде `generic` и `1c`.

### Нужно ли остановиться и переосмыслить всё заново

Полная остановка с переписыванием с нуля сейчас не нужна.
Нужна короткая фаза архитектурного уплотнения: зафиксировать ядро, разгрузить helper-монолит и перестать расширять ядро за счёт host-specific и process-specific деталей.

### Есть ли система, от которой лучше форкнуться

На `2026-04-10` не видно одной внешней системы, которая покрывает всю комбинацию требований `task-centric-knowledge` лучше текущего skill-а.
Рациональное решение: не форкаться целиком, а заимствовать отдельные идеи и практики из нескольких систем.

## 2. Где skill находится сейчас

По локальному дистрибутиву skill уже прошёл как минимум три крупных волны:

- `TASK-2026-0004`: git-жизненный цикл задачи и маршрутизация `текущая задача / подзадача / новая задача`;
- `TASK-2026-0006`: тестовый контракт с приоритетом реально допустимой автоматизации и единым ручным checklist;
- `TASK-2026-0007`: publish-flow через delivery units, PR/MR и host adapters.

После этого `vNext`-контур был не только спроектирован, но и реализован отдельными delivery tracks:

- `TASK-2026-0010`: канонический `Task Core` contract;
- `TASK-2026-0011`: модульная декомпозиция helper/runtime;
- `TASK-2026-0012`: `doctor-deps` и `migrate-cleanup-plan/confirm`;
- `TASK-2026-0013`: `read-model` `status / current-task / task show`;
- `TASK-2026-0014`: полевая валидация и adoption package.

Это означает, что skill уже перестал быть только раскладкой шаблонов и стал полноценным процессным слоем для agent-driven разработки.

### Сильные стороны текущей версии

- локальный источник истины репозитория через `knowledge/tasks/<TASK-ID>-<slug>/task.md`;
- жёсткая маршрутизация между новой задачей, подзадачей и продолжением текущей;
- дисциплина установки и обновления, а также различение managed-files и project data;
- publish-aware модель, не сводящая всё к одной долгоживущей ветке;
- достаточно развитый тестовый контур для installer/helper поведения;
- отдельный дистрибутивный `Task Core` snapshot в `references/core-model.md`;
- governance-слой `doctor-deps` и `migrate-cleanup-plan/confirm`;
- read-only операторский CLI `status / current-task / task show`;
- field-validated adoption patterns для `clean`, `mixed_system` и `compatible/1c`.

### Реальные признаки перегруза

- facade-entrypoints уже стали тонкими, а runtime разрезан на модули, но исторический narrative всё ещё несёт следы pre-vNext эпохи;
- правила всё ещё можно случайно размазать между `SKILL.md`, `references/*.md`, managed-блоками и шаблонами;
- главная remaining зона риска сейчас — document drift между task-local решениями и дистрибутивным reference-слоем;
- риск превращения skill-а в слишком общий meta-framework всё ещё появляется, если новый цикл снова начнёт расширять поверхность вместо удержания contract-line.

Это сигнал к модульной декомпозиции, а не доказательство, что сама модель ошибочна.

## 3. Сравнение с внешними системами

Этот дистрибутивный снимок сохраняет тот же набор внешних ориентиров, что и каноническая дорожная карта задачи `TASK-2026-0008`.
Вывод общий для всего списка: ни один источник не является кандидатом на `full fork`, но каждый даёт ограниченные идеи для заимствования.

### `GitHub Spec Kit`

- Источники:
  <https://github.com/github/spec-kit>,
  <https://github.github.com/spec-kit/index.html>
- Что даёт:
  дисциплину `spec -> plan -> tasks -> implement` и исполняемые спецификации.
- Что брать:
  specification layer и фазность перехода от постановки к реализации.
- Почему не форк:
  это feature-spec workflow, а не repo-local task operating model с registry, task lifecycle и managed upgrade.

### `Claude Code`

- Источники:
  <https://docs.anthropic.com/en/docs/claude-code/memory>,
  <https://docs.anthropic.com/en/docs/claude-code/sub-agents>
- Что даёт:
  layered memory, project instructions и изолированные subagents.
- Что брать:
  идеи scoped memory и формальный контракт субагентов.
- Почему не форк:
  это agent runtime и prompt/memory model, а не дистрибутив knowledge-системы задач.

### `Cursor`

- Источники:
  <https://docs.cursor.com/en/context/rules>,
  <https://docs.cursor.com/en/context/memories>
- Что даёт:
  scoped rules, project memory и совместимость с `AGENTS.md`.
- Что брать:
  совместимость с project rules и предупреждения о drift-е между слоями инструкций.
- Почему не форк:
  это IDE/context layer без task registry, delivery units и install/upgrade governance.

### `memories.sh`

- Источники:
  <https://memories.sh/>,
  <https://memories.sh/docs>
- Что даёт:
  local-first модель памяти и разделение памяти на типы.
- Что брать:
  дорожки памяти: `session`, `semantic`, `episodic`, `procedural`.
- Почему не форк:
  это система памяти, а не система ведения задач с `task.md / plan.md / sdd.md / registry.md`.

### Память GitHub Copilot / VS Code

- Источники:
  <https://code.visualstudio.com/docs/copilot/agents/memory>,
  <https://docs.github.com/en/copilot/how-tos/use-copilot-agents/copilot-memory>
- Что даёт:
  области памяти и привязка памяти к контексту.
- Что брать:
  явные области памяти и memory с подтверждёнными источниками.
- Почему не форк:
  память, контролируемая вендором, не заменяет git-tracked и человекочитаемый workflow знаний.

### База знаний Devin

- Источник:
  <https://docs.devin.ai/product-guides/knowledge>
- Что даёт:
  onboarding на уровне репозитория и извлечение знаний по триггерам.
- Что брать:
  явные триггеры извлечения знаний и различение знаний репозитория и знаний задачи.
- Почему не форк:
  это knowledge overlay, а не операционная модель задачи внутри репозитория.

### `OpenHands`

- Источники:
  <https://docs.openhands.dev/sdk/guides/task-tool-set>,
  <https://docs.all-hands.dev/usage/prompting/microagents-overview>,
  <https://docs.all-hands.dev/openhands/usage/microagents/microagents-repo>
- Что даёт:
  repository customization, microagents и возобновляемые подзадачи.
- Что брать:
  machine-executable subtask flow и packaging микроправил.
- Почему не форк:
  это слой orchestration/tooling, а не task-centric knowledge-дистрибутив со своими managed assets.

### `LangChain Deep Agents`

- Источники:
  <https://docs.langchain.com/oss/python/deepagents/index>,
  <https://docs.langchain.com/oss/python/deepagents/long-term-memory>,
  <https://docs.langchain.com/oss/python/deepagents/human-in-the-loop>
- Что даёт:
  planning, subagents, filesystem-backed memory и разделение между memory, skills, HITL и backend policies.
- Что брать:
  backend/policy separation и дисциплину writable/read-only memory.
- Почему не форк:
  это agent harness, а не готовый repo-local task workflow-дистрибутив.

### Агентные workflows GitHub

- Источники:
  <https://github.github.com/gh-aw/>,
  <https://github.github.com/gh-aw/reference/memory/>,
  <https://github.github.com/gh-aw/introduction/how-they-work/>
- Что даёт:
  память в git, мышление через package/version/lock и воспроизводимость.
- Что брать:
  package-слой, lock/governance и воспроизводимость для зависимостей skill-а и адаптеров.
- Почему не форк:
  это GitHub Actions-oriented execution framework, а не repo-local task operating model.

## 4. Решение по стратегии

### Итоговое решение

Дистрибутивный снимок фиксирует тот же пакет стратегического решения, что и task-local roadmap:

- `continue own path`
- `borrow ideas`
- `do not fork`
- `do not rewrite now`
- `redesign ядра без full rewrite`
- `own core + modular evolution`

Практический смысл этого пакета:

- не продолжать рост монолита без структурных изменений;
- не замораживать skill ради полного rewrite;
- не искать один внешний продукт для `full fork`;
- развивать собственное ядро и выносить memory/reporting/publish/governance в отдельные слои.

### Что заимствуется сейчас и что остаётся отложенным

Обязательно сейчас:

- фазность `spec -> plan -> tasks -> implement` из `GitHub Spec Kit`;
- совместимость с project rules и контроль drift между слоями инструкций из `Cursor`;
- правило, что память и `read-model` не подменяют `task.md`, по образцу memory-систем с явными областями контекста.

Откладывается:

- memory lanes, scoped memory и subagent contracts;
- machine-executable subtask flow и packaging микроправил;
- package/lock governance и расширенная adapter-surface модель.

### Формула продукта на следующую волну

`task-centric-knowledge` должен стать не “набором всех полезных правил для агентов”, а продуктом с жёсткой формулой:

- хранит канонический контекст задачи в локальной knowledge-системе репозитория;
- заставляет агента корректно выбирать `текущая задача / подзадача / новая задача`;
- задаёт минимально достаточный git/publish жизненный цикл;
- умеет устанавливаться и обновляться без потери project data;
- расширяется через адаптеры и профили, а не через бесконечное разрастание ядра.

## 5. Целевая конечная точка

Конечная цель следующего большого цикла:

создать `task-centric-knowledge vNext`, где ядро стабильно, helper-механика модульна, а publish- и domain-specific поведение подключается как отдельные расширения.

### Признаки достижения цели

- модель ядра умещается в короткий набор канонических документов без противоречий;
- `task_workflow` разделён по зонам ответственности;
- локальный режим без remote считается полноценным сценарием, а не деградированным fallback;
- GitHub/GitLab-специфика не просачивается в ядро задачи;
- install/check/upgrade/doctor образуют предсказуемый диагностируемый контур;
- новый профиль или новый host adapter добавляется без переписывания половины skill-а.

## 6. Дорожная карта по фазам

Фазы 1-4 уже закрыты задачами `TASK-2026-0010 ... TASK-2026-0014`.
Раздел ниже сохраняется как историческая карта того,
как был собран `vNext`,
и как повторно открывать похожие tracks без потери архитектурной дисциплины.

### Фаза 0. Ворота стабилизации

Результат:

- внешний GitHub smoke для `TASK-2026-0007` закрыт;
- GitLab остаётся отложенной областью и не тянется в ядро;
- собран список нормативных источников и дубликатов;
- собран минимальный список операторских CLI-ожиданий и обязательных полей вывода.

Ворота перехода:

- publish-flow подтверждён минимальным внешним smoke;
- нет крупных расхождений между описанием skill-а и фактическими возможностями.

Что подготавливает дальше:

- открывает короткий вход в `vNext-core`, не споря заново о publish-flow и исходном scope skill-а.

### Фаза 1. Заморозка контракта ядра

Результат:

- создан короткий `vNext-core` / `core-model.md`;
- определены канонические сущности, переходы состояний и границы владения;
- зафиксированы ограниченные контексты и корень агрегата `Task`;
- закреплено, что `task.md` владеет сводкой задачи, а `registry.md` остаётся навигационным кэшем;
- закреплено, что доказательные артефакты живут внутри каталога задачи или явно ссылаются из него;
- всё host-specific, профильное и связанное с read-моделью живёт вне ядра.

Ворота перехода:

- любое ключевое правило трассируется в один первичный источник;
- skill можно объяснить одной картой контекстов без скрытых special-cases.

Что подготавливает дальше:

- делает возможным отдельный track на `vNext-core contract` и безопасную декомпозицию helper-а без повторного архитектурного спора.

### Фаза 2. Внутренняя модульная декомпозиция

Результат:

- `task-knowledge workflow` использует модульный runtime;
- выделены `domain model`, `markdown io`, `registry sync`, `git ops`, `publish flow`, `forge adapters`, `cli`;
- появляется read-модель для `status`, `current-task` и `task show`;
- unit-тесты привязаны к модулям, а не только к одному большому сценарию.

Ворота перехода:

- доменная логика тестируется отдельно от текстовых снимков;
- новая функциональность не требует каждый раз менять один helper-монолит.

Что подготавливает дальше:

- открывает отдельные tracks на `doctor / cleanup governance` и `read model / reporting`.

### Фаза 3. Слои расширения

Результат:

- появляется отдельная модель памяти;
- оформлены adapter surfaces;
- publish-адаптеры развиваются независимо от модели задачи;
- профильные надстройки не меняют семантику ядра.

Ворота перехода:

- память и host-интеграции добавляются без роста центрального монолита;
- новая возможность подключается как слой, а не как special-case внутри ядра.

Что подготавливает дальше:

- позволяет отдельно решать, когда действительно нужен memory-layer, а когда достаточно `core + publish + reporting`.

### Фаза 4. Упаковка, обновление и внедрение

Результат:

- формализованы правила совместимости и история обновления;
- `doctor deps` и `migrate cleanup plan/confirm` становятся стандартным install/upgrade UX;
- есть migration notes, reference repo patterns и несколько эталонных задач;
- quickstart и adoption package проверены на внешних репозиториях.

Ворота перехода:

- путь обновления воспроизводим и проверяем;
- оператор получает понятные ответы на `status` и `current-task`;
- cleanup после миграции остаётся подтверждаемым.

## 7. Ворота остановки и переосмысления

Ниже критерии, при которых нужно не просто “допилить”, а остановиться и пересмотреть архитектуру.

### Стоп-ворота 1

Если после Этапа 1 не удаётся коротко и непротиворечиво определить контракт ядра, значит skill реально смешивает несколько продуктов и нуждается в разделении.

### Стоп-ворота 2

Если после Этапа 2 новые изменения по-прежнему требуют массовых правок в одном helper-монолите, нужно выделять отдельную границу package/module, а не продолжать локальный рефакторинг.

### Стоп-ворота 3

Если publish-host кейсы снова и снова протаскивают новые исключения в ядро, publish-flow нужно выносить ещё дальше от ядра, вплоть до отдельного companion layer.

### Стоп-ворота 4

Если следующая волна снова требует добавлять capability прямо в текущий helper-монолит, roadmap нужно пересмотреть до старта реализации.

### Стоп-ворота 5

Если в реальных репозиториях пользователям чаще нужен feature-spec workflow, чем task-centric жизненный цикл, надо не распухать дальше, а честно разделить продукт на `task-centric core` и `spec-driven companion`.

## 8. Обновление: стабильный релиз — 2026-05-13

### Все vNext-треки и post-release задачи закрыты

После завершения фаз 1-4 и post-release цикла `TASK-2026-0021 ... TASK-2026-0049`
проект вошёл в стабильное состояние. Ниже traceability закрытых контуров:

| Контур | Задачи | Что достигнуто |
|--------|--------|---------------|
| vNext core | `0010`–`0014` | Task Core, DDD-карта, модульная декомпозиция, `doctor`/`governance`, `read-model`, полевая валидация |
| v1 release | `0021`, `0026`, `0030`–`0034` | Standalone bootstrap, productization, repo-wide review-fix до clean verdict |
| Заимствованный `module core` | `0024` | Module passports, registry, dependency map, `file-local` contracts, verification catalog, module query |
| Upgrade governance | `0025`, `0034`, `0037`, `0038`, `0040` | Безопасное обновление, `compatibility-backfill`, глобальная и проектная установка |
| Нативный runtime | `0027`, `0028`, `0035`, `0036` | Local auto-finalize, CLI compat, consumer surfaces, `zip-context` ignore |
| Package и CLI | `0041`, `0042`, `0043` | Удаление legacy-фасадов, unified CLI, нормализация `src/task_knowledge/`, `bootstrap`-формализация |
| Publish | `0044` | `GitHubAPIAdapter` + `GitLabAPIAdapter` через HTTPS REST API без `gh`/`glab` |
| Документация | `0045`, `0048`, `0049` | Миграция Doxygen → MkDocs, разделение `README`/`CLI-reference`, `docs/index.md` |
| Интеграции | `0039`, `0046`, `0047` | Production-team snapshot, `mass-update` automation, `semantic-algorithm-design` reference |

### Текущая точка как стабильный релиз

- Полный набор: **290 тестов**, все зелены.
- Рабочее дерево чистое, все ветки слиты в `main`.
- **37 задач** в `knowledge/tasks/registry.md` — все со статусом `завершена`.
- Документация: `README.md` (обзор), `references/cli-reference.md` (CLI), `references/core-model.md` (ядро), `references/roadmap.md` (стратегия), `docs/index.md` (API).
- CLI: 9 подкоманд (`doctor`, `install`, `task`, `module`, `file`, `workflow`, `borrowings`, `bootstrap`, `--help`).
- Publish: CLI-адаптеры (`gh`/`glab`) + HTTP-адаптеры (`GITHUB_TOKEN`/`GITLAB_TOKEN`).

### Что осталось вне scope v1

Перечисленное ниже не входит в текущий стабильный контур и является кандидатами на следующий стратегический цикл:

- **Memory layer**: дорожки памяти `session`/`semantic`/`episodic`/`procedural`, scoped memory, subagent contracts — идеи заимствованы из `Claude Code`, `memories.sh`, `LangChain Deep Agents`, но удерживаются вне ядра до отдельного strategy track.
- **Расширенные adapter surfaces**: Bitbucket, Gitea, self-hosted forge; OAuth flow.
- **Machine-executable subtask flow**: упаковка микроправил и автономные подзадачи по образцу `OpenHands`.
- **Package/lock governance**: версионирование зависимостей skill-а по образцу `GitHub Agent Workflows`.
- **Внешний docs hosting**: CI pipeline для публикации MkDocs-сайта.
- **Параллельное обновление проектов**: в `mass-update` v1 обновление последовательное.

## 9. Следующий стратегический цикл: candidate delivery-tracks

### Track 6. Memory layer (кандидат)

Назначение: добавить управляемый memory-layer поверх `Task Core` с дорожками:
- `session` — контекст текущей сессии;
- `procedural` — правила, инварианты, контракты (уже частично покрыто `AGENTS.md` и `references/`);
- `semantic` — факты, решения, инсайты по задаче;
- `episodic` — история действий и хронология.

Граница: memory layer остаётся производным и не подменяет `task.md` как источник истины.

### Track 7. Subagent contract (кандидат)

Назначение: формальный контракт для параллельных субагентов — изолированные контексты задач, скоупы файлов, протокол обмена результатами и агрегации.

### Track 8. Расширенные adapter surfaces (кандидат)

Назначение: Bitbucket, Gitea, self-hosted forge; OAuth flow; multi-remote publish.

### Track 9. Внешний docs hosting (кандидат)

Назначение: CI pipeline для автоматической сборки и публикации MkDocs-сайта на GitHub Pages или аналог.

### Чего по-прежнему не делать

- Не расширять ядро (Task Core) без отдельного strategy track и утверждённого contract.
- Не превращать skill в universal agent platform.
- Не добавлять host-specific логику в модель задачи.
- Не форкаться от внешней системы целиком.

## 10. Краткая рекомендация владельцу skill-а

Текущая версия `task-centric-knowledge` (0.1.0, стабильный релиз 2026-05-13) прошла полный цикл:
проектирование → модульная декомпозиция → governance → `read-model` → полевая валидация →
productization → review-fix → publish-адаптеры → документация → CI-готовность.

Самая сильная линия следующего цикла:
- **не расширять модель вширь**;
- **добавить memory-layer** как точечное усиление agent-driven разработки;
- **формализовать subagent contract** для параллельной работы;
- считать успехом снижение неоднозначности и стоимости сопровождения, а не количество новых правил.
