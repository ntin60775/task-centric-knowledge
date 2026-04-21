# `vNext-core contract` для `task-centric-knowledge`

## Статус и назначение

- Статус: канонический нормативный источник Track 1 по `TASK-2026-0010`.
- Назначение: зафиксировать минимальный, но decision-complete contract ядра `task-centric-knowledge`, на который могут ссылаться `TASK-2026-0011` ... `TASK-2026-0014` без повторного стратегического выбора.
- Граница применения: этот документ отвечает только за модель `Task Core`, ownership по файлам, допустимые переходы состояний, источник истины и evidence / cleanup governance.
- Стратегические решения уровня фаз, gate-ов и очереди следующих track-ов остаются за `TASK-2026-0008`.
- Если возникает расхождение по модели ядра, приоритет у этого документа; если возникает расхождение по стратегической фазности, приоритет у `TASK-2026-0008`.

## DDD-карта контекстов

| Контекст | Чем владеет | Чего делать не может |
|----------|-------------|----------------------|
| `Task Core` | Семантика задачи, task-local сущности, source of truth, допустимые переходы состояний, ownership по `task.md` и связанным task-local файлам | Не делегирует смысл задачи `registry.md`, read-model, publish-адаптерам, memory-layer или профилям |
| `Read Model / Reporting` | Read-only проекции `status`, `current-task`, `task show`, warnings о неоднозначности и drift | Не меняет доменную модель и не становится источником истины |
| `Publish Integration` | Delivery-oriented интеграцию с forge-хостингами, publish-статусы и URL delivery units | Не меняет `Task Core` в обход канонических переходов и не протаскивает host-specific semantics в ядро |
| `Memory` | Дополнительные memory lanes и ссылки на производные знания | Не конкурирует с `task.md` и не подменяет task-local evidence |
| `Packaging / Governance` | Install, check, upgrade, doctor, cleanup после миграции | Не удаляет `project data` молча и не владеет смыслом задачи |
| `Profiles` | Профильные формулировки, шаблоны и overlay-слой | Не меняет семантику ядра, статусов, summary и ownership |

## Агрегат `Task Core`

### Корень агрегата

- Корень агрегата: `Task`.
- Канонический локальный контур агрегата: каталог `knowledge/tasks/<TASK-ID>-<slug>/`.

### Канонические task-local сущности

| Сущность | Каноническое представление | Что означает |
|----------|----------------------------|--------------|
| `Task` | `task.md` и каталог задачи | Основная planning-сущность со status, summary, branch, boundaries и итогом |
| `Subtask` | `subtasks/<TASK-ID>-<slug>/task.md` | Дочерняя task-local сущность внутри цели родителя |
| `Delivery Unit` | Таблица `## Контур публикации` в `task.md` | Контур конкретной поставки через branch и публикацию |
| `Verification Matrix` | `artifacts/verification-matrix.md` | Доказательная связка `инвариант -> сценарий -> проверка -> статус покрытия` |
| `Task Artifact` | Любой task-local материал в `artifacts/` | Evidence, samples, reports, migration notes и другие материалы задачи |
| `Decision` | `decisions.md` | Осознанные проектные решения и отклонения от SDD |
| `Worklog Entry` | `worklog.md` | Хронология хода задачи, этапов и проверок |
| `Handoff` | `handoff.md` | Передача задачи другому исполнителю или пользователю на проверку |

### Объекты-значения

| Объект-значение | Где зафиксирован | Смысл |
|-----------------|------------------|-------|
| `Task ID` | `task.md`, имя каталога, `registry.md` | Стабильный идентификатор задачи |
| `Task Slug` | имя каталога, краткое имя в `task.md`, git-ветка | Короткий технический ключ контекста |
| `Task Status` | `task.md`, кэш в `registry.md` | Planning-состояние задачи |
| `Branch Ref` | поле `Ветка` в `task.md`, кэш в `registry.md` | Текущий git-контекст задачи |
| `Publication State` | таблица delivery units в `task.md` | Состояние конкретной поставки |
| `Evidence Ref` | task-local путь или явная ссылка из `artifacts/` | Указатель на доказательный материал |

## Источник истины и ownership по файлам

