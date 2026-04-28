# SDD задачи TASK-2026-0039

## Проблема

Production-team snapshot содержит полезные изменения для rollout hardening, но прямой перенос небезопасен. В ревью snapshot обнаружены два blocker-а:

- unsafe symlink/outside-root target помечается как blocker, но apply продолжает частичные записи;
- новый production gate объявляет `ruff`/`mypy`, при этом lint baseline snapshot красный, а `mypy` может отсутствовать в окружении.

Нужно перенести полезный contract и safety-идею, но довести реализацию до проверяемого production-grade поведения.

## Границы

### Переносимые идеи

- Production rollout должен идти по слоям: source repo gate, global live-copy gate, project install gate.
- Global live-copy manifest target не должен писаться через symlink или outside-root path.
- Project managed path не должен читаться или писаться через symlink или outside-root path.
- Workflow mutators должны принимать только `task_dir`, который после `resolve()` остаётся внутри `project_root`.
- Tests должны воспроизводить failure mode через temp-dir и доказывать отсутствие повреждения external target.

### Запрещённый перенос

- Полный импорт архива целиком.
- Декларация production gate, который не проходит локально.
- Частичная запись после обнаружения unsafe target.
- Автоматический cleanup отсутствующих в snapshot repo-only файлов.

## Архитектура

### Путь глобальной установки

`scripts/install_global_skill.py` должен строить полный deployment plan до apply. Если любой item имеет `blocked-target-*`, apply должен завершиться без копирования остальных файлов и без CLI install/smoke, потому что target-root уже признан unsafe для текущего manifest.

Ожидаемый payload:

- `ok=false`;
- `plan_summary.blocked > 0`;
- `applied=[]` или только read-only диагностический список без фактических write-действий;
- `verification_issues` объясняет unsafe target.

### Путь проектной установки

`scripts/install_skill_runtime/environment.py` должен выполнять preflight по всем managed write/read targets до первого write. Если preflight находит symlink или outside-root path, install возвращает `ok=false` и не запускает:

- `copy_knowledge_files`;
- `write_migration_suggestion`;
- `ensure_repo_upgrade_state`;
- `install_agents_block`;
- любые другие mutating steps.

Если unsafe target появляется только в post-write verify, это отдельная ошибка реализации: весь target set должен быть известен до write.

### Безопасность пути workflow

Workflow mutators (`sync`, `backfill`, `publish`, `finalize`) используют единый helper:

- relative `task_dir` резолвится от `project_root`;
- absolute `task_dir` принимается только если resolved path внутри resolved `project_root`;
- symlinked task directory, ведущий наружу, блокируется до чтения/записи task truth;
- error marker должен содержать `task_dir_outside_project_root`.

### Производственный контур проверок

`Makefile`, `README.md` и `references/deployment.md` должны описывать один и тот же gate. Если `ruff` и `mypy` остаются частью `check-production`, они должны быть реально зелёными в dev environment. Если это optional strict gate, docs должны прямо отделять mandatory release checks от optional dev static checks.

## Инварианты

| ID | Инвариант |
|----|-----------|
| `INV-001` | Global install apply не выполняет ни одной записи, если deployment plan содержит unsafe manifest target. |
| `INV-002` | Project install не выполняет managed write steps, если любой managed target является symlink или выходит за `project_root`. |
| `INV-003` | External file behind symlink не меняется ни в global, ни в project install сценарии. |
| `INV-004` | Workflow mutators блокируют absolute или symlinked `task_dir`, resolving outside `project_root`, до изменения `task.md` или registry. |
| `INV-005` | Production gate в Makefile и docs не содержит невыполнимых обязательных команд. |
| `INV-006` | `knowledge/tasks/registry.md`, `knowledge/modules/registry.md` и существующие task-каталоги остаются project data. |
| `INV-007` | Managed blocks generic и 1c синхронизированы по новой safety policy. |
| `INV-008` | Все новые пользовательские Markdown-строки проходят localization guard. |

## Критерии приёмки

- Unsafe global manifest target останавливает apply до записи других manifest files.
- Unsafe project managed target останавливает install до записи managed-файлов, migration note, upgrade-state и AGENTS block.
- Workflow `sync`, `backfill`, `publish`, `finalize` имеют единое path-safety поведение.
- `check-production` либо проходит, либо переопределён как strict/dev gate с честным mandatory gate.
- Unit tests покрывают оба найденных blocker-а и новый workflow boundary.
- Документы, Makefile, tests и runtime совпадают по формулировкам и фактическому поведению.

## Стратегия проверки

- Unit tests на temp-dir scenarios для global/project symlink targets.
- Unit tests на workflow outside-root task dirs.
- Полный набор unit-тестов.
- Компиляция Python-файлов через `compileall`.
- Ruff/mypy по решению production gate.
- Localization guard для Markdown/user-facing changes.
- Manual final comparison с archive diff.

## Запрещённые действия

- Не применять архив как overlay поверх repo.
- Не использовать `git clean` или `rm` для отсутствующих в snapshot файлов.
- Не менять installed live-copy без отдельной команды пользователя.
- Не закрывать задачу при красной verification matrix.
