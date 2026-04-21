# SDD по задаче TASK-2026-0010

## Паспорт SDD

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0010` |
| Статус | `завершено` |
| Версия | `2` |
| Дата обновления | `2026-04-13` |

## 0. Инварианты и verification matrix

### Полный invariant set

- `INV-0010-01`: существует один и только один канонический нормативный документ `Task Core` в виде `artifacts/vnext-core-contract.md`;
- `INV-0010-02`: полный агрегат `Task Core` перечисляет `Task`, `Subtask`, `Delivery Unit`, `Verification Matrix`, `Task Artifact`, `Decision`, `Worklog Entry`, `Handoff`;
- `INV-0010-03`: `task.md` остаётся источником истины по summary, status, branch и delivery units, а `registry.md` — только производным cache;
- `INV-0010-04`: каноническая task summary всегда строится из `TASK-ID`, `Краткого имени` и `Человекочитаемого описания`;
- `INV-0010-05`: производные контексты `Read Model / Reporting`, `Publish Integration`, `Memory`, `Packaging / Governance`, `Profiles` не получают права менять `Task Core` в обход канонических правил;
- `INV-0010-06`: статусная модель задач и delivery units зафиксирована как допустимый набор состояний и переходов;
- `INV-0010-07`: evidence хранится внутри task-local `artifacts/` или явно ссылается из него;
- `INV-0010-08`: cleanup-governance наследует `plan -> confirm` и не удаляет `project data` молча;
- `INV-0010-09`: skill-level snapshot и managed-шаблоны повторяют те же core-инварианты, что и task-local contract.

### Связанные артефакты проверки

- `artifacts/vnext-core-contract.md`
- `artifacts/verification-matrix.md`
- `skills-global/task-centric-knowledge/SKILL.md`
- `skills-global/task-centric-knowledge/references/roadmap.md`

## 1. Проблема и цель

### Проблема

После `TASK-2026-0008` стратегическая форма `vNext` уже выбрана,
но первичный нормативный слой ядра ещё не был оформлен как отдельный короткий contract.
Из-за этого следующий execution-цикл рисковал снова смешать стратегию, runtime-реализацию,
read-model, governance и memory-слои, а также оставить drift между task-local документами,
skill-level snapshot и managed-шаблонами.

### Цель

Сформировать один короткий `vNext-core contract`, который однозначно описывает:

- полный агрегат `Task Core`;
- источник истины и ownership boundaries;
- каноническую task summary;
- допустимые переходы состояний задач и delivery units;
- локальное хранение evidence;
- базовый cleanup-governance;
- запрет на обход ядра со стороны производных слоёв.

## 2. Архитектура и границы

`Task Core` рассматривается как основной ограниченный контекст.
Производные контексты `Read Model / Reporting`, `Publish Integration`, `Memory`, `Packaging / Governance`, `Profiles`
могут расширять ядро, но не переопределяют его состояние, summary и смысл.

В рамках задачи фиксируются:

- корень агрегата `Task`;
- полный состав task-local сущностей и объектов-значений;
- ownership по `task.md`, `plan.md`, `sdd.md`, `artifacts/`, `worklog.md`, `decisions.md`, `handoff.md`;
- статусная модель задач и delivery units;
- базовые ограничения evidence / cleanup governance.

### Допустимые и недопустимые связи

- допустимо: `task.md` владеет summary, status и delivery units;
- допустимо: `plan.md`, `sdd.md` и `artifacts/verification-matrix.md` являются производными, но обязательными task-local носителями;
- допустимо: `registry.md`, read-model и skill-level snapshot читают task-local source-of-truth;
- недопустимо: `registry.md`, read-model, publish-adapter, memory-layer или profile-layer переопределяют summary, статус или ownership задачи;
- недопустимо: `Packaging / Governance` обходит `plan -> confirm` или молча удаляет `project data`;
- недопустимо: эта задача выбирает file-level modularization helper-а, transport layer CLI или host parity.

### Новые зависимости и их обоснование

- `нет`

### Наблюдаемые сигналы и диагностические маркеры

- `не требуется`

## 3. Изменения данных / схемы / metadata

- добавляется новый канонический документ `artifacts/vnext-core-contract.md`;
- обновляется task-local metadata задачи `TASK-2026-0010`;
- обновляются skill-level и managed Markdown-носители, повторяющие core contract;
- runtime-данные и схемы Python helper-а не меняются.

## 4. Новые сущности и интерфейсы

### Новый нормативный интерфейс

| Сущность / интерфейс | Формат | Назначение |
|----------------------|--------|------------|
| `artifacts/vnext-core-contract.md` | Markdown-документ | Канонический нормативный источник по `Task Core` |
| `Task Core aggregate` | DDD-карта и таблицы ownership внутри contract | Полный состав task-local сущностей, объектов-значений и границ |
| `Task state model` | Явный набор статусов и допустимых переходов | Нормализует planning-состояния задач |
| `Delivery Unit state model` | Явный набор publish-статусов и переходов | Нормализует publish-контур внутри `task.md` |

### Канонические сущности и объекты-значения

- Сущности: `Task`, `Subtask`, `Delivery Unit`, `Verification Matrix`, `Task Artifact`, `Decision`, `Worklog Entry`, `Handoff`.
- Объекты-значения: `Task ID`, `Task Slug`, `Task Status`, `Branch Ref`, `Publication State`, `Evidence Ref`.

## 5. Изменения в существующих компонентах

- `knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/task.md`
  - карточка задачи переведена в финальное состояние и ссылается на новый канонический contract;
- `knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/plan.md`
  - план приведён к decision-complete форме с точными verify-командами;
- `knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/sdd.md`
  - спецификация детализирована до полного invariant set, этапов и stop-критериев;
- `knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/verification-matrix.md`
  - матрица переведена в coverage-формат с фактическими командами;
- `skills-global/task-centric-knowledge/SKILL.md`
  - skill summary и инварианты синхронизированы с новым core contract;
- `skills-global/task-centric-knowledge/references/roadmap.md`
  - дистрибутивный roadmap теперь явно указывает на канонический core contract Track 1;
- `skills-global/task-centric-knowledge/assets/knowledge/tasks/README.md`
  - методика дополняется явной моделью `Task Core` и разграничением производных слоёв;
- `skills-global/task-centric-knowledge/assets/knowledge/tasks/_templates/task.md`
  - шаблон задачи подсказывает, где фиксировать канонический контракт, если задача меняет его;
- `skills-global/task-centric-knowledge/assets/knowledge/tasks/_templates/plan.md`
  - шаблон плана требует явно назвать канонический контракт, если задача его вводит;
- `skills-global/task-centric-knowledge/assets/knowledge/tasks/_templates/sdd.md`
  - шаблон SDD требует перечислять канонические сущности, переходы состояний и source-of-truth для contract-first задач;
- `skills-global/task-centric-knowledge/assets/knowledge/tasks/_templates/artifacts/verification-matrix.md`
  - шаблон матрицы требует фиксировать ownership и state-machine инварианты для contract-задач;
- `skills-global/task-centric-knowledge/tests/test_install_skill.py`
  - text-regression проверки закрепляют обновлённый vocabulary managed `README.md` и шаблонов.

## 6. Этапы реализации и проверки

### Этап 1: Канонический contract ядра

- создать `artifacts/vnext-core-contract.md`;
- зафиксировать DDD-карту контекстов, полный агрегат, objects of value, source-of-truth и ownership по файлам;
- зафиксировать статусную модель задач и delivery units, а также evidence / cleanup governance;
- Verify: `rg -n "Task Core|Read Model / Reporting|Publish Integration|Memory|Packaging / Governance|Profiles" knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md`
- Verify: `rg -n "Task Artifact|Decision|Worklog Entry|Handoff|Verification Matrix|Delivery Unit" knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md`
- Audit: `CONTRACT_AUDIT`

### Этап 2: Синхронизация производных носителей

- выровнять `task.md`, `plan.md`, `sdd.md` и `artifacts/verification-matrix.md` задачи относительно канонического contract;
- выровнять `SKILL.md`, `references/roadmap.md`, managed `README.md` и task-шаблоны;
- обновить text-regression проверки installer/templates;
- Verify: `rg -n "task.md|registry.md|TASK-ID|Краткое имя|Человекочитаемое описание|plan -> confirm|project data|artifacts/" knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md skills-global/task-centric-knowledge/SKILL.md skills-global/task-centric-knowledge/assets/knowledge/tasks/README.md`
- Verify: `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'`
- Audit: `DISTRIBUTION_AUDIT`

