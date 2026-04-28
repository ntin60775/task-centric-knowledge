# План задачи TASK-2026-0039

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0039` |
| Parent ID | `—` |
| Версия плана | `1` |
| Связь с SDD | `sdd.md` |
| Дата обновления | `2026-04-28` |

## Цель

Интегрировать полезные production-team изменения из snapshot в основной репозиторий без wholesale-распаковки и без переноса обнаруженных blocker-ов.

## Границы

### Входит

- Selective-port runtime, Makefile, docs и tests из snapshot.
- Исправление atomic safety-preflight для global/project install.
- Синхронизация production rollout wording с реальным verify contract.
- Обновление тестов и verification matrix.

### Не входит

- Push, cleanup веток, удаление файлов и обновление live-copy без отдельной команды пользователя.
- Перенос отсутствующих в snapshot repo-only изменений как удаления.

## Планируемые изменения

### Код

- Вынести общий path-boundary helper для workflow mutators.
- Добавить project-root safety checks для managed install targets.
- Добавить global install plan preflight, который блокирует apply до любых записей при `blocked-target-*`.
- При необходимости изменить install flow так, чтобы ошибки `copy_knowledge_files()` останавливали следующие mutating шаги.

### Конфигурация / схема данных / именуемые сущности

- Обновить `Makefile` targets только если их можно подтвердить локальными командами.
- Новые runtime/package зависимости: `нет`.

### Документация

- Обновить `README.md`, `references/deployment.md`, `references/upgrade-transition.md`.
- Обновить managed blocks для generic и 1c профилей.

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- Новый helper `scripts/task_workflow_runtime/path_safety.py` импортируется только из workflow mutators.
- Install runtime не должен зависеть от workflow runtime, если это не требуется для уже существующей архитектуры.

### Границы, которые должны остаться изолированными

- Global live-copy install и project install остаются разными контурами.
- Project data (`knowledge/tasks/registry.md`, `knowledge/modules/registry.md`, task-каталоги) не перезаписывается.
- CLI docs не должны обещать зелёный production gate, если dev dependencies недоступны или lint baseline красный.

### Критический функционал

- Отказ от записи через symlink и outside-root target.
- Отказ workflow mutators от внешнего `task_dir`.
- Повторяемость global install и project install verify.

### Основной сценарий

- Оператор интегрирует source changes, прогоняет source gate, обновляет global live-copy, затем project install verify в целевых проектах.

### Исходный наблюдаемый симптом

- Snapshot global apply с symlink на `SKILL.md` возвращает ошибку, но успевает записать 98 файлов.
- Snapshot project copy с symlink на managed template возвращает ошибку, но успевает записать 15 managed-файлов.
- Snapshot `python3 -m ruff check scripts tests` падает на 132 ошибках при добавленном `make lint`.

## Риски и зависимости

- Если исправить только тесты snapshot, но не atomic preflight, production safety contract останется ложноположительным.
- Если объявить lint/typecheck обязательными без зелёного baseline и dev environment, `check-production` станет невыполнимым release gate.
- Если перенести архив wholesale, можно случайно удалить repo-only файлы или внести устаревший snapshot state.

## Связь с SDD

- Этап 1 SDD: selective audit и scope lock.
- Этап 2 SDD: atomic safety implementation.
- Этап 3 SDD: production gate и documentation alignment.
- Этап 4 SDD: verification loop и task truth sync.
- Матрица покрытия: `artifacts/verification-matrix.md`.

## Проверки

### Что можно проверить кодом или тестами

- `python3 -m compileall -q scripts tests`
- `python3 -m unittest discover -s tests -v`
- `python3 -m ruff check scripts tests`
- `python3 -m mypy scripts`
- `git diff --check`
- `bash scripts/check-docs-localization.sh`
- Targeted temp-dir smoke для unsafe global/project install без записи.
- `task-knowledge --json task status --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge`

### Что остаётся на ручную проверку

- Сравнить итоговый selective-port со snapshot diff и подтвердить, что не перенесены repo-only удаления.

## Шаги

- [x] Зафиксировать точный diff snapshot и выбрать переносимые файлы/фрагменты.
- [x] Исправить atomic safety-preflight для global install.
- [x] Исправить project install flow, чтобы unsafe managed target останавливал mutating steps до записей.
- [x] Перенести workflow `task_dir` boundary helper и покрыть mutators тестами.
- [x] Синхронизировать Makefile/docs/managed blocks с фактическим production gate.
- [x] Прогнать полный verify-loop, localization guard и обновить verification matrix.
- [x] Подготовить local finalize: task-scoped commit, merge в `main`, checkout `main`, если blockers нет.

## Критерии завершения

- Все SDD invariants имеют покрытие в `artifacts/verification-matrix.md`.
- Тесты доказывают отсутствие частичной записи при unsafe target.
- Документация не расходится с CLI/Makefile поведением.
- Рабочее дерево после local finalize чистое на `main`.
