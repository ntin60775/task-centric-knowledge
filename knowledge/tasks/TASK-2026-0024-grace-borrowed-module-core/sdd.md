# SDD по задаче TASK-2026-0024

## Когда использовать

`sdd.md` обязателен только для сложных задач.
Если для задачи достаточно `task.md` и `plan.md`, этот файл можно не создавать.
Если `sdd.md` создан, рядом с ним по умолчанию нужно вести и `artifacts/verification-matrix.md`.

## Паспорт SDD

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0024` |
| Статус | `завершено` |
| Версия | `1` |
| Дата обновления | `2026-04-21` |

## 0. Инварианты и verification matrix

Для сложной задачи это обязательный раздел.
Агент должен до ревью зафиксировать полный invariant set и доказать его покрытие, а не полагаться на то, что внешнее ревью само найдёт недостающие сценарии.

### Полный invariant set

- `INV-01`: `Module Core` остаётся companion-layer к `Task Core` и не получает права подменять `task.md`, `registry.md`, статусы задач и publish lifecycle.
- `INV-02`: borrowed-layer из GRACE обновляется только через local-first `Pin + Local` механизм с `origin_url`, `pinned_revision`, `local_checkout_override` и явным `plan -> apply`.
- `INV-03`: новая product surface ограничена шестью capability-tracks и не разворачивается в full GRACE-подобный framework.
- `INV-04`: module-level query и verification добавляются как read-only инженерный слой и не меняют task-routing / task-query поведение.
- `INV-05`: file-local contracts и semantic anchors применяются только к governed hot spots и не становятся repo-wide обязательной разметкой.
- `INV-06`: весь `Module Core` остаётся language-agnostic и не зависит от одного семейства языков, AST или import-модели; поддержка `1С/BSL` является обязательной, а не факультативной.
- `INV-07`: versioned upgrade старых версий и legacy task backfill описаны явно; закрытые задачи получают только compatibility-backfill и migration-note, без переписывания их исторического narrative.
- `INV-08`: execution-контур `Module Core` строится как `main orchestrator + parallel read-only scouts + single sequential writer + read-only verifier`; одновременно допускается только один writer-subagent.
- `INV-09`: главный агент владеет task-truth, постановкой, readiness gate, выдачей execution packet, приёмкой и интеграцией; writer-subagent не меняет `task.md`, `plan.md`, `sdd.md`, `registry.md` и shared governance-истину.
- `INV-10`: writer-subagent может менять только явно выданный write-scope: код, конфиги, тесты и обычные repo-docs в границах packet-а; расширение scope возвращается контроллеру как blocker.
- `INV-11`: module verification catalog дополнительно даёт `ExecutionReadiness`, `VerificationExcerpt` и `FailureHandoff`, чтобы write-pass не стартовал без проверяемых критериев и evidence.
- `INV-12`: shared/public truth читается через module passports и `module show`, а file-local/private truth читается через governed file contracts и `file show`; private helper churn не переносится в shared module record.
- `INV-13`: execution/readiness rollout для legacy задач не создаёт ложный active target и не меняет historical branch/date/history.

### Связанные артефакты проверки

- `artifacts/verification-matrix.md` — матрица `инвариант -> сценарий нарушения -> проверка/команда -> статус покрытия`.
- Если для части инвариантов допустим только ручной сценарий, это нужно явно отметить и затем поднять в единый итоговый checklist общей задачи.

### Единый execution-концепт

`Module Core` должен поддерживать управляемое делегирование правок,
но не превращаться в самостоятельную multi-agent платформу.
Целевая модель:

- главный агент является `main orchestrator`, владельцем task-truth и единственным собеседником пользователя по смыслу задачи;
- read-only scouts могут параллельно исследовать код, docs, module passports, file-local contracts, logs и verification evidence;
- ровно один writer-subagent за раз получает `ExecutionPacket` и выполняет последовательный write-pass;
- read-only verifier сверяет результат с packet, module verification и task-local criteria;
- главный агент принимает или отклоняет результат и сам обновляет task-local truth.

Из GRACE заимствуются идеи `execution packet`, `failure handoff`,
синхронизации под управлением контроллера, общей публичной истины,
локальной файловой истины и переиспользуемых verification evidence.
Не заимствуются full XML platform, multiwriter waves,
repo-wide mandatory semantic markup и право workers менять shared planning artifacts.

## 1. Проблема и цель

### Проблема

После закрытия `TASK-2026-0021` у продукта есть чёткая standalone-формула,
но нет отдельного execution track для точечных module-centric заимствований из GRACE.
Старые артефакты фиксируют саму идею `adapter-to-grace`,
однако не разлагают её на implementable capability-track
и уже содержат устаревшую ссылку на прежний абсолютный путь upstream checkout.

### Цель

Открыть отдельный task-local рабочий трек,
в котором:

- сохраняется продуктовая граница `standalone + adapter as reserve`;
- появляется formal backlog на шесть связанных deliverables `Module Core`;
- первый deliverable сразу закрепляет устойчивый refresh-механизм borrowed-layer;
- все следующие deliverables можно детализировать и реализовывать независимо;
- вся новая surface проектируется так, чтобы быть применимой к репозиториям на разных языках, включая `1С/BSL`;
- для старых версий и старых задач появляется versioned migration policy без реткона уже завершённых задач.
- появляется repo-native execution-layer:
  `ExecutionPacket`, `ResultPacket`, `FailureHandoff` и `ExecutionReadiness`,
  которые дают главный контролируемый путь от module knowledge к одному последовательному writer-pass.

## 2. Архитектура и границы

- существующий `Task Core` остаётся ядром продукта;
- поверх него вводится новый companion-context `Module Core` для инженерной навигации по модулям и управляемым файлам;
- borrowed-layer опирается на GRACE как внешний источник идей и референсных артефактов, но не копирует его продуктовую роль целиком;
- future implementation должна использовать `knowledge/modules/` как managed-root модульной памяти и read-only query слой в `task-knowledge`;
- refresh borrowed-layer строится как one-way pull из pinned upstream snapshot в локальный companion-layer.
- execution-layer строится как handoff под владением контроллера:
  главный агент собирает module/file/verification context,
  выпускает packet только после readiness gate,
  принимает result/failure packet и сам интегрирует task-local выводы.
- все сущности `Module Core` описываются через language-neutral поля:
  путь, owned surface, contract markers, управляемые файлы, verification evidence и relation excerpts;
  они не требуют обязательного AST, package manager или import graph.
- upgrade-path использует уже существующий install/upgrade governance `Task Core`,
  а legacy backfill отделяется от managed refresh и от borrowed refresh.

### Допустимые и недопустимые связи

- допустимо: `Task Core` ссылается на `Module Core` как на companion-layer для инженерной детализации;
- допустимо: `Module Core` переиспользует task-local verification artifacts и будущие module passports;
- допустимо: borrowed-layer читает upstream GRACE checkout и строит локальный `refresh-plan`;
- допустимо: синхронизировать старые задачи по compatibility-метаданным и добавлять migration-note, если это не меняет смысл завершённой задачи;
- допустимо: доводить активные задачи до новых правил глубже, если они всё ещё находятся в рабочем жизненном цикле;
- недопустимо: `Module Core` становится новым источником истины по состоянию задачи;
- недопустимо: borrowed refresh silently меняет managed assets без preview и explicit apply;
- недопустимо: новая capability-сетка уводит продукт в mandatory XML/semantic markup framework на всём репозитории.
- недопустимо: любая capability требует language-specific parser или поддерживает только Python/TypeScript-style модульность;
- недопустимо: `1С/BSL` объявляется special-case вне общего контракта вместо полноценного supported языка.
- недопустимо: автоматически переписывать narrative, SDD и verification уже завершённых задач так, как будто новая версия существовала в прошлом.
- недопустимо: запускать несколько writer-subagent одновременно или разрешать writer-у менять task-truth и shared governance-документы;
- недопустимо: выдавать writer-pass без `ExecutionReadiness=ready`, точного write-scope, verification excerpt и stop conditions;
- недопустимо: превращать file-local/private truth в обязательную repo-wide разметку или зеркалировать private helper churn в module passport.

### Новые зависимости и их обоснование

- `нет`

### Наблюдаемые сигналы и диагностические маркеры

- `task_query status` должен показывать новую задачу и зарегистрированные подзадачи без новых warning-типов кроме уже существующих repo-level;
- старый путь `/home/prog7/MyWorkspace/30-Knowledge/AI/grace-marketplace/` отсутствует;
- актуальный checkout обнаружен по пути `/home/prog7/РабочееПространство/work/AI/git-update-only/grace-marketplace/`;
- product-thesis `TASK-2026-0021` прямо запрещает trajectory `свой собственный GRACE`.
- пользователь явно ожидает универсальный `Module Core`, применимый и к `1С/BSL`-репозиториям.
- пользователь ожидает, что новая версия будет включать upgrade-процесс со старых версий и policy по обновлению старых задач.

## 3. Изменения данных / схемы / metadata

- создаётся новая task-local запись `TASK-2026-0024`;
- создаются семь task-local подзадач `TASK-2026-0024.1 ... TASK-2026-0024.7`;
- в будущей реализации ожидаются новые metadata-сущности:
  - `knowledge/modules/registry.md`
  - `knowledge/modules/_templates/module.md`
  - `skills-global/task-centric-knowledge/borrowings/grace/source.json`
  - `skills-global/task-centric-knowledge/borrowings/grace/README.md`
  - `ExecutionPacket`
  - `ResultPacket`
  - `FailureHandoff`
  - `ExecutionReadiness`
  - правила versioned upgrade и legacy classification / backfill policy в `references/upgrade-transition.md`, `references/deployment.md`, `SKILL.md` и task-local migration notes

## 4. Новые сущности и интерфейсы

- верхнеуровневая task-сущность `TASK-2026-0024` как product track `Module Core`;
- подзадача `TASK-2026-0024.1` как обязательный source/refresh-governance слой;
- подзадачи `TASK-2026-0024.2 ... TASK-2026-0024.6` как capability-tracks;
- подзадача `TASK-2026-0024.7` как governance-слой versioned upgrade и legacy task backfill;
- будущие read-only CLI-команды:
  - `task-knowledge module find`
  - `task-knowledge module show`
  - `task-knowledge file show`
  - `task-knowledge borrowings status`
  - `task-knowledge borrowings refresh-plan`
  - `task-knowledge borrowings refresh-apply`

### Репозиторно-нативный packet vocabulary

`ExecutionPacket`:

- `task_id`
- `module_id`
- `purpose`
- `write_scope`
- `allowed_file_classes`
- `contract_excerpt`
- `dependency_summaries`
- `verification_excerpt`
- `allowed_checks`
- `stop_conditions`
- `forbidden_expansion`
- `expected_followups`

`ResultPacket`:

- `module_id`
- `changed_files`
- `executed_checks`
- `residual_risks`
- `assumptions`
- `needs_controller_decision`

`FailureHandoff`:

- `contract_ref`
- `scenario`
- `expected_evidence`
- `observed_evidence`
- `first_divergent_anchor`
- `suggested_next_action`

`ExecutionReadiness`:

- `status: ready|blocked|partial`
- `blocking_reasons`
- `required_verification_refs`
- `required_governed_files`
- `residual_manual_risk`

Эти сущности являются vocabulary для controller-guided execution.
Они не становятся отдельным source-of-truth поверх `Task Core`.

## 5. Изменения в существующих компонентах

- `knowledge/tasks/registry.md`
  - добавить строки для новой задачи и шести значимых подзадач;
  - сохранить branch-aware синхронизацию и task-centric summary.
- `knowledge/tasks/TASK-2026-0024-grace-borrowed-module-core/*`
  - создать task-local пакет новой задачи: карточка, план, SDD, verification matrix.
- `knowledge/tasks/TASK-2026-0024-grace-borrowed-module-core/subtasks/*`
  - создать шесть подзадач с общим контекстом и конкретной ролью в `Module Core`.
- downstream после task-local спецификации:
  - `SKILL.md` и README фиксируют `Module Core` как controller-guided single-writer companion-layer;
  - `references/core-model.md` фиксирует разделение `task-truth owner` и `writer-owned implementation scope`;
  - `references/roadmap.md` переводит узкий orchestration-contract из отложенных идей в scope `Module Core`, не открывая full subagent platform;
  - `references/upgrade-transition.md` и `references/deployment.md` получают rollout/backfill policy для readiness/packet модели.

## 6. Этапы реализации и проверки

### Этап 1: Открытие рабочего трека

- создать верхнеуровневую задачу и branch-aware контур;
- зафиксировать boundary с `TASK-2026-0021` и `TASK-2026-0008`;
- Verify: `task_query status`, `task_query current-task`, helper sync и `git diff --check`;
- Аудит: `SDD_AUDIT`

### Этап 2: Декомпозиция capability-tracks

- завести одну cross-cutting подзадачу для source/refresh governance;
- завести одну governance-подзадачу для versioned upgrade и legacy task backfill;
- завести пять capability-подзадач под borrowed module-centric surface;
- Verify: task-local проверка наличия карточек и plan-файлов, registry sync;
- Аудит: `IMPLEMENTATION_AUDIT`

### Этап 3: Execution-ready foundation

- детализировать `TASK-2026-0024.5` как module verification catalog,
  гейт готовности,
  выдержку верификации
  и `FailureHandoff`;
- затем детализировать `TASK-2026-0024.6` как read-only query layer,
  который собирает shared/public и file-local/private truth в execution context;
- Verify: task-local документы содержат единый verification/query контур,
  через который writer-pass не стартует вслепую;
- Аудит: `EXECUTION_CONTRACT_AUDIT`

### Этап 4: Upgrade и историчность

- определить policy `closed historical / active / reference` для старых задач;
- определить, какие поля и артефакты разрешены к compatibility-backfill автоматически, а какие требуют отдельного ручного решения;
- детализировать `TASK-2026-0024.7` как rollout/backfill governance,
  уже опирающийся на конкретные поля готовности,
  выдержки верификации
  и query excerpts;
- Verify: task-local документы явно разводят compatibility-backfill и narrative rewrite;
- Аудит: `MIGRATION_AUDIT`

### Этап 5: Отложенный structural backlog

- вернуться к `TASK-2026-0024.2` и определить managed-root `knowledge/modules/`
  только после фиксации execution/governance foundation;
- затем поднять `TASK-2026-0024.3`,
  чтобы dependency map опиралась на уже согласованный passport/query контур;
- затем поднять `TASK-2026-0024.4`,
  чтобы file-local contracts и anchors не замораживались раньше,
  чем понятны readiness/query потребители этих маркеров;
- Verify: task-local документы явно отделяют текущую приоритетную цепочку от отложенного structural backlog;
- Аудит: `BACKLOG_PRIORITY_AUDIT`

### Финальный этап: Интеграция backlog

- согласовать созданный backlog с продуктовой границей standalone-линии;
- зафиксировать next-step в `TASK-2026-0024` как приоритетную цепочку
  от `TASK-2026-0024.1` к `TASK-2026-0024.5`,
  затем к `TASK-2026-0024.6`,
  затем к `TASK-2026-0024.7`
  с отложенным возвратом к `TASK-2026-0024.2`, `TASK-2026-0024.3` и `TASK-2026-0024.4`;
- Verify: localization guard по новым Markdown-файлам, `git diff --check`, сверка инвариантов из `artifacts/verification-matrix.md`;
- Аудит: `INTEGRATION_AUDIT`

## 7. Критерии приёмки

1. Создана самостоятельная верхнеуровневая задача `TASK-2026-0024` с branch-aware контуром.
2. Созданы и зарегистрированы семь подзадач, покрывающих весь agreed scope borrowed `Module Core`.
3. В task-local документах явно зафиксирован механизм `Pin + Local` для borrowed refresh.
4. Новая задача не спорит с boundary `standalone / adapter / pivot`, принятой в `TASK-2026-0021`.
5. Versioned upgrade и policy legacy task backfill описаны без подмены исторических задач.
6. Execution/governance-цепочка прошла через `TASK-2026-0024.5`,
   затем `TASK-2026-0024.6`,
   затем `TASK-2026-0024.7`,
   а structural backlog `TASK-2026-0024.2`, `TASK-2026-0024.3` и `TASK-2026-0024.4`
   реализован и закрыт до финального закрытия верхнеуровневой задачи.
7. Все новые контракты и planned capabilities остаются language-agnostic и применимы к `1С/BSL` без отдельной ветки продукта.
8. Execution-layer описан как controller-guided single-writer model без parallel writers и без права writer-а менять task-truth.

## 8. Стоп-критерии

1. Если новая задача требует уже на старте полной XML/semantic-markup surface уровня GRACE, работу нужно остановить и пересмотреть продуктовую границу.
2. Если borrowed refresh нельзя описать без жёсткой привязки к одному локальному абсолютному пути, задачу нельзя считать корректно открытой.
3. Если capability-подзадачи не удаётся развести по scope и они снова схлопываются в один «большой adapter-track», декомпозицию нужно перепроектировать.
4. Если любой planned capability нельзя сформулировать без language-specific assumptions и без реальной применимости к `1С/BSL`, постановка задачи считается неполной.
5. Если migration policy для старых задач требует реткона закрытых артефактов вместо compatibility-backfill, постановка задачи считается неверной.
6. Если execution-layer требует нескольких writer-subagent одновременно или отдаёт writer-у `task.md` / `registry.md` / SDD ownership, постановка задачи считается неверной.
7. Если readiness gate нельзя доказать через module verification и query excerpts, writer-pass должен блокироваться до усиления verification.

## Связь с остальными файлами задачи

- `task.md` остаётся источником истины по статусу, границам и итоговому состоянию задачи;
- итоговый список ручных проверок общей задачи хранится в `task.md`, а не дублируется в нескольких документах;
- `plan.md` хранит только исполнимый план и ссылки на этапы SDD, без дублирования всей спецификации;
- `artifacts/verification-matrix.md` хранит доказательную связку `инвариант -> сценарий -> проверка -> статус покрытия`;
- `worklog.md` фиксирует прохождение этапов SDD, проверки и аудиты;
- `decisions.md` фиксирует любые осознанные отклонения от SDD.