### Финальный этап: Refresh и интеграция

- refresh-нуть managed-файлы текущего репозитория из обновлённых assets;
- прогнать installer check, `git diff --check` и локализационный guard;
- синхронизировать финальный status задачи и строку в `registry.md`;
- Verify: `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main --mode install --force`
- Verify: `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main --mode check`
- Verify: `git diff --check`
- Verify: `scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/task.md knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/plan.md knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/sdd.md knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/verification-matrix.md skills-global/task-centric-knowledge/SKILL.md skills-global/task-centric-knowledge/references/roadmap.md skills-global/task-centric-knowledge/assets/knowledge/tasks/README.md skills-global/task-centric-knowledge/assets/knowledge/tasks/_templates/task.md skills-global/task-centric-knowledge/assets/knowledge/tasks/_templates/plan.md skills-global/task-centric-knowledge/assets/knowledge/tasks/_templates/sdd.md skills-global/task-centric-knowledge/assets/knowledge/tasks/_templates/artifacts/verification-matrix.md knowledge/tasks/README.md knowledge/tasks/_templates/task.md knowledge/tasks/_templates/plan.md knowledge/tasks/_templates/sdd.md knowledge/tasks/_templates/artifacts/verification-matrix.md`
- Audit: `INTEGRATION_AUDIT`

## 7. Критерии приёмки

1. В репозитории существует один канонический документ `artifacts/vnext-core-contract.md`.
2. Полный агрегат `Task Core` и DDD-карта контекстов перечислены без двусмысленности.
3. `task.md` формально закреплён как source-of-truth по summary, status, branch и delivery units.
4. Статусная модель задач и delivery units описана как допустимый набор состояний и переходов.
5. Evidence / cleanup governance подняты до core-инвариантов.
6. `SKILL.md`, `references/roadmap.md`, managed `README.md` и шаблоны не расходятся с task-local contract.
7. Verification matrix покрыта фактически прогнанными командами и тестами.

## 8. Стоп-критерии

1. Contract начинает дублировать стратегическую roadmap вместо короткого нормативного слоя.
2. Любой производный слой получает право переопределять `Task Core`.
3. Для доказательства contract требуется немедленная runtime-декомпозиция helper-а или реализация соседних track-ов.
4. После refresh managed-файлов остаётся drift между assets и локальным `knowledge/tasks/`.

## Связь с остальными файлами задачи

- `task.md` остаётся источником истины по status, branch, границам и итогу задачи;
- `plan.md` хранит только исполнимый план и verify-команды;
- `artifacts/vnext-core-contract.md` является каноническим нормативным source по модели ядра;
- `artifacts/verification-matrix.md` доказывает покрытие contract-инвариантов;
- downstream-задачи `TASK-2026-0011` ... `TASK-2026-0014` должны ссылаться на этот contract, а не переоткрывать стратегию `TASK-2026-0008`.
