# CLI для task-centric-knowledge

`task-knowledge` собирает в одну команду четыре существующих контура навыка:

- установку и upgrade-governance;
- read-only операторскую отчётность по knowledge-задачам;
- read-only query layer по `Module Core`;
- workflow / publish helper для task-веток, compatibility-backfill и delivery units.
- versioned consumer runtime contract для проектов, которые встраивают минимальный runtime subset.

## Поверхности установки

У `task-centric-knowledge` есть четыре разные поверхности. Их нельзя подменять друг другом:

| Поверхность | Назначение | Команда |
|-------------|------------|---------|
| Source repo | Канонический standalone-дистрибутив для разработки и релиза. | `git status`, `python3 -m unittest discover -s tests -v` |
| Live skill copy | Глобальная копия навыка для Codex skills. | `make install-global` |
| User-site CLI layer | Команда `task-knowledge` и Python import path. | `make install-local` |
| Target project knowledge | Managed `knowledge/` и блок `AGENTS.md` в целевом проекте. | `task-knowledge install apply --project-root /abs/project --force` |

## Глобальная установка навыка

Полная глобальная установка должна обновлять live skill copy и CLI layer вместе:

Порядок команд: `make install-global-dry-run`, затем `make install-global`, затем `make verify-global-install`.

`make install-global` выполняет source-controlled overlay из текущего source repo в
`~/.agents/skills/task-centric-knowledge`, затем запускает `make install-local` уже из live-copy.
После этого обязательны две проверки:

- прямой live smoke через `~/.agents/skills/task-centric-knowledge/scripts/install_skill.py`;
- user-facing smoke через установленный `task-knowledge`.

Helper не удаляет target-only файлы. Если verify показывает лишние файлы в live-copy,
это отдельный cleanup-контур и он требует обычного delete-gate.

## Установка CLI layer

Из каталога skill-а:

```bash
make install-local
```

`make install-local` создаёт thin wrapper и `.pth` только для user-site CLI layer:

```bash
~/.local/bin/task-knowledge
```

Команда запускает `scripts/task_knowledge_cli.py` из того каталога, где был выполнен `make install-local`.
Поэтому зелёный `task-knowledge --help` сам по себе не доказывает, что live skill copy в
`~/.agents/skills/task-centric-knowledge` полная и свежая. Для этого использовать `make verify-global-install`.

После этого команда должна быть доступна из любого каталога:

```bash
command -v task-knowledge
task-knowledge --help
```

## Базовые команды

Проверить окружение и целевой проект:

```bash
task-knowledge doctor --project-root /abs/project
task-knowledge --json doctor --project-root /abs/project
```

Проверить или установить knowledge-систему:

```bash
task-knowledge install check --project-root /abs/project
task-knowledge install apply --project-root /abs/project --force  # полное обновление managed-шаблонов
task-knowledge install verify-project --project-root /abs/project --force  # read-only проверка результата
task-knowledge install doctor-deps --project-root /abs/project
task-knowledge install cleanup-plan --project-root /abs/project --existing-system-mode migrate
```

`install apply` всегда выполняет post-install verification перед успешным `ok=True`.
`install verify-project` повторяет ту же проверку read-only и нужен для отдельного аудита уже установленного проекта.
Для полного обновления managed-шаблонов используй `--force`: шаблоны должны совпасть с дистрибутивом,
а `knowledge/tasks/registry.md` и `knowledge/modules/registry.md` всё равно остаются project data и не перезаписываются.

Получить read-only отчётность:

```bash
task-knowledge task status --project-root /abs/project
task-knowledge task current --project-root /abs/project
task-knowledge task show --project-root /abs/project current
```

Получить read-only навигацию по `Module Core` можно через новые
module/file-подкоманды unified CLI.

