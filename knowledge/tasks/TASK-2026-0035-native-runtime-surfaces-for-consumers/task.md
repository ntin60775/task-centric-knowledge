# Карточка задачи TASK-2026-0035

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0035` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0035` |
| Технический ключ для новых именуемых сущностей | `native-runtime-surfaces-for-consumers` |
| Краткое имя | `native-runtime-surfaces-for-consumers` |
| Человекочитаемое описание | Добавить native runtime surfaces и updateable consumer contract, чтобы потребители могли полностью уйти от `.sisyphus` |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `main` |
| Требуется SDD | `да` |
| Статус SDD | `готово` |
| Ссылка на SDD | `sdd.md` |
| Дата создания | `2026-04-24` |
| Дата обновления | `2026-04-25` |

## Цель

Расширить канонический `task-centric-knowledge` минимально достаточным native runtime contract сверх текущего query/workflow subset, чтобы потребители вроде `oh-my-openagent-fork` могли полностью вывести `.sisyphus` без внешних абсолютных путей и без раздувания upstream до чужого framework scope.

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

- определение minimal native runtime surfaces, необходимых потребителям для полной замены `.sisyphus`;
- updateable/versioned consumer contract для embedded subset и consumer-owned update-flow;
- архитектурные guards, не позволяющие превратить продукт в чужой framework;
- тесты, docs и task-local артефакты для этого contract surface;
- интеграционная валидация на paired consumer-case `oh-my-openagent-fork`.

### Не входит

- реализация downstream-миграции в самих consumer repos;
- unrelated product-polish и broad vNext-expansion;
- превращение `task-centric-knowledge` в полный orchestration/runtime framework для всех возможных use-cases.

## Контекст

- источник постановки: paired upstream task для `TASK-2026-0007` в `/home/prog7/MyWorkspace/20-Personal/PetProjects/Active/oh-my-openagent-fork`, открытый по прямому запросу пользователя;
- связанная бизнес-область: standalone task-centric OS, consumer runtime contract и updateable embedded integration;
- ограничения и зависимости: решение должно оставаться в продуктовой формуле `standalone` / `adapter`, не ломать update-governance и не требовать внешнего absolute checkout у потребителя;
- исходный наблюдаемый симптом / лог-маркер: старый paired consumer path ожидал `mixed_system`; фактический checkout уже совместим, но upstream не фиксировал canonical embedded-consumer contract, root-boundary и versioned manifest как собственный product surface;
- основной контекст сессии: `текущая задача`

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | runtime contract, consumer-facing subset, sync/update metadata, tests |
| Конфигурация / схема данных / именуемые сущности | versioned consumer contract и правила embedded consumption |
| Интерфейсы / формы / страницы | CLI/operator contract и docs для потребителей |
| Интеграции / обмены | explicit integration path с downstream consumer repos |
| Документация | `task.md`, `plan.md`, `sdd.md`, `artifacts/verification-matrix.md`, `README.md`, `references/deployment.md`, `references/consumer-runtime-v1.md` |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0035-native-runtime-surfaces-for-consumers/`
- файл плана: `plan.md`
- файл SDD: `sdd.md`
- файл verification matrix: `artifacts/verification-matrix.md`
- канонический нормативный contract или source-of-truth для доменной модели, если задача его меняет: `references/consumer-runtime-v1.md`, `README.md`, `references/deployment.md`, `knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/artifacts/v1-product-thesis.md`
- пользовательские материалы: текущий диалог и paired downstream task `TASK-2026-0007`
- связанные коммиты / PR / ветки: implementation commits `87498a9`, `be67f01`; merge commit `e9c38a8`; paired downstream closeout commit `dea3597`
- связанные операции в `knowledge/operations/`, если есть: `нет`

## Контур публикации

Delivery unit описывает конкретную поставку через ветку и публикацию.
В одном `task.md` допускается `0..N` delivery units.
`registry.md` хранит только задачи и подзадачи, поэтому delivery units в него не добавляются.

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `DU-01` | Локальная поставка `consumer-runtime-v1` и root-boundary diagnostics | `main` | `main` | `none` | `none` | `merged` | `—` | `e9c38a8` | `выполнено` |

Подсказка по статусам delivery unit:

- `planned` — контур поставки ещё не стартовал.
- `local` — delivery-ветка создана локально, публикации ещё нет.
- `draft` — draft PR/MR опубликован.
- `review` — публикация готова к review.
- `merged` — поставка влита, merge commit зафиксирован.
- `closed` — поставка закрыта без merge.

## Текущий этап

Задача закрыта на `main`: `consumer-runtime-v1` закреплён как upstream contract для consumers, merge commit `e9c38a8` зафиксирован в delivery unit. Добавлен single-source version/contract module, `doctor` показывает `runtime_root`, `source_root_mode` и contract metadata, embedded runtime mirror получает единый `source_root_unavailable` blocker для install-assets команд, consumer-owned `assets/` и `references/` не мешают embedded mode, а docs/tests фиксируют consumer-owned update-flow без нового upstream sync CLI.

## Стратегия проверки

### Покрывается кодом или тестами

- `python3 -m unittest discover -s tests`
- `python3 -m unittest tests.test_task_knowledge_cli -v`
- `python3 -m unittest tests.test_task_knowledge_cli tests.test_consumer_runtime_contract tests.test_python_hardening_contracts -v`
- `python3 -m compileall -q scripts tests`
- `task-knowledge --json doctor --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/task-centric-knowledge`
- `task-knowledge --json install check --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/oh-my-openagent-fork`
- `git diff --check`
- `bash scripts/check-docs-localization.sh README.md references/deployment.md references/consumer-runtime-v1.md knowledge/tasks/TASK-2026-0035-native-runtime-surfaces-for-consumers/task.md knowledge/tasks/TASK-2026-0035-native-runtime-surfaces-for-consumers/plan.md knowledge/tasks/TASK-2026-0035-native-runtime-surfaces-for-consumers/sdd.md knowledge/tasks/TASK-2026-0035-native-runtime-surfaces-for-consumers/artifacts/verification-matrix.md knowledge/tasks/registry.md`

### Остаётся на ручную проверку

- `не требуется` для upstream-задачи; downstream live user-eye smoke остаётся в consumer task и не дублируется здесь.

## Критерии готовности

- upstream определяет minimal native runtime surfaces, достаточные для полного отказа consumers от `.sisyphus`;
- contract остаётся updateable, versioned и пригодным для embedded subset consumption;
- paired consumer-case может опираться на этот contract без внешнего absolute source path;
- product scope `task-centric-knowledge` не раздувается сверх формулы `standalone task OS`;
- verification matrix покрыта фактически прогнанными проверками.

## Итоговый список ручных проверок

- `не требуется` для upstream-задачи; paired consumer task подтверждает live UX после своего consumer-owned update-flow.

## Итог

Реализация закрыта на `main`. Upstream закрепляет `consumer-runtime-v1`, stable CLI/JSON surface, manifest shape и root-boundary `project_root` / `runtime_root` / `source_root`; consumer repos сохраняют собственный update script и не получают новый mutating `task-knowledge consumer sync-*` surface. Paired downstream task `TASK-2026-0007` в `oh-my-openagent-fork` уже опирается на этот contract и держит свой live smoke как consumer-owned остаток.
