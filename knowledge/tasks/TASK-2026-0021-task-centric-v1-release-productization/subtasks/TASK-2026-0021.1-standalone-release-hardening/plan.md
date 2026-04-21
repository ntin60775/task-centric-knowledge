# План задачи TASK-2026-0021.1

## Правило

Для задачи существует только один файл плана: `plan.md`.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0021.1` |
| Parent ID | `TASK-2026-0021` |
| Версия плана | `3` |
| Связь с SDD | `sdd.md`, `artifacts/verification-matrix.md` |
| Дата обновления | `2026-04-14` |

## Цель

Собрать короткий и проверяемый release-hardening пакет для `task-centric-knowledge`:
канонический дистрибутивный core-contract,
синхронизированные reference-документы,
и подтверждённый runtime-контур installer/query/workflow без ложных обещаний.

## Границы

### Входит

- перенести или адаптировать `vNext-core contract` в дистрибутивный reference-слой;
- синхронизировать `SKILL.md` и roadmap с фактическим состоянием vNext tracks;
- усилить тесты/контракт вокруг release-критичных CLI и governance-контуров;
- обновить task-local артефакты по фактическому объёму hardening.

### Не входит

- новые capability, не требуемые для release-hardening;
- memory/product-расширение или дополнительный operator UX;
- смена продуктовой траектории, уже подтверждённой в родительской задаче.

## Планируемые изменения

### Код

- точечные тесты и при необходимости небольшие runtime-правки вокруг release-critical поведения `install_skill.py`, `task_query.py`, `task_workflow.py`.

### Конфигурация / схема данных / именуемые сущности

- `references/core-model.md` как дистрибутивный core-contract;
- согласованный release-contract для install/check/doctor/query/workflow.

### Документация

- `skills-global/task-centric-knowledge/SKILL.md`
- `skills-global/task-centric-knowledge/references/core-model.md`
- `skills-global/task-centric-knowledge/references/roadmap.md`
- `skills-global/task-centric-knowledge/references/deployment.md`
- `skills-global/task-centric-knowledge/references/task-workflow.md`
- task-local файлы подзадачи и родителя при необходимости

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- допускаются только точечные правки внутри существующих runtime/tests skill-а;
- новые зависимости и новые крупные модули не добавляются.

### Границы, которые должны остаться изолированными

- task-local `vnext-core-contract` остаётся первичным источником по истории решения, а дистрибутивный `references/core-model.md` становится его release snapshot;
- roadmap не должен заново объявлять pending то, что уже реализовано в `TASK-2026-0010 ... TASK-2026-0014`;
- hardening не должен размывать границу между `Task Core`, read-model и publish/governance слоями.

### Критический функционал

- skill объясним через короткий набор канонических документов без скрытых special-cases;
- `status/current-task/task show` и install/check/doctor остаются рабочими и подтверждаются тестами;
- release-definition не вводит drift между task-local contract и дистрибутивным snapshot.

### Основной сценарий

- оператор читает `SKILL.md` и reference-файлы, быстро понимает форму продукта и опорный core-contract;
- применяет installer/query/workflow-контур без сюрпризов;
- использует skill как стабильный repo-dev слой, пока основной продукт развивается отдельно.

### Исходный наблюдаемый симптом

- release-capability уже есть, но нормативный слой не везде трактует её как завершённое, синхронизированное и канонически закреплённое состояние;
- это создаёт риск лишней полировки и повторного стратегического спора вместо прямого использования skill-а.

## Риски и зависимости

- если в runtime найдётся реальный контрактный зазор, придётся делать кодовую правку, а не ограничиться документацией;
- есть риск оставить drift между task-local core-contract и дистрибутивным snapshot, если не закрепить явную трассировку;
- есть риск переусложнить hardening лишним продуктовым слоем, если не держать жёсткий release-scope.

## Связь с SDD

- Этап 1: зафиксировать инварианты release-hardening и карту источников истины;
- Этап 2: выпустить дистрибутивный `core-model.md` и синхронизировать references;
- Этап 3: усилить тестовый контур и при необходимости runtime-поведение;
- Этап 4: прогнать verify-пакет, localization guard и закрыть task-local выводы;
- матрица покрытия: `artifacts/verification-matrix.md`.

## Проверки

### Что можно проверить кодом или тестами

- `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main status --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main current-task --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main task show TASK-2026-0021.1 --format json`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/druzhina --mode check`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/druzhina --mode doctor-deps`
- `git diff --check`
- `scripts/check-docs-localization.sh <изменённые-md-файлы>`

### Что остаётся на ручную проверку

- `не требуется`

## Шаги

- [x] Зафиксировать release-hardening invariant set и task-local verification matrix.
- [x] Выпустить `references/core-model.md` и синхронизировать `SKILL.md` и reference-файлы.
- [x] Усилить тестовый контур и при необходимости внести точечные runtime-правки.
- [x] Прогнать verify-пакет, localization guard и обновить task-local итог.
- [x] Получить пользовательский verdict по достаточности standalone hardening и закрыть или передать подзадачу.

## Критерии завершения

- `references/core-model.md` существует и очевидно является дистрибутивным snapshot ядра;
- `SKILL.md`, roadmap и workflow/deployment docs не спорят с фактической реализацией;
- release-critical контуры доказаны тестами и CLI-проверками;
- hardening завершён без открытия нового product track.
