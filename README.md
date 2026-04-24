# CLI для task-centric-knowledge

`task-knowledge` собирает в одну команду четыре существующих контура навыка:

- установку и upgrade-governance;
- read-only операторскую отчётность по knowledge-задачам;
- read-only query layer по `Module Core`;
- workflow / publish helper для task-веток, compatibility-backfill и delivery units.

## Установка

Из каталога skill-а:

```bash
make install-local
```

`make install-local` создаёт thin wrapper:

```bash
~/.local/bin/task-knowledge
```

Он запускает repo-local `scripts/task_knowledge_cli.py`, поэтому не требует сети, `pip install` или отдельного виртуального окружения.

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
task-knowledge install apply --project-root /abs/project
task-knowledge install doctor-deps --project-root /abs/project
task-knowledge install cleanup-plan --project-root /abs/project --existing-system-mode migrate
```

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
- Для `doctor` JSON включает диагностические поля окружения, `source_root_valid` / `source_root_mode` и вложенные payload'ы `install_check` и `dependency_check`.
- Для `install`, `task`, `module`, `file` и `workflow` JSON сохраняет payload существующих runtime-слоёв без потери деталей.
- Ошибки в `--json` не должны требовать парсинга текста и не должны содержать секреты.


## Владение standalone-репозиторием

Этот репозиторий является каноническим домом `task-centric-knowledge`.
Потребители не должны копировать реализацию в свои `skills-global/`;
ожидаемый интерфейс интеграции — команда `task-knowledge --project-root /abs/project`.

Product history хранится в `knowledge/tasks/` и импортирована из исходного `ai-agents-rules` только для задач, которые описывают развитие самого `task-centric-knowledge`.
