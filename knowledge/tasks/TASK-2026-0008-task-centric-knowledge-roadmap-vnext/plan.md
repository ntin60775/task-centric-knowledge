# План задачи TASK-2026-0008

## Правило

Для задачи существует только один файл плана: `plan.md`.
Если задача декомпозируется, каждая подзадача получает свой собственный `plan.md` внутри своей папки.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0008` |
| Parent ID | `—` |
| Версия плана | `15` |
| Связь с SDD | `sdd.md`, этапы 1-5; `artifacts/verification-matrix.md` |
| Дата обновления | `2026-04-12` |

План завершён и зафиксирован как итоговый контур выполнения задачи.
Пункты и проверки ниже сочетают целевую работу по задаче с фактически закрытыми этапами и финальным контуром закрытия Этапа 5.
Источником истины по фактическому прохождению этапов остаются блоки `Фактический статус` и записи в `artifacts/audit-gates.md`.

## Цель

Подготовить для `task-centric-knowledge` стратегический пакет `vNext`, который даёт понятную целевую архитектуру, явное решение `redesign ядра без full rewrite`, операторский CLI UX-контракт и промежуточные результаты до следующей волны реализации.

## Границы

### Входит

- Аудит текущего состояния skill-а и накопленных capability.
- Анализ внешних аналогов и соседних систем.
- Формализация решения `continue / redesign / fork` как `redesign ядра без full rewrite`.
- Черновик CLI UI/UX для query/reporting, diagnostics и migration cleanup.
- Roadmap по фазам и проверочным воротам.
- Синхронизация `artifacts/strategy-roadmap.md`, `skills-global/task-centric-knowledge/references/roadmap.md` и `skills-global/task-centric-knowledge/agents/openai.yaml`.
- Исправление sync-логики `registry.md` под каноническое поле `Человекочитаемое описание`.

### Не входит

- Реализация модульной декомпозиции `task_workflow.py`.
- Реализация дорожек памяти, plugin system и генераторов документации.
- Повторный host-specific smoke за пределами уже закрытого GitHub gate `TASK-2026-0007`.

## Планируемые изменения

### Код

- `skills-global/task-centric-knowledge/scripts/task_workflow.py`
- `skills-global/task-centric-knowledge/tests/test_task_workflow.py`

### Конфигурация / схема данных / именуемые сущности

- Зафиксировать целевую доменную модель `vNext`, границы ядра и операторский CLI-контракт без непосредственной реализации.
- Синхронизировать interface metadata `agents/openai.yaml` с фактическим scope skill-а без изменения runtime-кода.
- Синхронизировать кэш `knowledge/tasks/registry.md` с каноническим полем `Человекочитаемое описание` из `task.md`.

### Документация

- Создать стратегический набор документов по `TASK-2026-0008`.
- Зафиксировать изолированное evidence Этапа 1 в `artifacts/stage-1-audit.md`.
- Зафиксировать landscape review и дорожную карту развития в `artifacts/strategy-roadmap.md`.
- Синхронизировать дистрибутивный снимок стратегии в `skills-global/task-centric-knowledge/references/roadmap.md`.
- Зафиксировать CLI query/reporting draft в `artifacts/cli-ux-draft.md`.
- Зафиксировать предварительный анализ и закрытие контрольных замечаний в `artifacts/review-findings-closure.md`.
- Зафиксировать результаты audit-gates и правила их закрытия в `artifacts/audit-gates.md`.

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- `нет`, правка локализована внутри существующего helper-а синхронизации и его тестов.

### Границы, которые должны остаться изолированными

- Стратегический документ не должен автоматически переписывать runtime-код skill-а или live-копию `~/.agents/skills/task-centric-knowledge/`.
- Разрешены только синхронизационные правки дистрибутивной roadmap и interface metadata, потому что они являются частью проверяемого стратегического пакета.
- Анализ внешних систем не должен подменять локальный источник истины по текущему репозиторию.
- Исправление helper-а не должно ломать legacy-сценарий, где старый `task.md` ещё не содержит поля `Человекочитаемое описание`.

### Критический функционал

- Получить управляемую стратегию развития и минимальный операторский UX-контракт вместо расползания skill-а в очередной список фич.
- Синхронизировать сводку задачи в `registry.md` от канонического поля `Человекочитаемое описание` без ложного drift на новых и уже существующих задачах.

### Основной сценарий

- На основе локального аудита и внешних аналогов зафиксировать решение по траектории развития, фазовый roadmap и минимальный CLI UX contract.
- После ввода поля `Человекочитаемое описание` helper должен создавать и обновлять строку `registry.md` от этого поля, а для legacy-задач безопасно откатываться к `--summary` или `## Цель`.

