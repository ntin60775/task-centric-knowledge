# Карточка задачи TASK-2026-0024.5

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0024.5` |
| Parent ID | `TASK-2026-0024` |
| Уровень вложенности | `1` |
| Ключ в путях | `TASK-2026-0024.5` |
| Технический ключ для новых именуемых сущностей | `module-verification` |
| Краткое имя | `module-verification-catalog` |
| Человекочитаемое описание | `Добавить каталог модульной верификации, который переиспользуется task-local verification matrix и фиксирует канонические проверки governed modules.` |
| Статус | `завершена` |
| Приоритет | `средний` |
| Ответственный | `Codex` |
| Ветка | `main` |
| Требуется SDD | `нет` |
| Статус SDD | `не требуется` |
| Ссылка на SDD | `—` |
| Дата создания | `2026-04-20` |
| Дата обновления | `2026-04-20` |

## Цель

Сделать module-level verification переиспользуемой:
зафиксировать для governed modules канонические автоматические проверки,
маркеры smoke-проверок
и остаточный ручной риск,
чтобы task-local `verification-matrix` ссылалась на модульный контур,
а не изобретала его заново в каждой задаче.
Этот же контур должен выдавать `ExecutionReadiness`,
`VerificationExcerpt` и `FailureHandoff` для single-writer execution,
чтобы write-pass не начинался без проверяемых критериев.
Verification-модель должна быть language-agnostic и пригодной для `1С/BSL`.

## Границы

### Входит

- определить форму module-level verification records;
- определить связь module verification <-> task-local verification matrix;
- определить, какие проверки считаются каноническими для governed module;
- определить `ExecutionReadiness` как gate перед writer-subagent;
- определить `VerificationExcerpt` для `ExecutionPacket`;
- определить `FailureHandoff` как связку contract/evidence/anchor для исправления;
- определить language-neutral типы evidence и проверок, пригодные для разных toolchain, включая `1С/BSL`;
- определить, где хранится manual residual по модулю и по задаче.

### Не входит

- замена task-local verification matrix;
- обязательный coverage всех существующих модулей репозитория;
- интеграция с full GRACE verification-plan.xml.

## Контекст

- источник постановки: borrowed-идея reusable verification evidence из GRACE;
- связанная область: повторное использование модульных проверок между задачами;
- ограничения и зависимости: task-local matrix остаётся обязательной для сложных задач и владельцем task-specific invariant coverage;
- дополнительное ожидание: модульная верификация не может требовать только `pytest`/`npm test`-подобные сценарии и должна поддерживать проверки, типичные для `1С/BSL`;
- исходный наблюдаемый симптом / лог-маркер: сейчас verification хорошо описана на уровне задачи, но плохо переиспользуется на уровне модуля;
- основной контекст сессии: `capability-подзадача Module Core`

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | runtime `module_core_runtime/verification.py` для parser/readiness/excerpt/handoff и unit-тесты на него |
| Конфигурация / схема данных / именуемые сущности | отдельный артефакт `knowledge/modules/<MODULE-ID>-<slug>/verification.md`, additive managed template и связка `verification_ref -> ExecutionReadiness / VerificationExcerpt / FailureHandoff` |
| Интерфейсы / формы / страницы | groundwork для `module show --with verification`, без реализации CLI в этой подзадаче |
| Интеграции / обмены | reuse policy между module verification и task-local `artifacts/verification-matrix.md` |
| Документация | template `verification.md`, `knowledge/modules/README.md` и task-local фиксация storage/policy |

## Связанные материалы

- родительская задача: `knowledge/tasks/TASK-2026-0024-grace-borrowed-module-core/`
- тестовый контракт `Task Core`: `knowledge/tasks/TASK-2026-0006-task-centric-testing-contract/`
- текущий verification pattern в skill-е: `knowledge/tasks/_templates/artifacts/verification-matrix.md`
- runtime реализации `Module Core` для parser/readiness/excerpt/handoff
- additive managed template модульной верификации
- unit-тесты verification runtime и installer-контура

## Текущий этап

Подзадача завершена.
Зафиксирован отдельный storage pattern:
reusable module verification живёт в `verification.md`,
а passport модуля хранит только `verification_ref`
и краткую readiness summary.
Добавлен runtime для parser/readiness/excerpt/handoff,
managed template для `knowledge/modules/_templates/verification.md`
и install-test coverage.
Следующий активный шаг родительского трека —
подзадача query-layer,
где `VerificationExcerpt` будет поднят в read-only query surface.

## Стратегия проверки

### Покрывается кодом или тестами

- unit-тесты verification runtime
- unit-тесты installer/compatibility контура
- `git diff --check`
- команда проверки локализации: `bash scripts/check-docs-localization.sh`

### Остаётся на ручную проверку

- `не требуется`

## Критерии готовности

- module-level verification model определена;
- связь с task-local matrix однозначна;
- readiness gate и failure handoff описаны как verification-derived контракты;
- verification records допускают разные типы evidence, включая `1С/BSL`-совместимые проверки;
- ownership task-specific invariant coverage не потерян.

## Итоговый список ручных проверок

- `не требуется`

## Итог

Подзадача реализована как отдельный verification foundation для `Module Core`.
Выбран и зафиксирован storage pattern `verification_ref -> verification.md`,
а не секция внутри passport и не единый глобальный catalog-файл.
Новый runtime умеет:
парсить модульный verification markdown,
валидировать refs и cross-links,
вычислять `ExecutionReadiness`,
строить `VerificationExcerpt`
и формировать `FailureHandoff`.

В install-слой добавлены additive managed assets:
README модульного companion-layer
и template `verification.md`.
Это не завершает `TASK-2026-0024.2`,
но даёт канонический template для reusable verification уже сейчас,
не дожидаясь полного module passport/query rollout.