На текущем rollout-этапе `module` / `file` работают в partial-mode:
если `module.md`, relation layer или file-local contracts ещё не внедрены,
команды возвращают стабильный JSON/text shape и явные warning'и,
опираясь как минимум на `knowledge/modules/*/verification.md`.
Если passport-layer уже внедрён,
`module show` поднимает shared/public truth из `module.md`,
а `knowledge/modules/registry.md` используется как навигационный cache
и проверяется на drift относительно канонического паспорта.
Если в паспорте подключён `knowledge/modules/<MODULE-ID>-<slug>/file-local-policy.md`,
`file show` читает private/local truth только для явных hot spots из этого policy-файла:
без policy возвращается warning `file_contract_unavailable`,
вне hot-spot списка — warning `file_not_governed_hotspot`,
а для multi-owner файла без `--module` — warning `multi_owner_file_contract_ambiguous`.
JSON-поля `contract_markers` и `blocks` всегда остаются стабильными,
а text surface можно расширить через `file show --contracts --blocks`.
Для relation-layer v1 `module show --with relations` читает исходящие `depends_on`
из `module.md`,
строит derived `used_by`,
возвращает relation-summary для `ExecutionPacket`
и помечает слой как `degraded`,
если target не найден
или relation row не проходит валидацию.
`registry.md` relation-сводку не хранит.

Синхронизировать task workflow:

```bash
task-knowledge workflow sync \
  --project-root /abs/project \
  --task-dir knowledge/tasks/TASK-2026-0001-zadacha \
  --create-branch \
  --register-if-missing
```

Для governed compatibility-backfill legacy-задачи используй примерную команду `task-knowledge workflow backfill --project-root /abs/project --task-dir knowledge/tasks/TASK-2026-0001-zadacha --scope compatibility`.

Завершить локальный task lifecycle без `push` можно через local finalize:

- Команда: `task-knowledge workflow finalize --project-root /abs/project --task-dir knowledge/tasks/TASK-2026-0001-zadacha --base-branch main`

`workflow finalize` работает только в local-only режиме:

- при безопасном task-контексте он делает task-scoped commit, fast-forward merge в base-ветку и checkout base-ветки;
- при блокере он не мутирует git-состояние и возвращает явный blocker-report с причинами и следующими действиями;
- `push`, PR/MR и cleanup веток остаются отдельными шагами.

## Политика JSON

- Глобальный флаг `--json` включает стабильный машиночитаемый вывод.
- В JSON верхний уровень всегда содержит `ok` и `command` либо режим install/runtime, чтобы внешний агент мог ветвить обработку без парсинга текста.
- Для `doctor` JSON включает диагностические поля окружения, `runtime_root`, `source_root_valid` / `source_root_mode` и вложенные payload'ы `install_check` и `dependency_check`.
- Для `install`, `task`, `module`, `file` и `workflow` JSON сохраняет payload существующих runtime-слоёв без потери деталей.
- Ошибки в `--json` не должны требовать парсинга текста и не должны содержать секреты.

## Контракт потребительского runtime

Consumer repos могут использовать `task-knowledge` двумя способами:

- установленная команда `task-knowledge task status --project-root /abs/project`;
- consumer-owned embedded subset с явным manifest-ом и собственным update script-ом.

Контракт `consumer-runtime-v1` описан в `references/consumer-runtime-v1.md`.
Он фиксирует стабильный CLI/JSON surface, manifest-поля embedded subset-а и границу `project_root` / `runtime_root` / `source_root`.
`task-centric-knowledge` не добавляет upstream-команду, которая сама обновляет файлы consumer repo: обновление embedded subset-а остаётся обязанностью потребителя.


## Владение standalone-репозиторием

Этот репозиторий является каноническим домом `task-centric-knowledge`.
Потребители не должны копировать реализацию в свои `skills-global/`;
ожидаемый интерфейс интеграции — CLI `task-knowledge ... --project-root /abs/project`.

Product history хранится в `knowledge/tasks/` и импортирована из исходного `ai-agents-rules` только для задач, которые описывают развитие самого `task-centric-knowledge`.
