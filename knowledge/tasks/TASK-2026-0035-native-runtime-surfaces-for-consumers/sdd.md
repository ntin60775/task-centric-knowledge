# SDD по задаче TASK-2026-0035

## Паспорт SDD

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0035` |
| Статус | `готово` |
| Версия | `2` |
| Дата обновления | `2026-04-24` |

## 0. Инварианты и verification matrix

### Полный invariant set

- `INV-01`: `task-centric-knowledge` предоставляет minimal native runtime contract сверх текущего query/workflow subset, достаточный для consumer repos, которым нужно полностью уйти от `.sisyphus`.
- `INV-02`: новый consumer contract остаётся updateable, versioned и пригодным для embedded consumption без внешнего absolute checkout.
- `INV-03`: решение не раздувает продукт за пределы `standalone task OS` и не превращает его в чужой orchestration framework.
- `INV-04`: paired consumer-case `oh-my-openagent-fork` может опираться на этот contract как на канонический upstream путь к полному отказу от `.sisyphus`.

### Связанные артефакты проверки

- `artifacts/verification-matrix.md`

## 1. Проблема и цель

### Проблема

Сегодня `task-centric-knowledge` уже является каноническим standalone repo для managed task OS и даёт consumer-ам install/query/workflow surfaces. Paired consumer уже выбрал свой product runtime root и consumer-owned update script, но upstream не фиксировал это как поддерживаемый embedded-consumer contract. Без такого contract-а consumers вынуждены опираться на ad-hoc manifest shape, runtime subset и неявную границу между project root, runtime root и source root.

### Цель

Добавить в канонический repo минимально достаточный explicit consumer surface `consumer-runtime-v1`, который позволит paired consumer-ам обновлять embedded subset своим механизмом, не требуя внешнего absolute checkout, не ломая update-governance и не раздувая scope продукта.

## 2. Архитектура и границы

Целевая форма решения:

`standalone task-centric knowledge OS` + `minimal native runtime surfaces for consumers`

а не:

`full orchestration framework`

### Допустимые и недопустимые связи

#### Допустимые связи

- consumer-facing runtime contract может расширить текущий subset, если это минимально необходимо;
- paired downstream use-case может использоваться как field-validation target;
- embedded subset и consumer-owned update-flow могут быть формализованы как канонический путь потребления.

#### Недопустимые связи

- нельзя требовать от consumer repos внешний абсолютный source path на checkout upstream;
- нельзя вводить disguised replacement для `.sisyphus` без нормализации модели;
- нельзя добавлять новый upstream `task-knowledge consumer sync-*` CLI в этой задаче;
- нельзя решать задачу за счёт broad framework expansion или чужой product thesis.

### Новые зависимости и их обоснование

- runtime/package зависимости: `нет`
- новая зависимость уровня контракта: `да`, explicit consumer runtime contract нужен для paired downstream migration

### Наблюдаемые сигналы и диагностические маркеры

- старый paired path `/home/prog7/MyWorkspace/20-Personal/PetProjects/Active/oh-my-openagent-fork` отсутствует; фактический checkout находится в `/home/prog7/РабочееПространство/projects/PetProjects/oh-my-openagent-fork`;
- фактический paired checkout уже проходит strict install check как `compatible`, но upstream должен закрепить `consumer-runtime-v1`, manifest shape и root-boundary для повторяемости;
- review-маркер 3.1: `task status` в archive/zip срезе без `.git` должен возвращать JSON warning, а не traceback.
- review-маркер 3.2: `doctor` должен явно различать project root consumer-а и standalone source root skill-а, не требуя source-файлы skill-а от project-local mirror.

## 3. Изменения данных / схемы / metadata

- потребуется канонический consumer-facing runtime contract и versioning metadata для embedded subset;
- точная форма нового contract surface должна быть выбрана так, чтобы не дублировать legacy semantics `.sisyphus` один в один;
- install/upgrade governance и project-data safety должны остаться неизменными по смыслу.

## 4. Новые сущности и интерфейсы

- `consumer-runtime-v1` как versioned embedded-consumer surface;
- минимальная форма manifest: `integration_contract`, `pinned_commit`, `included_paths`, `consumer_runtime_root`, `consumer_entrypoint`;
- диагностика границы корней: `project_root`, `runtime_root`, `source_root`, `source_root_mode`;
- explicit docs для потребителей, как использовать этот surface без ad-hoc копирования репозитория и без upstream-owned sync CLI.

## 5. Изменения в существующих компонентах

- `README.md`, `references/deployment.md`, `references/consumer-runtime-v1.md`: описать consumer contract и consumer-owned update-flow;
- runtime/query/workflow glue и tests: расширить только минимально для root-boundary diagnostics и contract constants;
- knowledge/task docs этого repo: связать paired downstream use-case и architectural guard against scope creep.

## 6. Этапы реализации и проверки

### Этап 1: Freeze consumer gap и scope guard

- зафиксировать, каких runtime surfaces не хватает paired consumer-case;
- явно отрезать всё, что уводит продукт за пределы standalone формулы.
- Проверка: `task-knowledge --json install check --project-root /home/prog7/РабочееПространство/projects/PetProjects/oh-my-openagent-fork`
- Аудит: `SDD_AUDIT`

### Этап 2: Native consumer contract и versioning

- определить minimal native runtime contract;
- описать versioned/updateable embedded-consumer surface.
- Проверка: `python3 -m unittest tests.test_task_knowledge_cli tests.test_consumer_runtime_contract tests.test_python_hardening_contracts -v`; `task-knowledge --json doctor --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge`
- Аудит: `IMPLEMENTATION_AUDIT`

### Этап 3: Runtime glue, docs и paired applicability

- materialize-ить contract в коде/docs/tests;
- доказать пригодность для paired downstream case без реализации downstream-миграции здесь.
- Проверка: `python3 -m unittest discover -s tests`; `python3 -m compileall -q scripts tests`; `git diff --check`
- Аудит: `IMPLEMENTATION_AUDIT`

### Этап 4: Integration verdict

- собрать единый verdict по paired downstream applicability и scope guard;
- обновить verification matrix и task-local docs.
- Проверка: `task-knowledge --json install check --project-root /home/prog7/РабочееПространство/projects/PetProjects/oh-my-openagent-fork`; `bash scripts/check-docs-localization.sh README.md references/deployment.md references/consumer-runtime-v1.md knowledge/tasks/TASK-2026-0035-native-runtime-surfaces-for-consumers/task.md knowledge/tasks/TASK-2026-0035-native-runtime-surfaces-for-consumers/plan.md knowledge/tasks/TASK-2026-0035-native-runtime-surfaces-for-consumers/sdd.md knowledge/tasks/TASK-2026-0035-native-runtime-surfaces-for-consumers/artifacts/verification-matrix.md knowledge/tasks/registry.md`
- Аудит: `INTEGRATION_AUDIT`

## 7. Критерии приёмки

1. Upstream определяет minimal native runtime contract для consumer repos, которым нужно убрать `.sisyphus`.
2. Contract пригоден для versioned/updateable embedded consumption.
3. Paired downstream case может использовать этот contract без внешнего absolute checkout upstream.
4. Решение не выходит за рамки standalone thesis `task-centric-knowledge`.

## 8. Стоп-критерии

1. Для решения требуется broad framework expansion, противоречащий standalone thesis.
2. Новый contract фактически лишь переименовывает `.sisyphus` без нормализации модели.
3. Consumer applicability нельзя доказать без ad-hoc локальных обходов или внешнего absolute source path.

## Связь с остальными файлами задачи

- `task.md` остаётся источником истины по статусу и границам задачи;
- `plan.md` хранит исполнимую последовательность этапов;
- `artifacts/verification-matrix.md` хранит доказательную связку `инвариант -> сценарий -> проверка -> статус`.
