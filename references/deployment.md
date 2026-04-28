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
- post-install verification contract-ом, который подтверждает полноту установленной проектной части.

Отдельное правило для project data:

- `knowledge/tasks/registry.md` создаётся как стартовый seed-файл, но после первой установки не перезаписывается даже при `--force`.
- `knowledge/modules/registry.md` создаётся как стартовый seed-файл, но после первой установки не перезаписывается даже при `--force`.

Отдельное правило для write-safety:

- installer не читает и не пишет managed-path через symlink;
- managed target, который после `resolve()` выходит за пределы `project_root`, считается blocker-ом;
- workflow-команды, которые меняют task-файлы или registry, принимают только `task_dir` внутри `project_root` после полного path resolution.

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

## Глобальная установка самого навыка

Глобальная установка навыка — отдельная поверхность, не равная установке `knowledge/`
в целевой проект. Полная установка должна обновлять сразу два user-local слоя:

- слой `live skill copy`: `~/.agents/skills/task-centric-knowledge`;
- user-site CLI layer: `~/.local/bin/task-knowledge` и `task_knowledge_local.pth`.

Штатный порядок:

Порядок команд: `make install-global-dry-run`, затем `make install-global`, затем `make verify-global-install`.

`make install-global` копирует только manifest-допущенные части дистрибутива:

- отдельные файлы: `SKILL.md`, `README.md`, `Makefile`, `pyproject.toml`;
- каталоги дистрибутива: `agents/`, `assets/`, `borrowings/`, `references/`, `scripts/`, `tests/`;
- обязательный шаблонный блок: `assets/knowledge/**`.

В live-copy не должны попадать repo-local и transient артефакты:

- repo-local файлы: `.git`, `.gitignore`, `AGENTS.md`;
- repo-local каталоги: `knowledge/`, `output/`, `.codex`;
- transient-кэши: `__pycache__/`, `*.pyc`;
- локальный артефакт: `zip_context_ignore.md`.

После overlay helper запускает wrapper-based CLI install уже из live-copy, чтобы user-facing
`task-knowledge` был связан с установленной глобальной копией, а не только с source repo или editable dev install-ом.
Symlinked manifest targets в live-copy не перезаписываются: apply/verify возвращают blocker `blocked-target-symlink` или `blocked-target-outside-root`.

Обязательные smoke-checks:

- прямой smoke: `python3 ~/.agents/skills/task-centric-knowledge/scripts/install_skill.py --project-root /abs/project --mode check --format json`;
- smoke пользовательского CLI: `task-knowledge --json doctor --project-root /abs/project --source-root ~/.agents/skills/task-centric-knowledge`.

Helper не выполняет destructive cleanup и не использует `--delete`.
Лишние target-only файлы в live-copy считаются warning и должны чиститься отдельным
delete-gate, если действительно мешают.

## Production rollout внутри команды

Командный rollout должен идти по уровням в фиксированном порядке. Нельзя обновлять проектную установку, пока не прошёл source gate и verify глобальной live-copy.

### 1. Проверка source repo

Из source repo skill-а:

```bash
make check
```

`make check` выполняет compileall и весь unittest suite. Strict static checks вынесены отдельно:

```bash
make check-strict
```

`make check-strict` требует dev-зависимостей `ruff` и `mypy`. Если эти инструменты не установлены или baseline ещё красный, strict gate фиксируется как отдельный blocker dev hygiene, но не подменяет mandatory production gate.

### 2. Проверка global deploy

Из того же source repo:

```bash
make install-global-dry-run
make install-global
make verify-global-install
```

Ожидаемое состояние после gate:

- manifest files в `~/.agents/skills/task-centric-knowledge` совпадают с source repo;
- user-site wrapper `~/.local/bin/task-knowledge` указывает на live-copy;
- `task_knowledge_local.pth` указывает на `~/.agents/skills/task-centric-knowledge/scripts`;
- direct live smoke и user-facing CLI smoke возвращают `ok=True`.

Если verify показывает extra target files, это не повод автоматически удалять их. Cleanup live-copy выполняется отдельным ручным delete-gate после проверки, что файл не нужен.

### 3. Проверка project deploy

В каждом целевом проекте обновление managed-контура выполняется отдельно:

```bash
git status --short
git switch -c task/<task-id>-upgrade-task-knowledge

task-knowledge install check \
  --project-root /abs/project \
  --source-root ~/.agents/skills/task-centric-knowledge \
  --profile generic

task-knowledge install apply \
  --project-root /abs/project \
  --source-root ~/.agents/skills/task-centric-knowledge \
  --profile generic \
  --force

task-knowledge install verify-project \
  --project-root /abs/project \
  --source-root ~/.agents/skills/task-centric-knowledge \
  --profile generic \
  --force

task-knowledge doctor --project-root /abs/project --source-root ~/.agents/skills/task-centric-knowledge
git status --short
git diff -- AGENTS.md knowledge
```

Переход версии фиксируется отдельным commit-ом:

```bash
git add AGENTS.md knowledge
git commit -m "TASK-ID: обновить managed-контур task-centric-knowledge"
```

Если в проекте используется профиль `1c`, в командах указывается `--profile 1c`, а diff должен показывать обновление соответствующего managed-блока.

### Rollback и стоп-условия

