# Карточка задачи TASK-2026-0021

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0021` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0021` |
| Технический ключ для новых именуемых сущностей | `v1-release` |
| Краткое имя | `task-centric-v1-release-productization` |
| Человекочитаемое описание | `Финишировать первую релизную версию task-centric-knowledge, устранить repo-wide knowledge-drift и принять product decision относительно grace-marketplace` |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `main` |
| Требуется SDD | `да` |
| Статус SDD | `завершена` |
| Ссылка на SDD | `sdd.md` |
| Дата создания | `2026-04-13` |
| Дата обновления | `2026-04-14` |

## Цель

Убрать текущую продуктовую неоднозначность вокруг `task-centric-knowledge`:
синхронизировать накопившийся knowledge-drift репозитория,
зафиксировать release-grade форму первой полнофункциональной версии,
и принять проверяемое решение, зачем продолжать развитие этого продукта отдельно от `/home/prog7/MyWorkspace/30-Knowledge/AI/grace-marketplace/`,
а где правильнее брать готовый GRACE-стек целиком или строить адаптерный мост.

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
- При открытии верхнеуровневой задачи стартовый контекст обычно синхронизируется в `task/<task-id-lower>-<slug>`.
- Для первой и последующих поставок helper может переводить `Ветка` в delivery-ветку вида `du/<task-id-lower>-uNN-<slug>`.
- Для подзадачи по умолчанию можно указывать ветку родителя, если отдельная ветка или delivery unit не нужны.
- При каждом создании или переключении ветки нужно синхронизировать это поле и строку в `registry.md`.

## Границы

### Входит

- устранить repo-wide knowledge-drift в `task.md` и `knowledge/tasks/registry.md`, если он не требует изменения skill-кода;
- определить, что именно считается первой релизной, полнофункциональной версией `task-centric-knowledge`;
- зафиксировать конечный пользовательский сценарий, в котором система уже считается реально рабочей, а не только стратегически правильно спроектированной;
- сравнить продуктовую цель `task-centric-knowledge` с `grace-marketplace` и принять одно из решений: `развивать отдельно`, `строить адаптерный слой`, `считать GRACE целевым продуктом`;
- зафиксировать release-gate-ы, stop-критерии и минимальный scope, после которого продукт можно честно считать `v1`.

### Не входит

- немедленное переписывание `task-centric-knowledge` на архитектуру GRACE;
- расширение helper-а новыми большими capability вне release-scope `v1`;
- удалённая публикация, `push` и PR/MR в рамках текущего шага;
- продуктовые обещания, которые нельзя подтвердить локальными артефактами, verify-контуром или validated workflow.

## Контекст

