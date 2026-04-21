# План задачи TASK-2026-0021

## Правило

Для задачи существует только один файл плана: `plan.md`.
Если задача декомпозируется, каждая подзадача получает свой собственный `plan.md` внутри своей папки.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0021` |
| Parent ID | `—` |
| Версия плана | `1` |
| Связь с SDD | `Этапы 1-4 в sdd.md` |
| Дата обновления | `2026-04-14` |

## Цель

Превратить накопленный `vNext`-пакет `task-centric-knowledge` в понятный `v1`-продукт с явным release-scope, закрытым knowledge-drift и проверяемым решением по отношению к `grace-marketplace`.

## Границы

### Входит

- открыть productization-задачу и зафиксировать канонический scope;
- синхронизировать legacy task summary/status/branch metadata в knowledge-системе репозитория;
- сформулировать release-grade продуктовую форму `task-centric-knowledge v1`;
- сравнить `task-centric-knowledge` и `grace-marketplace` на уровне product boundary, а не на уровне маркетинговых названий;
- определить дальнейший delivery backlog только после product decision.

### Не входит

- конкурирующий редизайн сразу двух продуктов одновременно;
- интеграция с новыми host/provider системами вне уже подтверждённого scope;
- полное внедрение GRACE в этот репозиторий в рамках текущего шага.

## Планируемые изменения

### Код

- `нет`, если repo-wide drift удаётся закрыть одними knowledge-артефактами и существующим helper/read-model.

### Конфигурация / схема данных / именуемые сущности

- каноническое описание `task-centric-knowledge v1`;
- явное решение `continue / adapter / pivot`;
- синхронизация status/summary/branch metadata в `knowledge/tasks/registry.md` и legacy `task.md`.

### Документация

- `knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/task.md`
- `knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/plan.md`
- `knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/sdd.md`
- `knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/artifacts/verification-matrix.md`
- `knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/artifacts/v1-product-thesis.md`
- legacy `knowledge/tasks/**/task.md`, если им не хватает канонической summary-тройки
- `knowledge/tasks/registry.md`

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- `нет`, если release-definition удаётся закрыть на уровне knowledge и существующих helper-скриптов.

### Границы, которые должны остаться изолированными

- `task-centric-knowledge` не должен разрастаться в полный contract-first engineering framework уровня GRACE только ради оправдания своего существования;
- `grace-marketplace` не должен подменять собой task-local source of truth репозитория без отдельного решения о миграции;
- устранение drift в knowledge-метаданных не должно менять смысл завершённых задач.

### Критический функционал

- knowledge-система репозитория показывает консистентный статус задач без legacy summary/status/branch drift;
- продукт `task-centric-knowledge v1` описан так, чтобы пользователь понимал, что именно уже считается рабочей системой;
- сравнение с `grace-marketplace` приводит к проверяемому решению, а не к бесконечной стратегической подвешенности.

### Основной сценарий

- пользователь открывает репозиторий и должен понять, что `task-centric-knowledge` уже умеет как продукт;
- read-model `status/current-task/task show` не вводит в заблуждение legacy drift-ом;
- продуктовая документация объясняет, почему нужен именно этот продукт и где проходит граница относительно GRACE.

### Исходный наблюдаемый симптом

- `task_query status` поднимает warnings по legacy summary/status/branch drift;
- пользователь считает продукт зависшим между roadmap и работающей первой версией.

## Риски и зависимости

- есть риск обнаружить, что desired `v1` по факту совпадает с продуктовой целью GRACE и standalone-линия `task-centric-knowledge` не оправдана;
- есть риск, что часть legacy drift окажется следствием реального поведения helper-а, а не только старых task-артефактов;
- без жёсткой product boundary новая задача снова превратится в roadmap вместо release-definition.

## Связь с SDD

- Этап 1: закрыть knowledge-drift и подтвердить фактическое состояние read-model;
- Этап 2: выпустить канонический `v1-product-thesis` и decision matrix относительно GRACE;
- Этап 3: определить release-gates и stop-критерии;
- Этап 4: синхронизировать task-local выводы, проверить матрицу и подготовить следующий delivery backlog;
- матрица покрытия: `artifacts/verification-matrix.md`.

## Проверки

### Что можно проверить кодом или тестами

- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main status --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main current-task --format json`
- `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main --mode check`
- `git diff --check`
- `scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/task.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/plan.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/sdd.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/artifacts/verification-matrix.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/artifacts/v1-product-thesis.md knowledge/tasks/registry.md`

### Что остаётся на ручную проверку

- `не требуется`

## Шаги

- [x] Синхронизировать новую задачу с веткой и реестром.
- [x] Устранить repo-wide knowledge-drift вне skill-кода.
- [x] Зафиксировать `v1-product-thesis` и предварительное решение относительно `grace-marketplace`.
- [x] Прогнать verify-контур и обновить итог задачи.
- [x] Получить финальный verdict пользователя, что standalone hardening уже достаточен и дальнейшая глубокая полировка skill-а может быть отложена до post-release фазы `Druzhina`.

## Критерии завершения

- release-grade контур `v1` описан бинарно и без двусмысленности;
- repo-wide drift устранён или явно сведён к отдельно зафиксированным остаткам;
- есть чёткое решение, зачем продолжать этот продукт отдельно от GRACE или почему этого делать не надо.
