# План задачи TASK-2026-0037

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0037` |
| Parent ID | `—` |
| Версия плана | `1` |
| Связь с SDD | `sdd.md`, этапы 1-3 |
| Дата обновления | `2026-04-28` |

## Цель

Закрепить полную глобальную установку навыка как воспроизводимую процедуру: source repo обновляет live skill copy, затем CLI layer, затем выполняет прямую проверку обоих слоёв.

## Границы

### Входит

- Helper/target для global install.
- Verify-only режим для уже установленной live-copy.
- Regression-тесты на полноту deploy bundle.
- Документация install-поверхностей.

### Не входит

- Сетевой publish.
- Destructive cleanup live-копии.
- Изменение install semantics для target project `knowledge/`.

## Планируемые изменения

### Код

- Добавить helper в `scripts/` для global install/verify live skill copy.
- Добавить Makefile targets для dry-run/apply/verify.
- Добавить tests на bundle manifest, missing `assets/knowledge/**`, CLI/live split-brain.

### Конфигурация / схема данных / именуемые сущности

- Новых runtime/package зависимостей нет.
- Добавляется именованный deploy scope live-copy.

### Документация

- Обновить `README.md`, `SKILL.md`, `references/deployment.md`.

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- Новый helper может импортировать `install_skill_runtime.models` для единого источника списка обязательных ресурсов.
- Существующий install runtime не должен импортировать deploy-live helper.

### Границы, которые должны остаться изолированными

- `task-knowledge install apply` остаётся установкой knowledge-системы в target project.
- `make install-local` остаётся user-site CLI layer install.
- Global live-copy deploy остаётся отдельной явной поверхностью.

### Критический функционал

- Live-copy после установки содержит `assets/knowledge/**` и все required source resources.
- Проверка не может быть зелёной, если live-copy неполная.

### Основной сценарий

- Оператор запускает global install из source repo.
- Helper показывает dry-run или применяет overlay.
- Helper обновляет live-copy, обновляет CLI layer и выполняет direct-live + user-facing smoke checks.

### Исходный наблюдаемый симптом

- Live-copy была неполной: отсутствовал блок `assets/knowledge/**`, при этом CLI работал из source repo и маскировал дефект.

## Риски и зависимости

- Нельзя использовать destructive delete без отдельного delete-gate.
- Нельзя считать `task-knowledge --help` достаточной проверкой live-copy.
- Нельзя тащить repo-local артефакты `.git`, `AGENTS.md`, `knowledge/`, `output/`, `.codex`, `__pycache__`, `*.pyc`.

## Связь с SDD

- Этап 1: source-controlled deploy helper и manifest.
- Этап 2: tests и verify-only режим.
- Этап 3: документация и локальная установка.
- Матрица покрытия: `artifacts/verification-matrix.md`.

## Проверки

### Что можно проверить кодом или тестами

- `python3 -m unittest discover -s tests -v`
- `python3 -m compileall -q scripts tests`
- `bash scripts/check-docs-localization.sh`
- `git diff --check`
- direct-live smoke через `python3 /home/prog7/.agents/skills/task-centric-knowledge/scripts/install_skill.py ... --mode check --format json`
- user-facing smoke через `task-knowledge --json doctor --project-root ...`

### Что остаётся на ручную проверку

- Проверка видимости обновлённой live-копии в новой Codex-сессии, если host кеширует skill list.

## Шаги

- [x] Этап 1: добавить global install helper, manifest и Makefile targets.
- [x] Этап 2: добавить regression-тесты и verify-only проверки.
- [x] Этап 3: обновить документацию и выполнить локальную установку/верификацию.
- [x] Этап 4: прогнать полный verify loop, обновить матрицу и закрыть задачу.

## Критерии завершения

- Full global install выполняется одной штатной командой.
- Missing/stale live-copy class покрыт тестами.
- Документация не смешивает `install-local`, `install apply` и global live-copy deploy.
- Проверки пройдены, задача зафиксирована коммитом.