### Исходный наблюдаемый симптом

- После ввода поля `Человекочитаемое описание` helper `task_workflow.py` продолжает синхронизировать `registry.md` через `--summary` и fallback от `## Цель`, что создаёт drift между `task.md` и `registry.md`.

## Риски и зависимости

- Есть риск сделать слишком общий framework без чёткой границы ядра.
- Есть риск неверно оценить внешние аналоги и преждевременно искать fork вместо точечных заимствований.
- Без явных ворот roadmap может игнорировать lessons learned из уже закрытого publish-flow `TASK-2026-0007`.

## Связь с SDD

- Этап 1: собрать полный invariant set стратегии и ландшафт внешних систем.
- Этап 2: принять решение по траектории `эволюция / redesign / fork` как `redesign ядра без full rewrite`.
- Этап 3: зафиксировать целевую архитектуру `vNext-core`, карту модулей и CLI-контракт запросов и отчётности.
- Этап 4: разложить roadmap на фазы, ворота и следующие delivery-задачи, включая операторский слой.
- Этап 5: закрыть замечания контрольного и комплексного ревью по источнику истины, иерархии дорожных карт, DDD-границам, хранению доказательных артефактов, source-set roadmap и доказательности матрицы.

Результаты audit-gates `SDD_AUDIT`, `DECISION_AUDIT`, `ARCHITECTURE_AUDIT`, `INTEGRATION_AUDIT` и `REVIEW_CLOSURE_AUDIT` фиксируются в `artifacts/audit-gates.md` в виде статуса, даты и краткого evidence.

## Полный список этапов

### Этап 1: Локальный и внешний аудит

| Поле | Значение |
|------|----------|
| Назначение | Зафиксировать локальные архитектурные симптомы skill-а и собрать канонический внешний landscape |
| Основные работы | Локальный аудит `task_workflow.py`, install/upgrade-контуров, lessons learned из `TASK-2026-0004/0006/0007`; сбор официальных внешних ориентиров |
| Основные артефакты | `artifacts/stage-1-audit.md`, `sdd.md` |
| Автопроверки | `VERIFY-0008-02`, `VERIFY-0008-04` |
| Audit-gate | `SDD_AUDIT` |
| Критерий выхода | В `artifacts/stage-1-audit.md` изолированно зафиксированы локальные симптомы, lessons learned, единый набор внешних ориентиров и открытые вопросы для Этапа 2; в `artifacts/audit-gates.md` подготовлена запись gate-а |

#### Детализация этапа

Входы этапа:

- `task.md`, `sdd.md`, `artifacts/verification-matrix.md`, `artifacts/stage-1-audit.md`.
- `skills-global/task-centric-knowledge/scripts/task_workflow.py`, `skills-global/task-centric-knowledge/scripts/install_skill.py`, `skills-global/task-centric-knowledge/agents/openai.yaml`.
- Материалы и решения `TASK-2026-0004`, `TASK-2026-0006`, `TASK-2026-0007`.

Последовательность работ:

1. Собрать инвентаризацию локального состояния: текущие capability skill-а, нормативные источники, зоны дублирования и точки change amplification.
2. Зафиксировать локальные архитектурные симптомы: монолитность helper-а, drift между `task.md` и `registry.md`, расхождения между metadata и фактическим scope, рост числа нормативных поверхностей.
3. Выписать lessons learned из `TASK-2026-0004/0006/0007` как обязательные ограничения для `vNext`, а не как историческую справку.
4. Собрать единый внешний landscape только по официальным источникам и по каждому ориентиру зафиксировать: ценность, применимость, границу заимствования, причину отказа от `full fork`.
5. Подготовить доказательную базу для Этапа 2: список подтверждённых фактов, открытых вопросов и стратегических развилок без финального выбора траектории.

Обязательные выходы этапа:

- В `artifacts/stage-1-audit.md` есть разделы про локальные симптомы, lessons learned и канонический набор внешних ориентиров.
- В `sdd.md` и `artifacts/verification-matrix.md` есть трассировка локального аудита к инвариантам `INV-02` и `INV-04`.
- Для каждого внешнего ориентира указано, что именно заимствуется и почему источник не становится базой для полного форка.
- Для Этапа 2 подготовлен список вопросов, которые ещё не закрыты одним только аудитом.

Ограничения этапа:

