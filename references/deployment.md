# Развертывание knowledge-системы

Если перед установкой нужно понять, чем владеет ядро системы,
какой файл остаётся source-of-truth
и почему install/query/governance не конкурируют с `task.md`,
сначала прочитай `references/core-model.md`.

## Что управляет installer

Installer управляет только следующими сущностями:

- каталогом `knowledge/` в целевом проекте;
- managed-блоком между маркерами в `AGENTS.md`, если файл уже существует;
- snippet-файлом с managed-блоком, если `AGENTS.md` отсутствует.
- шаблоном `sdd.md` внутри `knowledge/tasks/_templates/` для сложных задач.

Отдельное правило для project data:

- `knowledge/tasks/registry.md` создаётся как стартовый seed-файл, но после первой установки не перезаписывается даже при `--force`.

## Что installer не делает

- не коммитит изменения;
- не открывает task-ветку сам по себе во время установки;
- не удаляет пользовательские task-данные;
- не заменяет произвольные project-specific разделы в `AGENTS.md`;
- не придумывает naming conventions для проекта;
- не переносит старые ad-hoc планы и заметки в новую структуру автоматически.

Git-жизненный цикл самой задачи начинается после установки и задаётся managed-правилами плюс вспомогательным скриптом `scripts/task_workflow.py`.
Сам installer не переопределяет `Task Core`, а только разворачивает и обновляет управляемый контур вокруг него.
До запуска git-процедур нужно определить, продолжается ли текущая задача, создаётся подзадача или открывается новая задача; правила для этого вынесены в `references/task-routing.md`.
Если обновляется старая версия skill-а, порядок перехода и git-фиксации вынесен в `references/upgrade-transition.md`.
Для проектов, которые встраивают минимальный runtime subset, consumer-facing contract описан в `references/consumer-runtime-v1.md`.

## Классификация существующей системы

Перед установкой installer определяет один из классов:

- `clean`
- `compatible`
- `partial_knowledge`
- `foreign_system`
- `mixed_system`

### Как это интерпретировать

- `clean` — можно устанавливать без дополнительных действий;
- `compatible` — проект уже близок к целевой модели, установка безопасна; сюда же относится совместимая предыдущая версия без новых managed-шаблонов, которые installer может докопировать;
- `partial_knowledge` — есть частично совместимая структура, нужно явно решить, принимать ли её как основу;
- `foreign_system` — обнаружена другая система хранения, рекомендуется миграция;
- `mixed_system` — одновременно найдены совместимые и сторонние контуры, требуется явная миграционная стратегия.

## Профили

### `generic`

Используй для большинства репозиториев, где достаточно общей терминологии:

- код;
- конфигурация;
- схема данных;
- интерфейсы;
- инфраструктурные настройки;
- тесты;
- документация.

### `1c`

Используй, когда проект явно опирается на 1С-термины:

- метаданные;
- формы;
- прикладные модули;
- интеграции 1С.

## Режимы запуска

### Проверка

```bash
python3 scripts/install_skill.py --project-root /abs/project --mode check
```

Проверяет:

- наличие обязательных файлов skill;
- существование целевого проекта;
- наличие или отсутствие `AGENTS.md`;
- какие managed-файлы уже существуют.
- наличие шаблона `sdd.md` в дистрибутиве и целевом наборе managed-файлов;
- классификацию существующей системы хранения;
- рекомендацию по следующему шагу: обычная установка, adopt или migrate.

### Установка

```bash
python3 scripts/install_skill.py --project-root /abs/project --mode install
```

Поведение:

- отсутствующие managed-файлы создаются;
- существующие managed-файлы не перезаписываются без `--force`;
- managed-блок в `AGENTS.md` вставляется или обновляется;
- если `AGENTS.md` нет, создаётся файл `AGENTS.task-centric-knowledge.<profile>.md` для ручного включения.
- шаблон `sdd.md` разворачивается вместе с остальными task-шаблонами;
- если в `AGENTS.md` обнаружены неконсистентные managed-маркеры, установка останавливается с ошибкой вместо молчаливого дублирования блока;
- если обнаружена другая система хранения, установка по умолчанию останавливается.

После установки открытие конкретной задачи нужно вести через knowledge и git синхронно.
Подробный порядок выполнения описан в `references/task-workflow.md`, validated quickstart и class-based adoption patterns — в `references/adoption.md`,
границы ядра и ownership по файлам — в `references/core-model.md`,
правила выбора между текущей задачей, подзадачей и новой задачей — в `references/task-routing.md`,
а правила upgrade-перехода старой версии на новую — в `references/upgrade-transition.md`.

Важно для самого первого task bootstrap после clean install:
если `install` и создание первых task-файлов уже сделали рабочее дерево грязным,
не нужно ожидать, что `task_workflow.py --create-branch` сам переключит ветку.
Field validation подтвердила безопасный порядок:
сначала явно создать `task/...` ветку вручную, затем вызвать helper в режиме `--register-if-missing`.

### Диагностика зависимостей

```bash
python3 scripts/install_skill.py --project-root /abs/project --mode doctor-deps
```

`doctor-deps` показывает:

- классы зависимостей `required`, `conditional`, `optional`, `not-applicable`;
- статус каждой зависимости: `ok`, `missing`, `misconfigured`, `optional`, `not-applicable`;
- границу между блокерами `core/local mode` и `publish/integration`;
- точную подсказку по исправлению.

