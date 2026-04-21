# Карточка задачи TASK-2026-0021.1

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0021.1` |
| Parent ID | `TASK-2026-0021` |
| Уровень вложенности | `1` |
| Ключ в путях | `TASK-2026-0021.1` |
| Технический ключ для новых именуемых сущностей | `release-hardening` |
| Краткое имя | `standalone-release-hardening` |
| Человекочитаемое описание | Довести `task-centric-knowledge` до release-grade standalone состояния без расширения product scope сверх уже подтверждённого ядра. |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `main` |
| Требуется SDD | `да` |
| Статус SDD | `завершена` |
| Ссылка на SDD | `sdd.md` |
| Дата создания | `2026-04-14` |
| Дата обновления | `2026-04-14` |

## Цель

Закрыть release-hardening контур `task-centric-knowledge` как самостоятельного repo-dev продукта:
свести к одному понятному дистрибутивному контракту уже реализованное ядро,
убрать drift между roadmap и фактическим состоянием skill-а,
и усилить проверочный контур вокруг installer/query/workflow без наращивания новой product surface.

## Границы

### Входит

- дистрибутивный core-contract внутри `skills-global/task-centric-knowledge/references/`;
- синхронизация `SKILL.md` и reference-документов с уже реализованными tracks `TASK-2026-0010 ... TASK-2026-0014`;
- точечный hardening тестов и runtime-контракта installer/query/workflow там, где это уменьшает release-risk;
- обновление task-local артефактов подзадачи и родительской задачи по факту реализации.

### Не входит

- новый memory-layer, новые host adapters и расширение publish-surface;
- перепроектирование базовой модели задачи поверх GRACE;
- отдельный новый продуктовый UX поверх существующих helper/CLI.

## Контекст

- источник постановки: подтверждённый запрос пользователя от `2026-04-14` выполнить четыре pragmatic hardening-пункта и довести skill до рабочего и надёжного состояния;
- связанная область: release-hardening `task-centric-knowledge` как repo-dev операционной системы задач;
- ограничения и зависимости: не превращать hardening в новый большой product track; опираться на уже завершённые `TASK-2026-0010 ... TASK-2026-0014`;
- исходный наблюдаемый симптом / лог-маркер: часть release-контракта уже реализована в runtime и тестах, но дистрибутивные reference-файлы не везде трактуют это как завершённое и канонически закреплённое состояние;
- основной контекст сессии: `подзадача внутри TASK-2026-0021`

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | точечные правки test/runtime при необходимости закрытия release-risk |
| Конфигурация / схема данных / именуемые сущности | дистрибутивный `core-model` и release-contract skill-а |
| Интерфейсы / формы / страницы | CLI-контракт `status/current-task/task show` как часть release-definition |
| Интеграции / обмены | install/check/doctor/cleanup governance без расширения host-specific semantics |
| Документация | `SKILL.md`, `references/*.md`, task-local артефакты подзадачи и родителя |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/subtasks/TASK-2026-0021.1-standalone-release-hardening/`
- файл плана: `plan.md`
- файл SDD: `sdd.md`
- файл verification matrix: `artifacts/verification-matrix.md`
- родительская задача: `knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/`
- task-local контракт ядра: `knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md`
- roadmap и strategy context: `knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/`
- дистрибутив skill-а: `skills-global/task-centric-knowledge/`
- связанные коммиты / PR / ветки: `task/task-2026-0021-1-standalone-release-hardening`

## Текущий этап

Подзадача завершена.
Release-hardening пакет реализован и проверен:
выпущен дистрибутивный `references/core-model.md`,
синхронизированы `SKILL.md` и reference-файлы,
добавлены release-contract тесты,
полный unit-прогон skill-а зелёный,
а live CLI-проверки подтвердили рабочий install/query контур.
Пользователь подтвердил,
что такого уровня hardening уже достаточно до релиза `Druzhina`,
после чего итог подзадачи передан в родительскую `TASK-2026-0021` и закрыт.

## Стратегия проверки

### Покрывается кодом или тестами

- `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main status --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main current-task --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main task show TASK-2026-0021.1 --format json`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/druzhina --mode check`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/druzhina --mode doctor-deps`
- `git diff --check`
- `scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/task.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/subtasks/TASK-2026-0021.1-standalone-release-hardening/task.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/subtasks/TASK-2026-0021.1-standalone-release-hardening/plan.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/subtasks/TASK-2026-0021.1-standalone-release-hardening/sdd.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/subtasks/TASK-2026-0021.1-standalone-release-hardening/artifacts/verification-matrix.md skills-global/task-centric-knowledge/SKILL.md skills-global/task-centric-knowledge/references/core-model.md skills-global/task-centric-knowledge/references/roadmap.md skills-global/task-centric-knowledge/references/deployment.md skills-global/task-centric-knowledge/references/task-workflow.md skills-global/task-centric-knowledge/references/adoption.md knowledge/tasks/registry.md`

### Остаётся на ручную проверку

- `не требуется`

## Критерии готовности

- у skill-а есть один явный дистрибутивный core-contract, на который ссылаются `SKILL.md` и reference-документы;
- reference-файлы не описывают как будущие те capability, которые уже реализованы и используются в release-контуре;
- installer/query/workflow hardening закрыт проверками и не оставляет неподтверждённых runtime-обещаний;
- итог подзадачи укрепляет standalone release-line, но не открывает новую большую волну product expansion.

## Итоговый список ручных проверок

- `не требуется`

## Итог

Закрыты следующие release-risk:

- у skill-а появился явный дистрибутивный core-contract `references/core-model.md`, трассируемый к `TASK-2026-0010`;
- `SKILL.md`, `deployment.md`, `task-workflow.md`, `adoption.md` и `roadmap.md` синхронизированы с уже реализованными tracks `TASK-2026-0010 ... TASK-2026-0014`;
- warning-first сценарий `parent + subtask на одной ветке -> ambiguous/branch_tie` зафиксирован в reference-слое и закреплён тестом;
- добавлен release-contract test-suite на трассировку `core-model` и статусов закрытых tracks;
- полный прогон `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'` прошёл успешно (`113 tests`, `OK`);
- live `check` и `doctor-deps` на `Druzhina` подтвердили отсутствие core/local blockers и publish/integration issues.

Финальный вывод подзадачи:
skill находится в рабочем и надёжном состоянии как repo-dev слой,
а дальнейшая глубокая полировка до релиза `Druzhina` уже не обязательна.
Этот вывод подтверждён пользователем и использован для закрытия родительской `TASK-2026-0021`.
