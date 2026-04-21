# SDD по задаче TASK-2026-0021

## Паспорт SDD

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0021` |
| Статус | `завершено` |
| Версия | `1` |
| Дата обновления | `2026-04-14` |

## 0. Инварианты и verification matrix

### Полный invariant set

- `INV-01`: knowledge-система репозитория не содержит устранимого legacy drift по канонической summary-тройке, статусу и branch metadata в рамках затронутых задач.
- `INV-02`: `task-centric-knowledge v1` определён как продукт с конечным пользовательским обещанием и бинарными release-gates, а не как бесконечная roadmap.
- `INV-03`: решение относительно `/home/prog7/MyWorkspace/30-Knowledge/AI/grace-marketplace/` зафиксировано в явной product boundary: `standalone`, `adapter`, `pivot` или `stop`.
- `INV-04`: если развитие `task-centric-knowledge` продолжается отдельно, его ценность ограничена ролью task-centric operating system для репозитория и не дублирует GRACE как contract-first engineering framework.
- `INV-05`: verify-контур задачи доказывает как консистентность knowledge-системы репозитория, так и воспроизводимость текущего runtime состояния skill-а.

### Связанные артефакты проверки

- `artifacts/verification-matrix.md` — матрица `инвариант -> сценарий нарушения -> проверка/команда -> статус покрытия`.
- `artifacts/v1-product-thesis.md` — канонический продуктовый тезис и решение относительно GRACE.

## 1. Проблема и цель

### Проблема

К `2026-04-13` у `task-centric-knowledge` есть сильный стратегический пакет `TASK-2026-0008` ... `TASK-2026-0015`,
но пользователь не получил из этого однозначного ответа, что именно уже считается рабочей системой.
Дополнительно read-model поднимает legacy warnings по `summary_drift`, `summary_fallback_goal`, `branch_drift`,
а значит knowledge-контур репозитория визуально выглядит незавершённым даже там, где core/runtime уже стабилизирован.

Второй слой проблемы продуктовый:
рядом существует `/home/prog7/MyWorkspace/30-Knowledge/AI/grace-marketplace/` — более оформленный framework с готовым CLI и зрелой skill-поверхностью.
Если `task-centric-knowledge` не определит свою жёсткую продуктовую границу, дальнейшее развитие будет выглядеть как дублирование уже существующего решения.

### Цель

После завершения задачи должно быть истинно следующее:

- knowledge-система репозитория не вводит в заблуждение устранимым legacy drift;
- есть короткое и проверяемое определение `task-centric-knowledge v1`;
- есть явное решение, зачем продукт развивать отдельно от GRACE, а где нужно остановиться и выбрать GRACE или адаптерный слой;
- следующий delivery backlog определяется release-логикой продукта, а не очередным абстрактным исследованием.

## 2. Архитектура и границы

- изменение работает на уровне task-local knowledge, release-definition и product boundary;
- затрагиваются `knowledge/tasks/**`, `knowledge/tasks/registry.md` и task-local product artifacts новой задачи;
- сравнение с GRACE выполняется на уровне назначения продукта, install/adoption UX, source of truth и operator workflow;
- если обнаружится, что release-goal фактически равен продуктовой цели GRACE, задача должна поднять stop-signal, а не придумывать искусственное отличие.

### Допустимые и недопустимые связи

- допустимо использовать `TASK-2026-0008`, `TASK-2026-0010`, `TASK-2026-0014`, `references/adoption.md` и README GRACE как первичные источники решения;
- допустимо синхронизировать legacy `task.md` и `registry.md`, если это не меняет смысл завершённых задач;
- недопустимо менять `task-centric-knowledge` код только ради маскировки документарного drift;
- недопустимо объявлять `task-centric-knowledge` конкурентом GRACE по всей поверхности возможностей, если реальный scope продукта уже другой.

### Новые зависимости и их обоснование

- `нет`

### Наблюдаемые сигналы и диагностические маркеры

- `task_query status --format json` показывает warnings по legacy drift;
- пользовательский сигнал: "я ожидал рабочую систему уже на этом этапе";
- наличие зрелого соседнего продукта `grace-marketplace` создаёт product-choice pressure и требует явного решения.

## 3. Изменения данных / схемы / metadata

- обновляются task-local summary поля `Человекочитаемое описание` в legacy карточках;
- синхронизируются строки `knowledge/tasks/registry.md` по статусу, summary и branch metadata;
- создаётся новый task-local product artifact `artifacts/v1-product-thesis.md`.

## 4. Новые сущности и интерфейсы

- `v1-product-thesis` как канонический task-local артефакт продуктовой позиции;
- матрица решений `task-centric-knowledge vs grace-marketplace`;
- release-gates для `task-centric-knowledge v1`.

## 5. Изменения в существующих компонентах

- `knowledge/tasks/registry.md`
  - синхронизируется с каноническими полями `task.md` для задач, где есть устранимый drift;
- legacy `knowledge/tasks/**/task.md`
  - получают отсутствующее поле `Человекочитаемое описание` и, где нужно, нормализуют branch/status metadata;
- `knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/*`
  - фиксируют release-definition, product boundary и verify-контур.

## 6. Этапы реализации и проверки

### Этап 1: Repo-wide knowledge sync

- найти все затронутые legacy task-карточки и строки `registry.md`, где drift устраним без изменения смыслов задач;
- синхронизировать summary/status/branch metadata до консистентного состояния;
- Verify: `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main status --format json`
- Audit: `IMPLEMENTATION_AUDIT`

### Этап 2: Product thesis и граница с GRACE

- зафиксировать конечную формулу `task-centric-knowledge v1`;
- выпустить decision matrix `standalone / adapter / pivot`;
- явно назвать случаи, когда развивать продукт дальше нельзя и нужно брать GRACE;
- Verify: `rg -n "standalone|adapter|pivot|GRACE|release-gate|не делать" knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/artifacts/v1-product-thesis.md`
- Audit: `SDD_AUDIT`

### Этап 3: Release gates и stop-критерии

- перевести продуктовую формулу в бинарные критерии готовности;
- зафиксировать, какой именно пользовательский сценарий считается доказательством "рабочей системы";
- Verify: `rg -n "release-gate|рабочая система|stop|v1" knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/task.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/sdd.md`
- Audit: `ARCHITECTURE_AUDIT`

### Финальный этап: Интеграция

- прогнать текущий runtime verify-контур skill-а;
- выполнить Markdown localization guard по новым и изменённым документам;
- синхронизировать итог задачи и подготовить следующий delivery backlog;
- Verify: `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'`
- Verify: `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main --mode check`
- Verify: `git diff --check`
- Verify: `scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/task.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/plan.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/sdd.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/artifacts/verification-matrix.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/artifacts/v1-product-thesis.md knowledge/tasks/registry.md`
- Audit: `INTEGRATION_AUDIT`

## 7. Критерии приёмки

1. `task_query status` больше не показывает устранимый drift по summary/status/branch для синхронизированных задач.
2. Есть один короткий product artifact, который отвечает, что такое `task-centric-knowledge v1`.
3. В продуктовой формуле явно указано, когда брать `grace-marketplace`, а не продолжать `task-centric-knowledge`.
4. Итог задачи позволяет открыть следующий delivery-track без нового стратегического спора о самом существовании продукта.
5. Все новые и изменённые Markdown-артефакты проходят локализационный guard.

## 8. Стоп-критерии

1. Если desired `v1` по факту требует contract-first XML/semantic-markup platform уровня GRACE, standalone-линия `task-centric-knowledge` должна быть остановлена.
2. Если drift нельзя устранить без изменения helper-кода, а не только knowledge-данных, это нужно выделять в отдельный delivery-step, а не маскировать вручную.
3. Если продуктовую формулу нельзя объяснить короче и яснее, чем формулу GRACE, задача считается неудачной и требует пересмотра траектории.

## Связь с остальными файлами задачи

- `task.md` остаётся источником истины по статусу, итогу и ручному checklist;
- `plan.md` хранит исполнимый маршрут реализации;
- `artifacts/verification-matrix.md` доказывает покрытие инвариантов;
- `artifacts/v1-product-thesis.md` хранит итоговую продуктовую позицию.
