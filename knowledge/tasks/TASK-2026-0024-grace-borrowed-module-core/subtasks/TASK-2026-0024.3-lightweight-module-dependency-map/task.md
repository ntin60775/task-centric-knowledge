# Карточка задачи TASK-2026-0024.3

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0024.3` |
| Parent ID | `TASK-2026-0024` |
| Уровень вложенности | `1` |
| Ключ в путях | `TASK-2026-0024.3` |
| Технический ключ для новых именуемых сущностей | `module-deps` |
| Краткое имя | `lightweight-module-dependency-map` |
| Человекочитаемое описание | `Добавить лёгкую dependency-модель между governed modules без перехода к full knowledge-graph.xml и полной graph-платформе уровня GRACE.` |
| Статус | `завершена` |
| Приоритет | `средний` |
| Ответственный | `Codex` |
| Ветка | `main` |
| Требуется SDD | `нет` |
| Статус SDD | `не требуется` |
| Ссылка на SDD | `—` |
| Дата создания | `2026-04-20` |
| Дата обновления | `2026-04-21` |

## Цель

Добавить к модульным паспортам и registry минимально достаточную dependency-модель,
которая даст навигацию по связям,
сводки зависимостей для `ExecutionPacket`,
но не потянет за собой полный graph-contract и XML-слой GRACE.
Dependency-модель должна быть пригодна и для языков без классического графа импортов, включая `1С/BSL`.

## Границы

### Входит

- выбрать минимальный набор полей связей (`depends_on`, `used_by`, `governed_files`, `public_contracts`);
- определить, где канонически хранится истина о связях;
- определить минимальный набор предупреждений о невалидных relation-строках и отсутствующих целях;
- определить, как выдержки по связям попадают в execution packet и query output;
- определить язык-независимую семантику связей для file-centric и metadata-centric модулей, включая `1С/BSL`;
- ограничить первую волну пилотных управляемых модулей.

### Не входит

- полный `knowledge-graph.xml`;
- богатый язык graph-query;
- автоматическое покрытие всех import/dependency-связей в репозитории.

## Контекст

- источник постановки: желание заимствовать из GRACE module-level navigation, но без полного graph-framework;
- связанная область: lightweight dependency-видимость между governed modules;
- ограничения и зависимости: новая модель должна быть достаточно простой для ручного сопровождения и read-model drift-checks;
- дополнительное ожидание: relation-layer не может опираться только на синтаксический импорт и должен поддерживать ручные контрактные связи для `1С/BSL`;
- исходный наблюдаемый симптом / лог-маркер: после появления module passports без relation-layer модульная память останется плоской и плохо пригодной для навигации;
- основной контекст сессии: `capability-подзадача Module Core`

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | runtime relation-parser, вычисляемая reverse-map и warning-коды read-model |
| Конфигурация / схема данных / именуемые сущности | поля связей в module passports и контракт text/JSON для `module show --with relations` |
| Интерфейсы / формы / страницы | `module show` со сводкой зависимостей, исходящими `depends_on` и вычисляемым `used_by` |
| Интеграции / обмены | связь с borrowings mapping и file-local contracts |
| Документация | управляемый шаблон, README и task-local описание relation-model и её границ |

## Связанные материалы

- родительская задача: `knowledge/tasks/TASK-2026-0024-grace-borrowed-module-core/`
- будущий managed-root из `TASK-2026-0024.2`
- GRACE reference-идея knowledge graph: `/home/prog7/РабочееПространство/work/AI/git-update-only/grace-marketplace/skills/grace/grace-explainer/references/knowledge-graph.md`

## Текущий этап

Подзадача реализована.
В read-model добавлен v1 relation-layer,
который читает исходящие `depends_on` из `module.md`,
строит вычисляемый `used_by`,
возвращает сводку зависимостей для `ExecutionPacket`
и не требует import-graph, XML или отдельной graph-платформы.

Приняты жёсткие границы первой волны:

- canonical relation-truth живёт только в `module.md`;
- `registry.md` relation-строки не кэширует;
- разрешены только цели вида exact `MODULE-ID` другого governed module;
- `used_by` вычисляется автоматически и в паспорт руками не записывается;
- статусы relation-строк ограничены `required`, `informational`, `planned`.

Следующий implementable шаг родительской цепочки — `TASK-2026-0024.4`.

## Стратегия проверки

### Покрывается кодом или тестами

- юнит-проверка `python3 -m unittest skills-global.task-centric-knowledge.tests.test_module_query_runtime`
- CLI-проверка `python3 -m unittest skills-global.task-centric-knowledge.tests.test_task_knowledge_cli`
- `git diff --check`
- команда проверки локализации: `bash scripts/check-docs-localization.sh`

### Остаётся на ручную проверку

- `не требуется`

## Критерии готовности

- relation-schema минимальна и однозначна;
- relation-excerpts можно безопасно использовать как сводки зависимостей в `ExecutionPacket`;
- она позволяет построить module-query без full graph-platform;
- relation-model одинаково работает для import-centric и file-centric / `1С/BSL` модулей;
- невалидные relation-строки и missing targets детектируются автоматически через warning-коды.

## Итоговый список ручных проверок

- `не требуется`

## Итог

Реализован минимально достаточный relation-layer для `Module Core`.
`module show --with relations` теперь отдаёт summary,
исходящие `depends_on`,
вычисляемый `used_by`
и статусы `ready | degraded | unavailable`.

Read-model валидирует type/status/target relation-строки,
блокирует self-edge и duplicate edge,
а отсутствие governed target поднимает как degradable warning,
не ломая весь `module show`.
Контракт text/JSON остаётся пригодным для `ExecutionPacket`
и не тянет за собой `knowledge-graph.xml`,
path-level цели
или отдельный graph DSL.