| Носитель | Чем владеет | Чем не владеет |
|----------|-------------|----------------|
| `task.md` | `TASK-ID`, `Краткое имя`, `Человекочитаемое описание`, `Статус`, `Ветка`, границы, текущий этап, delivery units, итоговый ручной checklist, итог задачи | Не дублирует SDD, verification matrix и runtime-реализацию |
| `plan.md` | Исполнимые шаги, риски, проверки, связь с SDD и критерии завершения | Не переопределяет архитектуру и не становится вторым источником истины |
| `sdd.md` | Полный invariant set, архитектура, этапы реализации, критерии приёмки и stop-критерии | Не подменяет `task.md` по status, summary и итоговому состоянию |
| `artifacts/verification-matrix.md` | Покрытие инвариантов и статус доказательства | Не владеет границами задачи или её summary |
| `artifacts/` | Все task-local evidence и ссылки на внешние объекты | Не подменяет описание задачи и не становится отдельной roadmap |
| `worklog.md` | История движения и прохождения этапов | Не подменяет summary, status и decision record |
| `decisions.md` | Осознанные решения и отклонения | Не подменяет task summary, SDD или verification matrix |
| `handoff.md` | Контекст передачи и ссылка на единый ручной checklist | Не создаёт второй источник истины по ручным проверкам |
| `registry.md` | Навигационный cache по задачам и подзадачам | Не владеет смыслом задачи, status model и delivery units |
| `references/roadmap.md` и `SKILL.md` | Дистрибутивный snapshot и методика skill-а | Не переопределяют task-local source of truth |

## Каноническая task summary

- Каноническая summary любой задачи строится только из тройки:
  - `TASK-ID`
  - `Краткое имя`
  - `Человекочитаемое описание`
- Единственный источник этой тройки: `task.md`.
- `registry.md`, helper, read-model и любые future memory-layers могут только кэшировать или проецировать эту summary.
- Если между task-local карточкой и производной проекцией есть расхождение, приоритет всегда у `task.md`.

## Модель состояний

### Статусы `Task` и `Subtask`

Канонический набор статусов:

- `черновик`
- `готова к работе`
- `в работе`
- `на проверке`
- `ждёт пользователя`
- `заблокирована`
- `завершена`
- `отменена`

Допустимые переходы:

- `черновик -> готова к работе | отменена`
- `готова к работе -> в работе | заблокирована | отменена`
- `в работе -> на проверке | ждёт пользователя | заблокирована | отменена`
- `на проверке -> завершена | в работе | ждёт пользователя | заблокирована | отменена`
- `ждёт пользователя -> готова к работе | в работе | отменена`
- `заблокирована -> готова к работе | в работе | отменена`

Финальные состояния:

- `завершена`
- `отменена`

### Статусы `Delivery Unit`

Канонический набор статусов:

- `planned`
- `local`
- `draft`
- `review`
- `merged`
- `closed`

Допустимые переходы:

- `planned -> local | closed`
- `local -> draft | closed`
- `draft -> review | closed`
- `review -> merged | draft | closed`

Финальные состояния:

- `merged`
- `closed`

Дополнительные инварианты:

- delivery unit живёт только внутри `task.md`;
- `registry.md` не получает отдельных строк для delivery units;
- задача не может считаться окончательно закрытой, пока все delivery units не находятся в `merged` или `closed`.

## Evidence и cleanup governance

### Локальное хранение evidence

- Все доказательные артефакты задачи по умолчанию живут внутри `artifacts/` этой задачи.
- Предпочтительные task-local подкаталоги: `screenshots/`, `logs/`, `samples/`, `reports/`, `migration/`.
- Если объект физически нельзя положить в репозиторий, в `artifacts/` должна быть явная ссылка на него и краткое объяснение, почему он внешний.
- Внешний объект без task-local ссылки не считается корректным evidence для задачи.

### Правила cleanup-governance

- Любой cleanup в слое `Packaging / Governance` наследует модель `plan -> confirm`.
- До подтверждения cleanup обязан раскрыть свой scope настолько, чтобы было ясно, какие task-local или migration-related объекты он затрагивает.
- Cleanup не может молча расширять scope между `plan` и `confirm`.
- `project data`, включая `knowledge/tasks/registry.md` и уже созданные task-каталоги, нельзя удалять или перезаписывать без явного и проверяемого шага подтверждения.

## Явные запреты

- Нельзя делать `registry.md` источником истины по смыслу задачи, status или summary.
- Нельзя делать read-model, publish-layer, memory-layer или profiles равноправным владельцем состояния `Task Core`.
- Нельзя переносить source of truth из task-local каталога в host-specific adapter, external memory или generated report.
- Нельзя использовать этот contract как повод сразу выбирать transport layer CLI, file-level modularization helper-а, host parity или memory implementation details.

## Что не входит в Track 1

- Не выбирать runtime-разрез модулей helper-а.
- Не проектировать `doctor deps` и `migrate cleanup` глубже базового governance-инварианта.
- Не определять output contract `status / current-task / task show`.
- Не проектировать field-validation и adoption package.

## Downstream-очередь

- `TASK-2026-0011` использует этот contract как вход для file-level modularization и ownership helper-модулей.
- `TASK-2026-0012` расширяет только governance-слой, не меняя ядро.
- `TASK-2026-0013` строит read-model поверх этого source-of-truth, а не вместо него.
- `TASK-2026-0014` валидирует продуктовую форму, не переопределяя core semantics.