- Этап не выбирает финальную стратегию `redesign / fork / rewrite`; это решение принимает только Этап 2.
- Этап не декомпозирует delivery-задачи реализации; он только формирует доказательную базу и границы следующего шага.
- Этап не использует неофициальные обзоры как источник стратегического решения, если для ориентира есть официальный первичный материал.

Стоп-критерии:

- Нет официальных ссылок хотя бы по одному внешнему ориентиру.
- Нет явной связи хотя бы одного ключевого локального симптома с реальным файлом, metadata или предыдущей задачей.
- Lessons learned из `TASK-2026-0007` не отражены как ограничение для следующего цикла развития.

Фактический статус на `2026-04-12`:

- Критерий выхода Этапа 1 закрыт.
- Выходы Этапа 1 использованы как замороженный вход для закрытия Этапа 2.

### Этап 2: Принятие стратегического решения

| Поле | Значение |
|------|----------|
| Назначение | Принять и зафиксировать курс `continue own path / borrow ideas / do not fork / do not rewrite now` как `redesign ядра без full rewrite` |
| Основные работы | Сравнить локальную траекторию с внешними аналогами, зафиксировать отказ от `full fork` и `full rewrite`, описать правило приоритета task-local roadmap над skill-level snapshot |
| Основные артефакты | `artifacts/strategy-roadmap.md`, `artifacts/review-findings-closure.md`, `skills-global/task-centric-knowledge/references/roadmap.md` |
| Автопроверки | `VERIFY-0008-01`, `VERIFY-0008-14` |
| Audit-gate | `DECISION_AUDIT` |
| Критерий выхода | Стратегическое решение сформулировано без двусмысленности, task-local roadmap объявлена канонической, а skill-level roadmap подтверждена как дистрибутивный снимок той же стратегии |

#### Детализация этапа

Входы этапа:

- `artifacts/stage-1-audit.md`, `sdd.md`, `artifacts/verification-matrix.md`, `artifacts/audit-gates.md`.
- `artifacts/strategy-roadmap.md`, `artifacts/review-findings-closure.md`, `skills-global/task-centric-knowledge/references/roadmap.md`.
- Текущая формулировка цели и активного шага в `task.md`.

Последовательность работ:

1. Зафиксировать неизменяемую базу Этапа 2: использовать локальные симптомы, lessons learned и канонический source-set из `artifacts/stage-1-audit.md`; не переоткрывать Этап 1 без нового противоречия.
2. Разобрать открытые вопросы Этапа 1 на три группы: обязательные для решения в Этапе 2, переносимые в Этап 3/4 и ручной остаток, допустимый после `DECISION_AUDIT`.
3. Для каждого внешнего ориентира выписать конкретные заимствования и явно отделить их от идей, которые не входят в ближайший `vNext-core`.
4. Сформулировать итоговое решение одним пакетом стратегического решения: `continue own path`, `borrow ideas`, `do not fork`, `do not rewrite now`, `redesign ядра без full rewrite`, `own core + modular evolution`.
5. Зафиксировать правило иерархии источников истины: task-local `artifacts/strategy-roadmap.md` является каноническим источником, а `skills-global/task-centric-knowledge/references/roadmap.md` остаётся дистрибутивным снимком той же стратегии.
6. Подготовить evidence для `DECISION_AUDIT`: синхронизировать формулировки в `artifacts/strategy-roadmap.md`, `artifacts/review-findings-closure.md` и `skills-global/task-centric-knowledge/references/roadmap.md`, не подменяя этим архитектурные решения Этапов 3-4.

Обязательные выходы этапа:

- В `artifacts/strategy-roadmap.md` есть однозначный набор формулировок `continue own path`, `borrow ideas`, `do not fork`, `do not rewrite now` и `redesign ядра без full rewrite`.
- В task-local и skill-level roadmap совпадают канонический внешний source-set, правило приоритета источников истины и стратегический вывод.
- В `artifacts/review-findings-closure.md` решения по `FIND-02`, `FIND-07` и `FIND-10` опираются на тот же пакет стратегического решения, что и каноническая roadmap задачи.
- `VERIFY-0008-01` и `VERIFY-0008-14` можно прогнать без обращения к новым невалидированным источникам и без захода в runtime-реализацию.

Ограничения этапа:

- Этап 2 не закрывает DDD-карту, CLI-поверхность и фазовую декомпозицию реализации; это предмет Этапов 3 и 4.
- Этап 2 не меняет runtime-код skill-а, helper-ы и тесты; он готовит стратегическое решение и иерархию источников истины.
- Новый внешний ориентир нельзя включать в пакет стратегического решения без такой же официальной валидации, как в Этапе 1.

Стоп-критерии:

