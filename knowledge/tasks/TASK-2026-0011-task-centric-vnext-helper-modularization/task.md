# Карточка задачи TASK-2026-0011

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0011` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0011` |
| Технический ключ для новых именуемых сущностей | `vnext-helper-modules` |
| Краткое имя | `task-centric-vnext-helper-modularization` |
| Человекочитаемое описание | `Модульная декомпозиция helper-контуров task-centric-knowledge без регрессии git и publish-flow` |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `task/task-2026-0011-task-centric-vnext-helper-modularization` |
| Требуется SDD | `да` |
| Статус SDD | `завершено` |
| Ссылка на SDD | `sdd.md` |
| Дата создания | `2026-04-12` |
| Дата обновления | `2026-04-13` |

## Цель

Разрезать `skills-global/task-centric-knowledge/scripts/task_workflow.py` на модульные зоны ответственности
так, чтобы доменная логика, markdown I/O, registry sync, git/publish-операции и CLI-слой перестали жить в одном orchestration-монолите.

## Границы

### Входит

- выделение модулей доменной модели и переходов состояний;
- отделение markdown I/O и registry sync от бизнес-правил;
- отделение git/publish-операций и adapter-слоя;
- перенос unit-тестов с монолитных сценариев на модульный уровень;
- сохранение поведения `sync` и publish-flow без регрессии.

### Не входит

- изменение стратегического курса `TASK-2026-0008`;
- расширение host parity и новых capability;
- внедрение memory-layer;
- продуктовая read-model для операторских команд.

## Контекст

- источник постановки: Track 2 из `TASK-2026-0008`;
- основной technical debt: монолитность `task_workflow.py`;
- зависимость: `TASK-2026-0010` завершена и даёт нормативный `vNext-core contract`, на который опирается этот runtime-разрез;
- baseline подтверждён локально: `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_workflow.py` проходит (`44` теста);
- текущий риск совместимости: regression-набор грузит `scripts/task_workflow.py` по файлу через `importlib`, поэтому facade-entrypoint обязан сохранить file-based import surface.

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | `scripts/task_workflow.py`, новые модули helper-а, test-suite |
| Архитектура | разделение domain, I/O, git/publish и CLI |
| Тесты | модульные unit-тесты и regression coverage |
| Документация | task-артефакты задачи и технические notes по новому разрезу |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0011-task-centric-vnext-helper-modularization/`
- файл плана: `plan.md`
- файл SDD: `sdd.md`
- матрица проверки: `artifacts/verification-matrix.md`
- стратегический источник: `knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/strategy-roadmap.md`

## Контур публикации

Delivery unit для черновика постановки пока не требуется.

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | — | `—` | `—` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |

## Текущий этап

Реализация завершена:
runtime helper-а вынесен в пакет `scripts/task_workflow_runtime/`,
`task_workflow.py` оставлен тонким facade-entrypoint,
а доказательство parity перенесено на сочетание black-box regression, модульных и архитектурных тестов.

## Стратегия проверки

### Покрывается кодом или тестами

- `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_workflow.py`;
- `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'`;
- `python3 skills-global/task-centric-knowledge/scripts/task_workflow.py --help`;
- архитектурный тест на разрешённый import graph и тонкий facade;
- `git diff --check`;
- `scripts/check-docs-localization.sh` по всем изменённым Markdown-файлам задачи и skill-а, если они будут затронуты.

### Остаётся на ручную проверку

- `не требуется`, если import graph и facade-проверки закрыты автоматикой.

## Критерии готовности

- `task_workflow.py` перестал быть единственным носителем политики и выполняет только bootstrap, compatibility re-export и CLI-dispatch;
- runtime helper-а живёт в пакете `scripts/task_workflow_runtime/` с явным разрезом `models / git_ops / task_markdown / registry_sync / forge / sync_flow / publish_flow / cli`;
- `sync` и publish-flow не теряют совместимость по существующим `44` regression-сценариям;
- модульные и архитектурные тесты подтверждают отсутствие циклов и скрытого orchestration-монолита;
- verification matrix переведена в `covered` по всем инвариантам.

## Итоговый список ручных проверок

- `не требуется`

## Итог

`task_workflow.py` перестал быть orchestration-монолитом и теперь выступает совместимым facade-entrypoint поверх модульного runtime-пакета.

Вынесены отдельные слои `models`, `git_ops`, `task_markdown`, `registry_sync`, `forge`, `sync_flow`, `publish_flow`, `cli`,
а black-box regression по прежнему file-based import surface сохранён.

Дополнительно добавлены новые модульные и архитектурные тесты.
Итоговый verify-контур подтверждён командами:
`python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_workflow.py`,
`python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'`,
`python3 skills-global/task-centric-knowledge/scripts/task_workflow.py --help`,
`git diff --check`
и локализационным guard по task-local Markdown.
