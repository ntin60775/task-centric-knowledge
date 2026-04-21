# Карточка задачи TASK-2026-0025

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0025` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0025` |
| Технический ключ для новых именуемых сущностей | `knowledge-upgrade` |
| Краткое имя | `task-centric-knowledge-local-upgrade` |
| Человекочитаемое описание | `Обновить managed knowledge-систему этого репозитория до текущей версии skill-а task-centric-knowledge без потери project data.` |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `task/task-2026-0025-task-centric-knowledge-local-upgrade` |
| Требуется SDD | `нет` |
| Статус SDD | `не требуется` |
| Ссылка на SDD | `—` |
| Дата создания | `2026-04-20` |
| Дата обновления | `2026-04-20` |

## Цель

Локально обновить managed-ресурсы `task-centric-knowledge` в текущем репозитории
до актуальной версии из `/home/prog7/.agents/skills/task-centric-knowledge/`,
сохранив `project data`, существующие task-каталоги и пользовательские разделы вне managed-блока `AGENTS.md`.

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

- локальная диагностика `check` и `doctor-deps` для текущего project-root;
- обновление managed knowledge-файлов и managed-блока `AGENTS.md` через `install --force`;
- проверка, что `knowledge/tasks/registry.md` и уже существующие каталоги задач не потеряли project data;
- проверка cleanup-governance через `migrate-cleanup-plan`, если upgrade создаст installer-generated хвосты;
- локализационная проверка новых task-артефактов этой задачи.

### Не входит

- публикация изменений в remote, `push` и PR/MR;
- массовое переписывание существующих task-артефактов как части новой версии;
- реализация новых capability из `TASK-2026-0024`.

## Контекст

- источник постановки: пользовательский запрос от `2026-04-20` обновить систему до последней версии через skill `task-centric-knowledge`;
- связанная бизнес-область: локальный upgrade knowledge-системы и managed governance;
- ограничения и зависимости: upgrade должен идти отдельным task-scoped переходом и не должен повреждать `project data`;
- исходный наблюдаемый симптом / лог-маркер: текущий репозиторий классифицируется как `compatible`, значит ожидается upgrade managed-ресурсов поверх существующего контура;
- основной контекст сессии: `обновление локальной knowledge-системы до актуальной версии skill-а`

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | installer/runtime контур не меняется напрямую, но его upgrade применяется к репозиторию |
| Конфигурация / схема данных / именуемые сущности | managed knowledge-файлы и managed-блок `AGENTS.md` |
| Интерфейсы / формы / страницы | read-only operator поведение может обновиться через managed-шаблоны |
| Интеграции / обмены | локальный install/upgrade контур skill-а |
| Документация | task-local артефакты `TASK-2026-0025` и обновлённые managed-docs |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0025-task-centric-knowledge-local-upgrade/`
- файл плана: `plan.md`
- файл SDD: `—`
- файл verification matrix: `—`
- безопасный порядок upgrade: `skills-global/task-centric-knowledge/references/upgrade-transition.md`
- skill-источник upgrade: `/home/prog7/.agents/skills/task-centric-knowledge/`
- пользовательские материалы: сообщение пользователя от `2026-04-20`
- связанные коммиты / PR / ветки: `task/task-2026-0025-task-centric-knowledge-local-upgrade`
- связанные операции в `knowledge/operations/`, если есть: `нет`

## Контур публикации

Delivery unit для локального upgrade пока не требуется.

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | — | `—` | `—` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |

## Текущий этап

Локальный transition завершён.
`install --force` выполнен успешно,
post-upgrade diagnostics зелёные,
а materialized managed-файлы уже совпадали с актуальной версией skill-а,
поэтому фактический git-diff ограничился task-local артефактами и строкой в `registry.md`.

## Стратегия проверки

### Покрывается кодом или тестами

- `python3 /home/prog7/.agents/skills/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules --mode check`
- `python3 /home/prog7/.agents/skills/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules --mode install --force`
- `python3 /home/prog7/.agents/skills/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules --mode doctor-deps`
- `python3 /home/prog7/.agents/skills/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules --mode migrate-cleanup-plan`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules task show TASK-2026-0025 --format json`
- `git diff --check`
- `bash scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0025-task-centric-knowledge-local-upgrade/task.md knowledge/tasks/TASK-2026-0025-task-centric-knowledge-local-upgrade/plan.md knowledge/tasks/registry.md`

### Остаётся на ручную проверку

- `не требуется`

## Критерии готовности

- managed knowledge-контур обновлён до текущего skill-source;
- `project data` и существующие task-каталоги не повреждены;
- `registry.md` содержит новую задачу и синхронизирован с её веткой;
- `migrate-cleanup-plan` либо пустой, либо ограничен ожидаемым allowlist scope;
- diff не содержит структурных ошибок.

## Итоговый список ручных проверок

- `не требуется`

## Итог

Для текущего репозитория выполнен безопасный upgrade-контур
`check -> install --force -> doctor-deps -> migrate-cleanup-plan`.
Installer подтвердил совместимую классификацию `compatible`,
обновил managed-scope без ошибок
и не тронул `project data`, включая `knowledge/tasks/registry.md`.

После применения `install --force` фактический diff не показал новых изменений
в materialized managed-файлах и managed-блоке `AGENTS.md`,
что означает:
репозиторий уже находился на последней доступной локально версии
`task-centric-knowledge`,
а запрос пользователя привёл систему в подтверждённое актуальное состояние.

Cleanup-governance также подтверждён:
`TARGET_COUNT=0`, `COUNT=0`,
без safe-delete объектов и без необходимости запрашивать подтверждение на удаление.