- Хотя бы один открытый вопрос из `artifacts/stage-1-audit.md` всё ещё влияет на выбор траектории и не классифицирован как `решить сейчас` или `отложить`.
- Task-local и skill-level roadmap расходятся по source-set, правилу приоритета или стратегическому выводу.
- Формулировка решения всё ещё допускает трактовку в пользу `full fork` или `full rewrite`.
- Для обоснования решения приходится опираться на тезисы, которых нет в Этапе 1 или в официальном source-set.

Фактический статус на `2026-04-12`:

- Этап 1 дал полный входной пакет для старта Этапа 2.
- Все четыре открытых вопроса Этапа 1 переведены в пакет стратегического решения, классификацию `отложить` и правило иерархии источников истины.
- `DECISION_AUDIT` переведён в `pass` на основе синхронизированных `artifacts/strategy-roadmap.md`, `artifacts/review-findings-closure.md` и `skills-global/task-centric-knowledge/references/roadmap.md`.
- Этот входной пакет использован для закрытия Этапа 3 без переоткрытия стратегического решения.

### Этап 3: Целевая архитектура и CLI-контракт

| Поле | Значение |
|------|----------|
| Назначение | Зафиксировать архитектуру `vNext-core`, DDD-границы и минимальный операторский CLI UX-contract |
| Основные работы | Описать `Task Core`, `Read Model / Reporting`, `Publish Integration`, `Memory`, `Packaging / Governance`, `Profiles`; зафиксировать CLI-поверхность `status/current-task/task show/doctor deps/migrate cleanup`; закрепить правило локального хранения evidence |
| Основные артефакты | `sdd.md`, `artifacts/strategy-roadmap.md`, `artifacts/cli-ux-draft.md`, `artifacts/verification-matrix.md` |
| Автопроверки | `VERIFY-0008-03`, `VERIFY-0008-07`, `VERIFY-0008-08`, `VERIFY-0008-09`, `VERIFY-0008-10`, `VERIFY-0008-12`, `VERIFY-0008-13` |
| Audit-gate | `ARCHITECTURE_AUDIT` |
| Критерий выхода | DDD-карта, слой CLI/reporting и контракт хранения evidence описаны так, что их можно декомпозировать в отдельные delivery-задачи без переоткрытия стратегии |

#### Детализация этапа

Входы этапа:

- закрытый пакет стратегического решения Этапа 2 в `task.md`, `sdd.md` и `artifacts/strategy-roadmap.md`;
- `artifacts/cli-ux-draft.md` как операторский черновик read-модели;
- `artifacts/verification-matrix.md` и `artifacts/audit-gates.md` как канонический verify/gate-контур;
- `artifacts/review-findings-closure.md` как источник обязательных замечаний по DDD-границам, единому источнику истины и хранению evidence.

Последовательность работ:

1. Зафиксировать неизменяемый вход Этапа 3: не переоткрывать вопросы `continue / redesign / fork`, а использовать уже принятый пакет `redesign ядра без full rewrite`.
2. В `sdd.md` довести `Task Core` до короткого нормативного контракта: корень агрегата, ограниченные контексты, объекты-значения, источник истины, владение по файлам и границы между core и производными слоями чтения и интеграции.
3. В `artifacts/strategy-roadmap.md` закрепить карту слоёв `vNext`, явную границу `что входит в ядро / что остаётся первой волной модульной декомпозиции / что сознательно остаётся вне core`.
4. В `artifacts/cli-ux-draft.md` зафиксировать минимальную публичную поверхность `status`, `current-task`, `task show`, `doctor deps`, `migrate cleanup plan/confirm`, а также обязательный заголовок задачи, поведение на неоднозначности и сценарии warning/drift.
5. Отдельно зафиксировать governance-инварианты Этапа 3: `registry.md` остаётся навигационным кэшем, cleanup работает только по схеме `plan -> confirm`, а все доказательные материалы задачи живут внутри каталога задачи или явно ссылаются из него.
6. Подготовить для `ARCHITECTURE_AUDIT` воспроизводимый пакет доказательств через `VERIFY-0008-03`, `VERIFY-0008-07`, `VERIFY-0008-08`, `VERIFY-0008-09`, `VERIFY-0008-10`, `VERIFY-0008-12`, `VERIFY-0008-13` без захода в runtime-рефакторинг.

Обязательные выходы этапа:

- `sdd.md` однозначно фиксирует ограниченные контексты, границы владения агрегатом, канонические объекты-значения и минимальный `vNext-core contract`;
- `artifacts/strategy-roadmap.md` содержит целевую форму `vNext`, границу `core / runtime modules / expansion layers` и явное правило, что transport layer CLI не выбирается на Этапе 3;
- `artifacts/cli-ux-draft.md` содержит полный по решениям UX-контракт по публичным intent-именам, обязательным полям вывода, классификации зависимостей, поведению на неоднозначности и cleanup-сценарию;
- `artifacts/verification-matrix.md` даёт отдельное покрытие всем инвариантам Этапа 3 и связывает их с конкретными командами;
- `artifacts/audit-gates.md` содержит явные условия закрытия `ARCHITECTURE_AUDIT`.

Ограничения этапа:

- Этап 3 не выбирает конкретный transport layer CLI и не навязывает, будет ли он отдельным бинарём, subcommand tree или thin wrapper.
- Этап 3 не выполняет runtime-декомпозицию `task_workflow.py` и не переносит host-specific publish-логику в core.
- Этап 3 не переоткрывает внешний source-set и не меняет rule hierarchy между task-local и skill-level roadmap.
- Этап 3 не подменяет Этап 4: фазовая roadmap и следующие delivery-задачи уточняются отдельно после закрытия `ARCHITECTURE_AUDIT`.

Стоп-критерии:

- хотя бы один ограниченный контекст остаётся описан как список модулей без владения агрегатом и границы ответственности;
- хотя бы одна из команд `status`, `current-task`, `task show`, `doctor deps`, `migrate cleanup` не имеет обязательных полей, warning-сценария или поведения на неоднозначности;
- cleanup-сценарий не раскрывает `TARGETS`, `TARGET_COUNT`, `COUNT`, абсолютные пути и не фиксирует запрет на расширение scope между `plan` и `confirm`;
- локальное хранение evidence не поднято до инварианта ядра и остаётся только договорённостью уровня репозитория;
- для любого ключевого архитектурного правила нельзя назвать один первичный источник внутри task-local артефактов.

Фактический статус на `2026-04-12`:

- `sdd.md`, `artifacts/strategy-roadmap.md` и `artifacts/cli-ux-draft.md` согласованы по `vNext-core`, ограниченным контекстам, публичной CLI-поверхности и cleanup-governance.
- `VERIFY-0008-03`, `VERIFY-0008-07`, `VERIFY-0008-08`, `VERIFY-0008-09`, `VERIFY-0008-10`, `VERIFY-0008-12`, `VERIFY-0008-13` пройдены.
- `ARCHITECTURE_AUDIT` переведён в `pass`.
- Этот входной пакет был использован для закрытия Этапа 4 без переоткрытия архитектурного решения.

### Этап 4: Фазовая roadmap и следующие delivery-задачи

| Поле | Значение |
|------|----------|
| Назначение | Разложить развитие на фазы, ворота перехода и следующий набор delivery-задач |
| Основные работы | Зафиксировать фазы `0..4`, переходные gate-ы, stop-критерии антиразрастания, ожидания по `doctor deps` и `migrate cleanup`, а также очередь следующей волны candidate delivery-tracks без превращения их в почти готовые `task.md` |
| Основные артефакты | `artifacts/strategy-roadmap.md`, `skills-global/task-centric-knowledge/references/roadmap.md`, `task.md`, `artifacts/audit-gates.md`, `artifacts/verification-matrix.md` |
| Автопроверки | `VERIFY-0008-05`, `VERIFY-0008-06`, `VERIFY-0008-14` |
| Audit-gate | `INTEGRATION_AUDIT` |
| Критерий выхода | Task-local и skill-level roadmap согласованы по фазам, воротам, источнику истины и стратегическому выводу; по результату можно открывать отдельные delivery-задачи |

#### Детализация этапа

Входы этапа:

- закрытый архитектурный пакет Этапа 3: `sdd.md`, `artifacts/strategy-roadmap.md`, `artifacts/cli-ux-draft.md` и `ARCHITECTURE_AUDIT = pass`;
- task-local и skill-level roadmap, которые уже совпадают по source-set и стратегическому решению, но ещё не были доведены до decision-complete фазовой дорожной карты;
- `artifacts/verification-matrix.md` и `artifacts/audit-gates.md` как канонический verify/gate-контур;
- закрывающие ограничения из `artifacts/review-findings-closure.md`: не допускать конкуренции между roadmap задачи и roadmap skill-а.

Последовательность работ:

1. Зафиксировать, что Этап 4 остаётся стратегическим пакетом: он описывает очередь следующей волны, но не создаёт новые каталоги задач и не подменяет собой `task.md` будущих delivery-единиц.
2. В `artifacts/strategy-roadmap.md` развернуть фазы `0..4` до формата `результат -> ворота перехода -> что подготавливается дальше`, чтобы следующий цикл открывался без повторного выбора курса `fork / rewrite / redesign`.
3. Добавить в task-local roadmap явную очередь candidate delivery-tracks: `vNext-core contract`, модульная декомпозиция helper-а, `doctor / cleanup governance`, `read model / reporting`, полевая валидация.
4. Для каждого candidate delivery-track зафиксировать только назначение, границы и ожидаемый выход; не превращать его в почти готовую постановку и не смешивать с runtime-реализацией Этапа 5.
5. В `skills-global/task-centric-knowledge/references/roadmap.md` синхронизировать короткий фазовый снимок, те же gate-ы и те же stop-ворота, но не переносить в него task-local evidence и расширенную классификацию долгов.
6. Зафиксировать `INTEGRATION_AUDIT` как gate, который закрывается только при одновременном наличии фаз `0..4`, переходных ворот, anti-bloat stop-критериев и синхронизированной очереди следующей волны реализации.

Обязательные выходы этапа:

- `artifacts/strategy-roadmap.md` содержит decision-complete фазовую карту `0..4`, переходные gate-ы, stop-критерии и очередь следующей волны candidate delivery-tracks;
- `skills-global/task-centric-knowledge/references/roadmap.md` даёт сокращённый, но синхронный снимок тех же фаз, ворот и stop-ворот без конкурирующего источника истины;
- `task.md` переводит активный шаг на Этап 5 и фиксирует Этап 4 как закрытый стратегический пакет;
- `artifacts/verification-matrix.md` переводит `INV-05` и `INV-06` в `covered` с опорой на воспроизводимые команды;
- `artifacts/audit-gates.md` содержит закрывающий checklist и запись `INTEGRATION_AUDIT` со статусом, датой и кратким evidence.

Ограничения этапа:

- Этап 4 не меняет runtime-код skill-а, `task_workflow.py`, `agents/openai.yaml`, `registry.md` и тесты helper-а.
- Этап 4 не создаёт новые task-каталоги и не открывает delivery-задачи автоматически; он только фиксирует их стратегическую очередь.
- Этап 4 не переоткрывает DDD-границы, CLI intent-имена и правило хранения evidence, уже закрытые Этапом 3.
- Этап 4 не переносит task-local доказательные артефакты в skill-level snapshot и не допускает появления второго канонического источника стратегии.

Стоп-критерии:

- хотя бы одна фаза остаётся описанной как абстрактное пожелание без результата и ворот перехода;
- очередь следующей волны описана как список идей без границ, ожидаемого выхода и причины отдельного выполнения;
- task-local и skill-level roadmap расходятся по фазам, stop-воротам или стратегическому выводу;
- для следующего цикла снова предлагается расширять helper-монолит до стабилизации ядра и модульной декомпозиции;
- candidate delivery-tracks начинают описываться как готовые `task.md`, хотя их реализация ещё не открыта.

Фактический статус на `2026-04-12`:

- task-local `artifacts/strategy-roadmap.md` и skill-level `references/roadmap.md` синхронизированы по фазам `0..4`, переходным gate-ам, stop-критериям и очереди следующей волны.
- В стратегическом пакете зафиксировано, что следующий цикл открывается через пять candidate delivery-tracks: `vNext-core contract`, декомпозицию helper-а, `doctor / cleanup governance`, `read model / reporting`, полевую валидацию.
- `VERIFY-0008-05`, `VERIFY-0008-06` и `VERIFY-0008-14` проходят без захода в runtime-реализацию Этапа 5.
- Evidence для `INTEGRATION_AUDIT` зафиксировано в `artifacts/audit-gates.md`, поэтому Этап 4 закрыт, а следующим активным этапом становится `Этап 5`.

### Этап 5: Закрытие замечаний ревью и синхронизационный контур

| Поле | Значение |
|------|----------|
| Назначение | Закрыть замечания ревью и довести до согласованного состояния task-local документы, skill metadata и helper sync |
| Основные работы | Синхронизировать `review-findings-closure.md`, `verification-matrix.md`, `artifacts/audit-gates.md`, `skills-global/task-centric-knowledge/agents/openai.yaml`, `task_workflow.py`, `test_task_workflow.py` и строку `TASK-2026-0008` в `knowledge/tasks/registry.md` |
| Основные артефакты | `artifacts/review-findings-closure.md`, `artifacts/verification-matrix.md`, `artifacts/audit-gates.md`, `skills-global/task-centric-knowledge/agents/openai.yaml`, `skills-global/task-centric-knowledge/scripts/task_workflow.py`, `skills-global/task-centric-knowledge/tests/test_task_workflow.py`, `knowledge/tasks/registry.md` |
| Автопроверки | `VERIFY-0008-11`, `VERIFY-0008-14`, `VERIFY-0008-15`, `VERIFY-0008-OPENAI`, `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_workflow.py` |
| Audit-gate | `REVIEW_CLOSURE_AUDIT` |
| Критерий выхода | Review-findings закрыты, verify-контур согласован, skill metadata не противоречит стратегии, а helper/registry не дают drift по `Человекочитаемому описанию` |

