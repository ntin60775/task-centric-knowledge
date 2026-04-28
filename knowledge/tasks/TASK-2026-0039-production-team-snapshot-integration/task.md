# Карточка задачи TASK-2026-0039

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0039` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0039` |
| Технический ключ для новых именуемых сущностей | `—` |
| Краткое имя | `production-team-snapshot-integration` |
| Человекочитаемое описание | `Интегрировать полезные правки из production-team snapshot после исправления blocker-ов ревью.` |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `не назначен` |
| Ветка | `main` |
| Требуется SDD | `да` |
| Статус SDD | `актуален` |
| Ссылка на SDD | `sdd.md` |
| Дата создания | `2026-04-28` |
| Дата обновления | `2026-04-28` |

## Цель

Selective-port полезных изменений из архива production-team в основной репозиторий `task-centric-knowledge`: production rollout contract, safety guards для symlink/outside-root и проверяемые тесты. Интеграция должна исправить найденные blocker-ы до merge, а не переносить snapshot wholesale.

## Границы

### Входит

- Сравнить архив `/home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge-production-team-2026-04-28.zip` с текущим `main`.
- Перенести полезные runtime-правки из snapshot только после исправления atomic preflight для unsafe targets.
- Зафиксировать production rollout contract в `README.md`, `references/deployment.md`, `references/upgrade-transition.md` и managed blocks без противоречий с реальными проверками.
- Добавить или обновить тесты на global install safety, project install safety и workflow `task_dir` boundary.
- Довести production gate до согласованного состояния: либо зелёный `ruff`/`mypy`, либо явное документированное ограничение, не противоречащее Makefile.
- Прогнать локальный verify-loop и обновить verification matrix.

### Не входит

- Wholesale-распаковка архива поверх репозитория.
- Удаление repo-only файлов, zip-context артефактов или target-only файлов live-copy.
- Обновление глобальной live-copy в `/home/prog7/.agents/skills/task-centric-knowledge` без отдельного явного шага.
- `git push`, удаление веток и cleanup вне обычного local finalize.

## Контекст

- источник постановки: пользователь попросил открыть задачу по интеграции полезных правок разработчика;
- связанная бизнес-область: production rollout и safety governance навыка `task-centric-knowledge`;
- ограничения и зависимости: текущий репозиторий чистый на момент открытия; архив является plain snapshot, не git bundle;
- исходный наблюдаемый симптом / лог-маркер: при проверке snapshot обнаружено, что symlink blocker не атомарный и `ruff` gate красный;
- основной контекст сессии: новая задача.

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | `scripts/install_global_skill.py`, `scripts/install_skill_runtime/environment.py`, `scripts/task_workflow_runtime/*`, новый helper `path_safety.py` |
| Конфигурация / схема данных / именуемые сущности | `Makefile` production targets; новых runtime/package зависимостей не ожидается |
| Интерфейсы / формы / страницы | CLI contract install/workflow helpers и machine-readable blocker statuses |
| Интеграции / обмены | Global live-copy install, project install, workflow sync/finalize/publish/backfill |
| Документация | `README.md`, `references/deployment.md`, `references/upgrade-transition.md`, managed blocks |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0039-production-team-snapshot-integration/`
- файл плана: `plan.md`
- файл SDD: `sdd.md`
- файл verification matrix: `artifacts/verification-matrix.md`
- финальное сравнение scope с архивом: `artifacts/snapshot-scope-review.md`
- пользовательские материалы: `/home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge-production-team-2026-04-28.zip`
- рабочий каталог анализа архива: `/tmp/tck-prod-review.V3x4ih`
- связанные коммиты / PR / ветки: `task/task-2026-0039-production-team-snapshot-integration`
- связанные операции в `knowledge/operations/`, если есть: `не требуется`

## Контур публикации

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | — | `—` | `—` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |

## Текущий этап

Локальный finalize выполнен: task-ветка влита в base-ветку, рабочий контекст переведён на base-ветку, `push` остаётся отдельным шагом.
## Стратегия проверки

### Покрывается кодом или тестами

- `python3 -m compileall -q scripts tests`
- `python3 -m unittest discover -s tests -v`
- `python3 -m ruff check scripts tests` как optional `check-strict`; текущий baseline красный и не входит в mandatory `check-production`.
- `python3 -m mypy scripts` как optional `check-strict`; текущая среда не содержит `mypy`.
- `git diff --check`
- `bash scripts/check-docs-localization.sh`
- Targeted tests по safety guard: global install symlink, project install symlink/outside-root, workflow `task_dir_outside_project_root`.
- Проверка `artifacts/verification-matrix.md`: каждый invariant должен иметь команду, тест или явно зафиксированный ручной остаток.

### Остаётся на ручную проверку

- `не требуется`: финальное review-сравнение scope с архивом выполнено в `artifacts/snapshot-scope-review.md`.

## Критерии готовности

- Полезные правки из snapshot перенесены selective-port-ом.
- Unsafe target обнаруживается до любых write-действий в global/project install path.
- Workflow mutators не принимают `task_dir`, который после `resolve()` выходит за пределы `project_root`.
- Production gate в Makefile, docs и tests не противоречит фактически доступным проверкам.
- Все новые пользовательские документы и изменённые user-facing строки прошли localization guard.
- Verification matrix заполнена фактическими результатами проверок.

## Итоговый список ручных проверок

- `не требуется`: финальное review-сравнение scope с архивом выполнено в `artifacts/snapshot-scope-review.md`.

## Итог

Selective-port выполнен: перенесены production rollout contract, atomic safety-preflight для global/project install и workflow `task_dir` boundary guard. Strict static checks отделены от mandatory production gate.
