# План задачи TASK-2026-0038

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0038` |
| Parent ID | `—` |
| Версия плана | `1` |
| Связь с SDD | `sdd.md`, этапы 1-4 |
| Дата обновления | `2026-04-28` |

## Цель

Закрепить полный install/update flow проектной части: preflight, apply, post-install verification, doctor-deps и cleanup-plan остаются явными и проверяемыми.

## Границы

### Входит

- Постустановочный verifier.
- Режим проверки без записи.
- Регрессионные тесты.
- Документация полного операторского flow.

### Не входит

- Глобальная установка live-copy.
- Разрушительный cleanup.
- Публикация и push.

## Планируемые изменения

### Код

- Добавить verifier в install runtime.
- Подключить verifier после `install apply`.
- Добавить режим `verify-project` в legacy facade и unified CLI.
- Добавить tests на missing/stale/project-data/AGENTS scenarios.

### Конфигурация / схема данных / именуемые сущности

- Новых runtime/package зависимостей нет.
- Добавляется именованный install verification contract.

### Документация

- Обновить `README.md`, `SKILL.md`, `references/deployment.md`.

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- Verify logic живёт внутри `install_skill_runtime.environment`.
- Facade CLI импортирует только существующие runtime entrypoints.

### Границы, которые должны остаться изолированными

- Project install не пишет в `~/.agents/skills`.
- Global install не пишет в target project.
- Cleanup требует отдельный plan/confirm.

### Критический функционал

- Неполная установка не может считаться успешной.
- Project data не теряется при `--force`.
- Managed-блок не дублируется и не маскирует invalid markers.

### Основной сценарий

- Оператор запускает `task-knowledge install apply --project-root /abs/project --force` для обновления.
- Installer пишет только допустимые managed-файлы.
- Installer выполняет post-install verification и возвращает ошибки при неполном результате.
- Оператор может отдельно запустить `task-knowledge install verify-project --project-root /abs/project`.

### Исходный наблюдаемый риск

- Установка могла быть частично успешной, но полнота project knowledge проверялась отдельной операторской дисциплиной, а не единым contract-ом installer-а.

## Связь с SDD

- Этап 1: post-install verifier.
- Этап 2: CLI mode и payload contract.
- Этап 3: tests.
- Этап 4: docs и full verify.
- Матрица покрытия: `artifacts/verification-matrix.md`.

## Проверки

### Что можно проверить кодом или тестами

- `python3 -m unittest discover -s tests -v`
- `python3 -m compileall -q scripts tests`
- `bash scripts/check-docs-localization.sh`
- `git diff --check`
- `make verify-global-install`

### Что остаётся на ручную проверку

- Проверка на реальном внешнем consumer repo при следующем обновлении.

## Шаги

- [x] Этап 1: добавить verifier проектной установки.
- [x] Этап 2: подключить CLI режим `verify-project`.
- [x] Этап 3: добавить regression-тесты.
- [x] Этап 4: обновить документацию, full verify, global install, finalize.

## Критерии завершения

- `install apply` сам доказывает результат.
- `verify-project` доступен и работает без мутаций.
- Missing/stale/project-data cases покрыты тестами.
- Проверки пройдены, задача зафиксирована коммитом.