#### Детализация этапа

Входы этапа:

- закрытые Этапы 1-4 с `SDD_AUDIT`, `DECISION_AUDIT`, `ARCHITECTURE_AUDIT` и `INTEGRATION_AUDIT = pass`;
- task-local стратегический пакет `task.md`, `sdd.md`, `artifacts/strategy-roadmap.md`, `artifacts/cli-ux-draft.md`, `artifacts/review-findings-closure.md`;
- runtime-состояние helper-а и metadata, в котором `task_workflow.py`, `test_task_workflow.py`, `agents/openai.yaml` и строка `TASK-2026-0008` в `knowledge/tasks/registry.md` уже допускают воспроизводимую финальную проверку без новой функциональности;
- `artifacts/verification-matrix.md` и `artifacts/audit-gates.md` как единый verify/gate-контур этапа закрытия.

Последовательность работ:

1. Зафиксировать, что Этап 5 не переоткрывает стратегический пакет Этапов 2-4 и не меняет принятые решения по `fork / rewrite / redesign`.
2. В `artifacts/review-findings-closure.md` разделить findings на уже закрытые Этапами 2-4, исторически снятые синхронизацией ветки и активный пакет закрытия Этапа 5: `FIND-09`, `FIND-11`, `FIND-12`, `FIND-13`.
3. В `artifacts/verification-matrix.md` оставить финальный verify-контур Этапа 5 на `INV-11`, `INV-14`, `INV-15` и `VERIFY-0008-OPENAI`; после фактического прогона перевести `INV-11` и `INV-15` в `covered`.
4. В `artifacts/audit-gates.md` добавить подготовку к старту Этапа 5 и переводить `REVIEW_CLOSURE_AUDIT` в `pass` только при одновременном прохождении `VERIFY-0008-11`, `VERIFY-0008-14`, `VERIFY-0008-15`, `VERIFY-0008-OPENAI` и unit-тестов helper-а.
5. Синхронизировать `task.md` и строку `TASK-2026-0008` в `knowledge/tasks/registry.md` с финальным состоянием задачи: `Статус = завершена`, `Статус SDD = завершено`, Этап 5 закрыт, дополнительный Этап 6 не требуется.
6. Повторно прогнать локализационный контроль Markdown-артефактов и `git diff --check`, чтобы пакет закрытия считался завершённым не только логически, но и формально.

Обязательные выходы этапа:

- `artifacts/review-findings-closure.md` содержит явную карту закрытия по этапам и отдельно фиксирует активный пакет Этапа 5 `FIND-09`, `FIND-11`, `FIND-12`, `FIND-13`;
- `artifacts/verification-matrix.md` переводит `INV-11` и `INV-15` в `covered`, а verify-контур больше не содержит `planned`-строк для Этапа 5;
- `artifacts/audit-gates.md` содержит `REVIEW_CLOSURE_AUDIT = pass` с датой и кратким evidence;
- `task.md` и `knowledge/tasks/registry.md` согласованы по финальному статусу задачи и не оставляют открытого активного этапа;
- новые runtime-возможности не добавлены: этап закрытия только подтверждает уже синхронизированное состояние helper-а, тестов и metadata.

Ограничения этапа:

- Этап 5 не меняет DDD-карту, source-set внешних ориентиров, фазовую roadmap и публичные intent-имена CLI.
- Этап 5 не вводит новые capability в `task_workflow.py`, не расширяет `agents/openai.yaml` сверх уже согласованного scope и не меняет `artifacts/strategy-roadmap.md`, если для этого нет явной причины синхронизации.
- Этап 5 не открывает отдельный следующий этап внутри этой же задачи; следующий цикл допускается только через candidate delivery-tracks из roadmap.

Стоп-критерии:

