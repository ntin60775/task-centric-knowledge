# Карточка задачи TASK-2026-0027

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0027` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0027` |
| Технический ключ для новых именуемых сущностей | `local-auto-finalize` |
| Краткое имя | `local-auto-finalize` |
| Человекочитаемое описание | Добавить local auto-finalize helper: безопасный локальный `commit -> merge -> checkout main` или явный stop-report с причинами блокировки. |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `агент` |
| Ветка | `main` |
| Требуется SDD | `да` |
| Статус SDD | `в работе` |
| Ссылка на SDD | `sdd.md` |
| Дата создания | `2026-04-21` |
| Дата обновления | `2026-04-21` |

## Цель

Довести workflow-слой до ожидаемого пользователем поведения: после завершения задачи локальный helper должен либо автоматически выполнить task-scoped `commit`, безопасно влить task-ветку в base-ветку и вернуть рабочий контекст на `main`, либо остановиться без мутаций и вернуть явный список причин блокировки с вариантами следующего действия.

## Подсказка по статусу

Использовать только одно из значений:

- `черновик`
- `готова к работе`
- `в работе`
- `на проверке`
- `ждёт пользователя`
- `заблокирована`
- `завершена`
- `отменена`

## Git-подсказка

- Поле `Ветка` хранит текущую активную ветку рабочего контекста, а не обязательную долгоживущую task-ветку.
- На старте задачи это обычно `task/...`.
- Во время поставки helper может переводить `Ветка` в delivery-ветку вида `du/<task-id-lower>-uNN-<slug>`.
- Для подзадачи по умолчанию можно указывать ветку родителя, если отдельная ветка или delivery unit не нужны.
- При каждом создании или переключении ветки нужно синхронизировать это поле и строку в `registry.md`.

## Границы

### Входит

- новый local finalize surface в unified CLI и legacy workflow facade;
- runtime-проверки безопасного finalize-контекста и structured stop-report;
- автоматический локальный `commit -> merge -> checkout base/main` без `push`;
- синхронизация `task.md` и `registry.md` после успешного локального finalize;
- тесты и reference-документация по новому finalize-поведению.

### Не входит

- автоматический `push`, PR/MR publish и сетевые публикации;
- переписывание истории, `rebase`, `reset`, удаление веток;
- автоматическое закрытие задач при наличии незавершённых delivery units или неоднозначного task-контекста без явного blocker-report.

## Контекст

- источник постановки: пользователь явно ожидает от проекта auto-finalize локального git-контура после завершения задачи;
- связанная бизнес-область: task workflow / local operator UX;
- ограничения и зависимости: helper обязан оставаться local-only, не обещать network actions и не обходить existing stop-conditions по грязному дереву и неоднозначному контексту;
- исходный наблюдаемый симптом / лог-маркер: `references/task-workflow.md` и `SKILL.md` прямо фиксируют, что helper не делает `finalize-task`, не пушит и не удаляет ветки;
- основной контекст сессии: `текущая задача`

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | Unified CLI, workflow runtime, git helpers, текстовый/JSON surface finalize-результата |
| Конфигурация / схема данных / именуемые сущности | Новая CLI-команда или action finalize и её payload contract |
| Интерфейсы / формы / страницы | `нет` |
| Интеграции / обмены | Локальный git workflow без сетевого publish |
| Документация | `README.md`, `SKILL.md`, `references/task-workflow.md`, task-артефакты |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0027-local-auto-finalize/`
- файл плана: `plan.md`
- файл SDD: `sdd.md`
- файл verification matrix: `artifacts/verification-matrix.md`
- канонический нормативный contract или source-of-truth для доменной модели, если задача его меняет: `references/core-model.md`, `references/task-workflow.md`
- пользовательские материалы: текущий диалог о local auto-finalize
- связанные коммиты / PR / ветки: `task/task-2026-0027-local-auto-finalize`
- связанные операции в `knowledge/operations/`, если есть: `нет`

## Контур публикации

Delivery unit описывает конкретную поставку через ветку и публикацию.
В одном `task.md` допускается `0..N` delivery units.
`registry.md` хранит только задачи и подзадачи, поэтому delivery units в него не добавляются.

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | — | `—` | `—` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |

Подсказка по статусам delivery unit:

- `planned` — контур поставки ещё не стартовал.
- `local` — delivery-ветка создана локально, публикации ещё нет.
- `draft` — draft PR/MR опубликован.
- `review` — публикация готова к review.
- `merged` — поставка влита, merge commit зафиксирован.
- `closed` — поставка закрыта без merge.

## Текущий этап

Local auto-finalize helper реализован, docs синхронизированы, полный verify loop пройден. Текущий этап задачи - локальная проверка итогового diff и подготовка к git-финализации.

## Стратегия проверки

### Покрывается кодом или тестами

- `python3 -m unittest discover -s tests`
- целевые unit-тесты на finalize runtime, CLI surface и blocker-report
- `python3 scripts/task_knowledge_cli.py workflow --help`
- `python3 scripts/task_knowledge_cli.py task show --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge TASK-2026-0027`
- `bash scripts/check-docs-localization.sh`
- `git diff --check`

### Остаётся на ручную проверку

- проверка фактического операторского UX на внешнем репозитории с реальными task-ветками вне sandbox-ограничений, если понадобится дополнительное field validation

## Критерии готовности

- unified CLI даёт явный finalize surface для local-only сценария;
- helper безопасно делает локальный finalize при валидном task-контексте;
- при любом блокере helper не мутирует git-состояние и возвращает явный stop-report с действиями;
- `task.md`, `registry.md`, tests и reference-docs синхронизированы с новым contract.

## Итоговый список ручных проверок

- Проверить local finalize на внешнем репозитории с реальным merge в `main`, если понадобится подтвердить поведение вне sandbox.

## Итог

Реализован отдельный local-only finalize path для workflow runtime и unified CLI. Helper теперь либо делает task-scoped commit, fast-forward merge в base-ветку и checkout base-ветки, либо возвращает явный blocker-report без частичных git-мутаций. Полный `unittest`, localization guard и `git diff --check` пройдены локально; сетевой `push` и cleanup веток по контракту остаются отдельными действиями.
