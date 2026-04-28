# SDD по задаче TASK-2026-0038

## Паспорт SDD

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0038` |
| Статус | `принят` |
| Версия | `1` |
| Дата обновления | `2026-04-28` |

## 0. Инварианты и verification matrix

### Полный invariant set

- `INV-01`: `install apply` выполняет post-install verification перед `ok=True`.
- `INV-02`: все managed target files из manifest существуют после установки.
- `INV-03`: force-updatable шаблоны при `--force` совпадают с source assets.
- `INV-04`: project data (`registry.md`) сохраняется и не перезаписывается даже при `--force`.
- `INV-05`: managed `AGENTS.md` block или snippet существует, валиден и соответствует выбранному profile.
- `INV-06`: verify-only режим не мутирует target project.
- `INV-07`: cleanup project artifacts не выполняется внутри install/apply/verify.
- `INV-08`: docs разделяют project install flow и global skill install flow.

### Связанные артефакты проверки

- `artifacts/verification-matrix.md` — матрица `инвариант -> сценарий нарушения -> проверка/команда -> статус покрытия`.

## 1. Проблема и цель

### Проблема

Project install/update flow уже умеет копировать managed resources и сохранять project data, но полнота результата не была выделена как отдельный проверяемый post-apply contract. Оператор мог получить успешную команду и всё равно должен был помнить дополнительный набор проверок.

### Цель

После реализации `install apply` должен возвращать `ok=True` только если post-install verification подтверждает полный project knowledge contour. Для уже установленных проектов должен быть read-only режим `verify-project`.

## 2. Архитектура и границы

Изменение остаётся внутри install runtime:

- source repo / live skill copy остаются внешними source roots;
- target project получает только `knowledge/` и managed `AGENTS.md`/snippet;
- cleanup остаётся отдельным `cleanup-plan` / `cleanup-confirm`;
- publish остаётся вне install/apply.

### Допустимые и недопустимые связи

- Допустимо: `install()` вызывает `verify_project_install()` после записи.
- Допустимо: CLI facade добавляет режим `verify-project`.
- Запрещено: verifier удаляет или переписывает файлы.
- Запрещено: project install пишет в global live-copy.

### Новые зависимости и их обоснование

- `нет`

### Наблюдаемые сигналы и диагностические маркеры

- missing managed file: `project_verify` со статусом `error`.
- stale force-updatable file после `--force`: `project_verify` со статусом `error`.
- сохранённый registry data: `project_verify` со статусом `ok`.
- invalid managed block: `project_verify` со статусом `error`.

## 3. Изменения данных / схемы / metadata

Новых persisted схем нет. В JSON payload install/check добавляются результаты `project_verify` и режим `verify-project`.

## 4. Новые сущности и интерфейсы

- Runtime entrypoint для verifier-а: `verify_project_install(project_root, source_root, profile, force=False)`.
- Legacy-режим для совместимости: `python3 scripts/install_skill.py --project-root /abs/project --mode verify-project`.
- Единый CLI-режим для операторов: `task-knowledge install verify-project --project-root /abs/project`.

## 5. Изменения в существующих компонентах

- `scripts/install_skill_runtime/models.py`: добавить константу режима.
- `scripts/install_skill_runtime/environment.py`: добавить verifier и вызвать после install.
- `scripts/install_skill_runtime/cli.py`: добавить маршрутизацию режима.
- `scripts/task_knowledge_cli.py`: добавить subcommand и маршрутизацию режима.
- `tests/test_install_skill.py`, `tests/test_task_knowledge_cli.py`: регрессионное покрытие.
- `README.md`, `SKILL.md`, `references/deployment.md`: описать полный flow.

## 6. Этапы реализации и проверки

### Этап 1: Verifier

- Добавить проверку target files, force-updatable content, project data, AGENTS/snippet.
- Проверка: `python3 -m unittest tests.test_install_skill -v`
- Аудит: `IMPLEMENTATION_AUDIT`

### Этап 2: CLI-режим

- Добавить `verify-project` в legacy и unified CLI.
- Проверка: `python3 -m unittest tests.test_task_knowledge_cli -v`
- Аудит: `IMPLEMENTATION_AUDIT`

### Этап 3: Документация

- Обновить README/SKILL/deployment.
- Проверка: `bash scripts/check-docs-localization.sh`
- Аудит: `IMPLEMENTATION_AUDIT`

### Финальный этап: Интеграция

- Прогнать полный test suite, compileall, diff check, localization guard.
- Обновить global live-copy через `make install-global`.
- Проверка: полный набор из `plan.md` и `artifacts/verification-matrix.md`.
- Аудит: `INTEGRATION_AUDIT`

## 7. Критерии приёмки

1. `install apply` не зелёный при неполной проектной установке.
2. `verify-project` доступен и не мутирует проект.
3. `--force` обновляет только допустимые templates и проверяет их актуальность.
4. `registry.md` остаётся project data и не перезаписывается.
5. Docs описывают полный project install/update flow.

## 8. Стоп-критерии

1. Verifier требует сеть или root-доступ.
2. Verifier удаляет файлы.
3. Project install начинает писать в global live-copy.
4. Existing task data или registry перезаписываются без явного scope.

## Связь с остальными файлами задачи

- `task.md` остаётся источником истины по статусу, границам и итоговому состоянию задачи.
- `plan.md` хранит исполнимый план и ссылки на этапы SDD.
- `artifacts/verification-matrix.md` хранит доказательную связку.