- хотя бы одна из проверок `VERIFY-0008-11`, `VERIFY-0008-14`, `VERIFY-0008-15`, `VERIFY-0008-OPENAI` или unit-тесты helper-а не проходят;
- `task.md`, `registry.md` и `agents/openai.yaml` дают разные ответы о статусе task summary, scope skill-а или корректности имени;
- этап закрытия начинает заново редактировать стратегические решения вместо фиксации доказательств и gate-ов;
- после синхронизации остаётся открытый активный шаг, требующий Этапа 6, хотя stage-5 verify-контур уже пройден.

Фактический статус на `2026-04-12`:

- `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_workflow.py` пройден: `42` теста подтверждают helper-level sync канонической сводки и legacy-fallback.
- `VERIFY-0008-11`, `VERIFY-0008-14`, `VERIFY-0008-15` и `VERIFY-0008-OPENAI` пройдены без новых правок runtime-кода.
- `review-findings-closure.md`, `verification-matrix.md` и `audit-gates.md` синхронизированы по финальному пакету закрытия Этапа 5.
- `REVIEW_CLOSURE_AUDIT` закрыт, `task.md` и `knowledge/tasks/registry.md` переведены в завершённое состояние, поэтому дополнительный Этап 6 не требуется.

## Проверки

### Фактически прогнанные автопроверки

- `scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/task.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/plan.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/sdd.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/stage-1-audit.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/verification-matrix.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/strategy-roadmap.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/cli-ux-draft.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/audit-gates.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/review-findings-closure.md skills-global/task-centric-knowledge/references/roadmap.md`
- `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_workflow.py`
- `git diff --check`
- Воспроизводимые команды `VERIFY-0008-01` ... `VERIFY-0008-15` и `VERIFY-0008-OPENAI` из `artifacts/verification-matrix.md`

### Итоговый ручной остаток

- Дополнительный ручной остаток для финального этапа закрытия не требуется: содержательные стратегические оценки были закрыты Этапами 1-4, а Этап 5 носит чисто синхронизационный и доказательный характер.

## Шаги

- [x] Собрать локальный аудит текущего состояния skill-а и уже реализованных capability.
- [x] Параллельно собрать экспертные заключения по архитектурным рискам и внешним аналогам.
- [x] Оформить новую стратегическую задачу knowledge-системы.
- [x] Закрыть открытые вопросы Этапа 2 и отделить обязательные заимствования для `vNext-core` от отложённого слоя.
- [x] Зафиксировать стратегическое решение `continue own path / borrow ideas / do not fork / do not rewrite now` и иерархию источников истины между task-local и skill-level roadmap.
- [x] Зафиксировать `vNext`-цель и фазовый roadmap.
- [x] Добавить отдельный CLI UI/UX draft и включить его в стратегическую рамку `vNext`.
- [x] Закрыть замечания контрольного ревью с предварительным анализом по каждому замечанию.
- [x] Закрыть Этап 4 как стратегический пакет: синхронизировать фазы `0..4`, gate-ы, stop-критерии и очередь candidate delivery-tracks между task-local и skill-level roadmap.
- [x] Закрыть замечания комплексного ревью по синхронизации roadmap, доказательности матрицы, scope и `agents/openai.yaml`.
- [x] Зафиксировать для каждого audit-gate в `artifacts/audit-gates.md` статус `planned/pass/fail/manual-residual`, дату и краткое evidence.
- [x] Исправить sync `registry.md` под каноническое поле `Человекочитаемое описание` и закрыть drift по `TASK-2026-0008`.
- [x] Закрыть `REVIEW_CLOSURE_AUDIT`, синхронизировать `task.md` и `knowledge/tasks/registry.md` по финальному статусу задачи.
- [x] Прогнать локализационные и форматные проверки по новым Markdown-артефактам.

## Критерии завершения

На `2026-04-12` критерии завершения закрыты:

- В knowledge-системе есть отдельная задача со стратегией развития `task-centric-knowledge`.
- Есть явно сформулированный курс: `continue own path`, `borrow ideas`, `do not fork`, `do not rewrite now`, `redesign ядра без full rewrite`.
- Зафиксирован query/reporting contract для операторских CLI-команд.
- Findings контрольного ревью закрыты проверяемыми изменениями в task-local и skill-level документации.
- Helper и тесты доказывают, что `registry.md` синхронизируется от `Человекочитаемого описания`, а legacy-задачи не ломаются.
- Строка `TASK-2026-0008` в `knowledge/tasks/registry.md` совпадает с `task.md`.
- Есть roadmap минимум из нескольких фаз с измеримыми результатами.
- Результаты audit-gates зафиксированы в `artifacts/audit-gates.md` со статусом, датой и кратким evidence.
- Зафиксированы stop-критерии, при которых roadmap нужно пересматривать.