Для `publish/integration` отдельными строками проверяются `publish_remote`, `gh`, `glab` и доступная offline-auth диагностика.
Отсутствие `gh` или `glab` не должно выглядеть как поломка всего skill-а, если `core/local mode` остаётся зелёным.

Начиная с governed legacy-upgrade rollout, install/governance payload'ы также обязаны возвращать поля:

совместимости `compatibility_epoch`, `upgrade_status`, `execution_rollout`,
а также счётчики `legacy_pending_count` и `reference_manual_count`.

Это не заменяет task-local source-of-truth и не делает installer владельцем задач;
поля нужны только для operator diagnostics и controlled rollout.

### Диагностика root-границ

В consumer-runtime сценариях нужно различать три пути:

- `project_root` — целевой consumer repo;
- `runtime_root` — каталог исполняемого runtime subset-а или установленной команды;
- `source_root` — standalone-дистрибутив с install assets.

Если доступен только embedded runtime subset, `project_root` не считается `source_root`.
Команды, которым нужны install assets, должны возвращать один blocker `source_root_unavailable`;
read-only runtime commands должны продолжать работать от `project_root`, если их subset доступен.

### План cleanup после миграции

```bash
python3 scripts/install_skill.py --project-root /abs/project --mode migrate-cleanup-plan
```

`migrate-cleanup-plan` не удаляет ничего и вместо этого:

- раскрывает абсолютные пути `safe_delete`;
- показывает `TARGETS`, `TARGET_COUNT`, `COUNT`, `plan_fingerprint` и точную confirm-команду;
- делит найденные объекты на `safe_delete`, `keep` и `manual_review`.

Auto-delete allowlist v1 ограничен только installer-generated артефактами:

- `knowledge/MIGRATION-SUGGESTION.md`, если текущая классификация уже `clean` или `compatible`;
- `AGENTS.task-centric-knowledge.<profile>.md`, если managed-блок knowledge-системы уже materialized в `AGENTS.md`.

`project data` и legacy-контуры из `FOREIGN_SYSTEM_INDICATORS` (`.sisyphus`, `doc/tasks`, `docs/tasks`, `docs/roadmap`, `docs/plans`) не попадают в auto-delete.
Даже для allowlist v1 auto-delete допустим только для обычных файлов; symlink и каталоги уходят в `manual_review`.

Field validation показала два ожидаемых паттерна:

- для `mixed_system` cleanup-plan может дать `target_count=0` и оставить legacy-контуры только в `manual_review`;
- для `compatible` cleanup-plan может ограничиться одним stale installer-generated артефактом вроде `knowledge/MIGRATION-SUGGESTION.md`.

### Подтверждённый cleanup

```bash
python3 scripts/install_skill.py --project-root /abs/project --mode migrate-cleanup-confirm --confirm-fingerprint <sha256> --yes
```

`migrate-cleanup-confirm` заново строит cleanup-plan и останавливается, если изменились:

- `TARGETS`;
- `TARGET_COUNT`;
- `COUNT`;
- confirm-команда, из которой вычислялся fingerprint.

Без `--confirm-fingerprint` или без `--yes` применение cleanup невозможно.

### Принудительное обновление

```bash
python3 scripts/install_skill.py --project-root /abs/project --mode install --force
```

Используй, если нужно обновить именно managed-шаблоны из этого дистрибутива.
`knowledge/tasks/registry.md` в этот режим не входит: он сохраняется как project data.

### Безопасное обновление старой версии

Если проект уже использует более старую совместимую версию `task-centric-knowledge`, обновление должно проходить так:

1. сначала `check`;
2. затем локальный task-scoped upgrade на чистом рабочем дереве;
3. затем проверки на отсутствие потерь project data, дубликатов managed-блока и неожиданных изменений в уже созданных задачах;
4. затем отдельный локальный commit, который и является точкой перехода версии;
5. только после этого можно продолжать следующую работу.

Детальный playbook находится в `references/upgrade-transition.md`.

После materialized upgrade-state следующий governed шаг —
explicit backfill legacy-задач через команду `task-knowledge workflow backfill --project-root /abs/project --task-dir /abs/project/knowledge/tasks/TASK-... --scope compatibility`.

Обычный `workflow sync` не должен использоваться как скрытый migration/backfill substitute.

### Режимы работы с существующей системой

```bash
python3 scripts/install_skill.py --project-root /abs/project --mode install --existing-system-mode abort
python3 scripts/install_skill.py --project-root /abs/project --mode install --existing-system-mode adopt
python3 scripts/install_skill.py --project-root /abs/project --mode install --existing-system-mode migrate
```

- `abort` — безопасный режим по умолчанию; при конфликте установка останавливается;
- `adopt` — допускает работу с частично совместимой knowledge-структурой;
- `migrate` — разрешает установку при конфликтующей старой системе и создаёт `knowledge/MIGRATION-SUGGESTION.md` с явным предложением миграции.

## Managed-маркеры

Installer управляет блоком между строками:

```text
⟦⟦BEGIN_TASK_KNOWLEDGE_SYSTEM#KB01⟧⟧
...
⟦⟦END_TASK_KNOWLEDGE_SYSTEM#KB01⟧⟧
```

Только этот блок считается управляемым.
Весь остальной текст `AGENTS.md` должен сохраняться как есть.