Если global deploy gate не прошёл, проектные установки не обновляются. Если project deploy gate не прошёл, transition commit не создаётся.

Блокеры, требующие ручного исправления перед повторным запуском:

- `symlink` в managed path (`AGENTS.md`, `knowledge/**`, generated snippet, migration note);
- `task_dir_outside_project_root` в workflow-командах;
- stale managed-файл после `install apply --force`;
- неконсистентные managed-маркеры в `AGENTS.md`;
- отличие user-site wrapper или `.pth` от live-copy в `verify-global-install`.

## Обновление локальных установок в проектах

Локальная проектная установка — это managed `knowledge/` и managed-блок/snippet в целевом репозитории. Она не обновляет сам skill и не должна использовать source repo напрямую, если уже есть verified live-copy.

Штатная процедура обновления проекта:

1. Обновить и проверить глобальную live-copy через `make install-global` и `make verify-global-install`.
2. На чистом рабочем дереве проекта открыть отдельную task-ветку для перехода версии.
3. Выполнить `task-knowledge install check` с `--source-root ~/.agents/skills/task-centric-knowledge`.
4. Выполнить `task-knowledge install apply --force`.
5. Выполнить `task-knowledge install verify-project --force`.
6. Проверить diff только по ожидаемым managed-шаблонам и managed-блоку.
7. Зафиксировать transition commit отдельно от продуктовых изменений.

Что не должно изменяться при локальном обновлении:

- уже созданные task-каталоги;
- `task.md`, `plan.md`, `sdd.md` существующих задач;
- `knowledge/tasks/registry.md` как project data;
- `knowledge/modules/registry.md` как project data;
- project-specific разделы вне managed-блока `AGENTS.md`.

Если installer создаёт `AGENTS.task-centric-knowledge.<profile>.md`, это означает, что `AGENTS.md` отсутствует. Snippet нужно вручную включить в проектный `AGENTS.md` или явно оставить как staged artifact по правилам проекта.

Если локальный проект содержит symlink вместо managed file/directory, installer останавливается. Допустимые действия: заменить symlink обычным файлом/каталогом внутри проекта, удалить небезопасный target вручную, либо изменить project layout. Перезапускать installer с ожиданием, что он пройдёт по ссылке, запрещено.

Для workflow-команд после обновления действует та же root-политика:

```bash
task-knowledge workflow sync --project-root /abs/project --task-dir /abs/project/knowledge/tasks/TASK-...
```

`--task-dir` может быть абсолютным или относительным, но после `resolve()` обязан оставаться внутри `/abs/project`. Symlinked task directory, ведущий наружу, блокируется до любых изменений `task.md` или `registry.md`.

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
python3 scripts/install_skill.py --project-root /abs/project --mode install --force  # полное обновление managed-шаблонов
```

Поведение:

- отсутствующие managed-файлы создаются;
- существующие managed-файлы не перезаписываются без `--force`;
- managed-блок в `AGENTS.md` вставляется или обновляется;
- если `AGENTS.md` нет, создаётся файл `AGENTS.task-centric-knowledge.<profile>.md` для ручного включения.
- шаблон `sdd.md` разворачивается вместе с остальными task-шаблонами;
- после записи выполняется post-install verification: все managed-файлы должны существовать, managed-блок или snippet должен соответствовать profile, а force-updatable шаблоны после `--force` должны совпасть с source assets;
- если в `AGENTS.md` обнаружены неконсистентные managed-маркеры, установка останавливается с ошибкой вместо молчаливого дублирования блока;
- если обнаружена другая система хранения, установка по умолчанию останавливается.

`install` возвращает `ok=True` только после успешной post-install verification.
Project data не сравнивается с source-шаблоном по содержимому: `registry.md` файлы проверяются на наличие и остаются данными целевого проекта.

### Read-only проверка проектной установки

```
python3 scripts/install_skill.py --project-root /abs/project --mode verify-project  # read-only аудит установленного проекта
python3 scripts/install_skill.py --project-root /abs/project --mode verify-project --force  # проверка полного обновления
```

`verify-project` повторяет post-install verification без записи в целевой проект.
Обычный режим допускает warning для managed-шаблонов, которые отличаются от текущего дистрибутива.
Режим `--force` трактует такое отличие как ошибку, потому что полный upgrade должен привести force-updatable шаблоны к source assets.

Unified CLI использует ту же семантику:

```
task-knowledge install verify-project --project-root /abs/project --force  # read-only проверка результата
```

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
python3 scripts/install_skill.py --project-root /abs/project --mode verify-project --force  # проверка полного обновления
```

Используй, если нужно обновить именно managed-шаблоны из этого дистрибутива.
`knowledge/tasks/registry.md` в этот режим не входит: он сохраняется как project data.
После `install --force` повторный `verify-project --force` должен быть зелёным; если он возвращает stale managed-файл, upgrade считается неполным.

### Безопасное обновление старой версии

Если проект уже использует более старую совместимую версию `task-centric-knowledge`, обновление должно проходить так:

1. сначала `check`;
2. затем локальный task-scoped upgrade на чистом рабочем дереве через `install --force`;
3. затем `verify-project --force`, `doctor-deps` и проверки на отсутствие потерь project data, дубликатов managed-блока и неожиданных изменений в уже созданных задачах;
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
