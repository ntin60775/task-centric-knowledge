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
| Статус | `готова к работе` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `task/task-2026-0035-native-runtime-surfaces-for-consumers` |
| Требуется SDD | `да` |
| Статус SDD | `готово` |
| Ссылка на SDD | `sdd.md` |
| Дата создания | `2026-04-24` |
| Дата обновления | `2026-04-24` |

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
- updateable/versioned consumer contract для embedded subset и sync-flow;
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
- исходный наблюдаемый симптом / лог-маркер: consumer `oh-my-openagent-fork` остаётся `mixed_system`, потому что текущий upstream даёт query/workflow runtime, но не покрывает все live use-cases `.sisyphus`;
- основной контекст сессии: `текущая задача`

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | runtime contract, consumer-facing subset, sync/update metadata, tests |
| Конфигурация / схема данных / именуемые сущности | versioned consumer contract и правила embedded consumption |
| Интерфейсы / формы / страницы | CLI/operator contract и docs для потребителей |
| Интеграции / обмены | explicit integration path с downstream consumer repos |
| Документация | `task.md`, `plan.md`, `sdd.md`, `artifacts/verification-matrix.md`, update/deployment references |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0035-native-runtime-surfaces-for-consumers/`
- файл плана: `plan.md`
- файл SDD: `sdd.md`
- файл verification matrix: `artifacts/verification-matrix.md`
- канонический нормативный contract или source-of-truth для доменной модели, если задача его меняет: `README.md`, `references/deployment.md`, `knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/artifacts/v1-product-thesis.md`
- пользовательские материалы: текущий диалог и paired downstream task `TASK-2026-0007`
- связанные коммиты / PR / ветки: `task/task-2026-0035-native-runtime-surfaces-for-consumers`; paired downstream branch `task/task-2026-0007-full-sisyphus-retirement`
- связанные операции в `knowledge/operations/`, если есть: `нет`

## Контур публикации

Delivery unit описывает конкретную поставку через ветку и публикацию.
В одном `task.md` допускается `0..N` delivery units.
`registry.md` хранит только задачи и подзадачи, поэтому delivery units в него не добавляются.

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | Контур не стартовал; сначала нужен freeze consumer contract | `task/task-2026-0035-native-runtime-surfaces-for-consumers` | `main` | `github` | `pr` | `planned` | `—` | `—` | `не требуется` |

Подсказка по статусам delivery unit:

- `planned` — контур поставки ещё не стартовал.
- `local` — delivery-ветка создана локально, публикации ещё нет.
- `draft` — draft PR/MR опубликован.
- `review` — публикация готова к review.
- `merged` — поставка влита, merge commit зафиксирован.
- `closed` — поставка закрыта без merge.

## Текущий этап

Задача открыта как paired upstream task. Следующий практический шаг — зафиксировать минимальный native runtime contract для consumer repos и связать его с downstream use-case из `oh-my-openagent-fork`, не переходя границу `standalone task OS`.

## Стратегия проверки

### Покрывается кодом или тестами

- `python3 -m unittest discover -s tests`
- `task-knowledge --json doctor --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/task-centric-knowledge`
- `task-knowledge --json install check --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/oh-my-openagent-fork`
- `git diff --check`
- `bash scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0035-native-runtime-surfaces-for-consumers/task.md knowledge/tasks/TASK-2026-0035-native-runtime-surfaces-for-consumers/plan.md knowledge/tasks/TASK-2026-0035-native-runtime-surfaces-for-consumers/sdd.md knowledge/tasks/TASK-2026-0035-native-runtime-surfaces-for-consumers/artifacts/verification-matrix.md knowledge/tasks/registry.md`

### Остаётся на ручную проверку

- downstream live user-eye smoke остаётся в consumer task и не дублируется здесь;
- архитектурный residual review по границе `standalone / adapter`, если его нельзя закрыть только автоматикой.

## Критерии готовности

- upstream определяет minimal native runtime surfaces, достаточные для полного отказа consumers от `.sisyphus`;
- contract остаётся updateable, versioned и пригодным для embedded subset consumption;
- paired consumer-case может опираться на этот contract без внешнего absolute source path;
- product scope `task-centric-knowledge` не раздувается сверх формулы `standalone task OS`;
- verification matrix покрыта фактически прогнанными проверками.

## Итоговый список ручных проверок

- paired consumer task подтверждает, что новый upstream contract действительно позволяет убрать `.sisyphus` из live runtime.
- если останется архитектурный residual между `standalone` и `adapter`, он должен быть явно закрыт отдельным verdict, а не неявным расширением scope.

## Итог

Задача только что открыта. Реализация не начиналась; upstream task существует как обязательная пара к downstream `TASK-2026-0007` и фиксирует, что дальнейшая работа должна идти через канонический updateable repo, а не через ad-hoc локальную копию в consumer.
