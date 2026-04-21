# Карточка задачи TASK-2026-0024.2

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0024.2` |
| Parent ID | `TASK-2026-0024` |
| Уровень вложенности | `1` |
| Ключ в путях | `TASK-2026-0024.2` |
| Технический ключ для новых именуемых сущностей | `module-passports` |
| Краткое имя | `module-passports-and-registry` |
| Человекочитаемое описание | `Ввести managed-root `knowledge/modules/` с модульными паспортами и registry как companion-layer для постоянной инженерной памяти по governed модулям.` |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `main` |
| Требуется SDD | `нет` |
| Статус SDD | `не требуется` |
| Ссылка на SDD | `—` |
| Дата создания | `2026-04-20` |
| Дата обновления | `2026-04-21` |

## Цель

Добавить в продукт постоянный слой модульной памяти:
`knowledge/modules/README.md`,
`registry.md`
и шаблон `module.md`,
через которые governed modules будут описываться независимо от конкретной задачи,
но без конкуренции с `Task Core`.
Module passport должен быть shared/public truth для controlled execution:
он хранит публичный контракт, управляемые файлы, relation refs,
verification refs и execution-readiness summary,
но не хранит private helper churn.
Паспорт должен быть одинаково пригоден для проектов на Python, TypeScript, Go и `1С/BSL`.

## Границы

### Входит

- определить структуру `knowledge/modules/`;
- определить формат module passport и registry row;
- определить минимальный набор обязательных полей паспорта;
- определить поля `verification_ref`, `governed_files`, `file_local_policy_ref` и `execution_readiness_summary`;
- определить language-neutral поля паспорта, которые не предполагают AST/import-graph и подходят для `1С/BSL`;
- определить первый governed scope для pilot-модулей внутри skill-а.

### Не входит

- граф зависимостей и модульный query-слой как отдельные capability;
- локальная разметка файлов и каталог модульной верификации;
- обязательное покрытие модулями всего репозитория.

## Контекст

- источник постановки: заимствование из GRACE идеи module-level общей публичной истины;
- связанная область: долговременная инженерная память по модулям, живущим через несколько task-поставок;
- ограничения и зависимости: module passport не должен подменять `task.md` и не должен становиться вторым owner продуктового состояния;
- дополнительное ожидание: понятие `module` должно определяться через owned surface и контракт, а не только через package/import conventions конкретного языка;
- исходный наблюдаемый симптом / лог-маркер: в текущем продукте task-level память сильная, но постоянного модульного контекста между задачами нет;
- основной контекст сессии: `capability-подзадача Module Core`

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | будущий read-model и installer managed assets |
| Конфигурация / схема данных / именуемые сущности | новый managed-root `knowledge/modules/` и формат module passport |
| Интерфейсы / формы / страницы | read-only module registry как операторская поверхность |
| Интеграции / обмены | связь с borrowed mapping из `TASK-2026-0024.1` |
| Документация | module README, registry, template и task-local описание пилотного governed scope |

## Связанные материалы

- родительская задача: `knowledge/tasks/TASK-2026-0024-grace-borrowed-module-core/`
- контракт `Task Core`: `skills-global/task-centric-knowledge/references/core-model.md`
- boundary с GRACE: `knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/artifacts/v1-product-thesis.md`

## Текущий этап

Подзадача завершена.
Реализованы:

- управляемые assets `knowledge/modules/registry.md` и `_templates/module.md`;
- installer-governance, где `knowledge/modules/registry.md` теперь считается проектными данными
  и не перезаписывается даже при `--force`;
- объединение read-model по `module.md + verification.md + registry.md`;
- staged rollout с `source_state=verification_only|passport_ready|partial`;
- query-поднятие общей публичной истины из `module.md`
  и fallback `file show` в режимах `passport_governed` / `verification_evidence_only`;
- пилотный срез на модулях `M-MODULE-VERIFICATION` и `M-MODULE-QUERY`,
  зафиксированный как первая волна governed module passports.

Следующий implementable шаг родительской цепочки — `TASK-2026-0024.3`.

## Стратегия проверки

### Покрывается кодом или тестами

- будущие installer/read-model tests на managed-root `knowledge/modules/`;
- будущие registry sync tests для module registry;
- `git diff --check`

### Остаётся на ручную проверку

- `не требуется`

## Критерии готовности

- структура `knowledge/modules/` определена;
- у паспорта есть стабильный обязательный набор полей;
- паспорт пригоден для сборки `ExecutionPacket`, но не становится владельцем task-truth;
- schema пригодна для file-centric модулей и для `1С/BSL`, а не только для package-centric языков;
- пилотный управляемый срез выбран и не требует сразу покрывать весь репозиторий.

## Итоговый список ручных проверок

- `не требуется`

## Итог

Подзадача реализована как первый постоянный passport-layer для `Module Core`.
В продукт добавлены канонические managed assets для `knowledge/modules/`,
новый шаблон `module.md`,
навигационный registry cache,
runtime-парсинг схемы passport
и drift-проверки между `module.md`, `verification.md` и `registry.md`.

Принят жёсткий ownership:
`module.md` хранит общую публичную истину и управляемую поверхность,
`verification.md` остаётся владельцем readiness/evidence,
`registry.md` работает только как навигационный cache.
Query-layer теперь поддерживает как исторический rollout `verification_only`,
так и полноценный `passport_ready`,
не теряя пригодность для file-centric и `1С/BSL`-совместимых модулей.