- источник постановки: прямой запрос пользователя от `2026-04-13` устранить repo-wide drift, перестать держать продукт в подвешенном состоянии и открыть новую задачу на финиш первой релизной версии;
- связанная бизнес-область: task-centric operating system для агентной разработки внутри git-репозитория;
- ограничения и зависимости: сравнение с `grace-marketplace` должно быть предметным и не сводиться к поверхностному "у них тоже есть skills";
- исходный наблюдаемый симптом / лог-маркер: `task_query status` поднимает legacy warnings (`summary_drift`, `summary_fallback_goal`, `branch_drift`), а пользователь считает продукт застрявшим между стратегией и готовой рабочей системой;
- основной контекст сессии: `текущая задача`

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | точечные изменения helper/runtime допускаются только если без них невозможно подтвердить release-grade контур |
| Конфигурация / схема данных / именуемые сущности | каноническая формула продукта `task-centric-knowledge v1`, release-gates и решение по отношению к `grace-marketplace` |
| Интерфейсы / формы / страницы | read-only operator UX `status/current-task/task show` как часть release-definition |
| Интеграции / обмены | граница между `task-centric-knowledge`, forge publish-flow и внешним продуктом `grace-marketplace` |
| Документация | `task.md`, `plan.md`, `sdd.md`, `artifacts/verification-matrix.md`, `artifacts/v1-product-thesis.md`, legacy task-карточки и `knowledge/tasks/registry.md` |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/`
- файл плана: `plan.md`
- файл SDD: `sdd.md`
- файл verification matrix: `artifacts/verification-matrix.md`
- product-thesis и сравнение с GRACE: `artifacts/v1-product-thesis.md`
- модель внедрения для 1С-легаси: `artifacts/grace-task-layer-1c-model.md`
- связанный стратегический контекст: `knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/`
- канонический контракт ядра: `knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md`
- проверенный пакет внедрения: `skills-global/task-centric-knowledge/references/adoption.md`
- внешний сравниваемый продукт: `/home/prog7/MyWorkspace/30-Knowledge/AI/grace-marketplace/README.md`
- пользовательские материалы: сообщения пользователя от `2026-04-13`
- связанные коммиты / PR / ветки: `task/task-2026-0021-task-centric-v1-release-productization`
- связанные операции в `knowledge/operations/`, если есть: `нет`

## Контур публикации

Delivery unit для текущего product-definition этапа пока не требуется.

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | — | `—` | `—` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |

## Текущий этап

Задача завершена.
Пользователь подтвердил,
что текущий standalone hardening уже достаточен для закрытия release-definition шага.
`TASK-2026-0021.1` закрыта как достаточный hardening-пакет,
repo-wide knowledge-drift устранён,
а продуктовая формула `task-centric-knowledge v1` зафиксирована
как узкая `standalone`-линия task-centric operating system для репозитория.
Глубокая дополнительная полировка отложена до post-release фазы `Druzhina`.

## Стратегия проверки

### Покрывается кодом или тестами

- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main status --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main current-task --format json`
- `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main --mode check`
- `git diff --check`
- `scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/task.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/plan.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/sdd.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/artifacts/verification-matrix.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/artifacts/v1-product-thesis.md knowledge/tasks/registry.md`
- `scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/task.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/plan.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/sdd.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/artifacts/verification-matrix.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/artifacts/v1-product-thesis.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/artifacts/grace-task-layer-1c-model.md knowledge/tasks/registry.md`

### Остаётся на ручную проверку

- `не требуется`

## Критерии готовности

- repo-wide knowledge-drift, который не требует изменения skill-кода, устранён и подтверждён `task_query status`;
- определена проверяемая release-формула `task-centric-knowledge v1` с бинарными release-gates;
- явно сформулировано, чем продукт является и чем не является по отношению к `grace-marketplace`;
- есть решение, при каких условиях продукт продолжается как самостоятельный, а при каких дальнейшее развитие нужно остановить в пользу GRACE или адаптерного слоя;
- итоговый ручной checklist и дальнейший delivery backlog не противоречат выбранной продуктовой траектории.

## Итоговый список ручных проверок

- `не требуется`

## Итог

Задача закрыта с подтверждённым пользовательским verdict:
`task-centric-knowledge v1` фиксируется как standalone task-centric operating system для репозитория,
а не как ещё один contract-first engineering framework.

В релизный scope вошли:
предсказуемый `knowledge/`-контур,
локальный источник истины по задаче,
маршрутизация `текущая задача / подзадача / новая задача`,
operator CLI `status/current-task/task show`,
минимально достаточный git/publish lifecycle
и install/check/doctor/upgrade governance без потери project data.

Сознательно не вошли:
расширение в сторону full framework уровня GRACE,
слой семантической разметки и граф-ориентированной инженерной навигации
и любая новая большая product-поверхность поверх уже подтверждённого ядра.

Отдельное существование продукта признано оправданным только в узкой формуле `standalone`.
Траектория `adapter` остаётся допустимым следующим delivery-направлением,
если позже понадобится связка `task lifecycle + GRACE contract workflow`,
но не является prerequisite для релизной `v1`.
