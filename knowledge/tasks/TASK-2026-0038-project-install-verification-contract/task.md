# Карточка задачи TASK-2026-0038

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0038` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0038` |
| Технический ключ для новых именуемых сущностей | `project-install-verification-contract` |
| Краткое имя | `project-install-verification-contract` |
| Человекочитаемое описание | Закрепить полную и проверяемую установку или обновление проектной части `task-centric-knowledge`. |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `main` |
| Требуется SDD | `да` |
| Статус SDD | `принят` |
| Ссылка на SDD | `sdd.md` |
| Дата создания | `2026-04-28` |
| Дата обновления | `2026-04-28` |

## Цель

Сделать установку и обновление проектной части knowledge-системы полными и проверяемыми: после `install apply` installer должен сам доказать, что managed `knowledge/`, managed-блок или snippet, project data и upgrade-state находятся в ожидаемом состоянии.

## Границы

### Входит

- Post-install verifier для проектной части системы.
- Отдельный verify-only режим для уже установленного проекта.
- Проверка полноты managed-файлов, актуальности force-updatable шаблонов, сохранности project data и managed `AGENTS.md`/snippet.
- Regression-тесты на неполную установку, stale-шаблоны и сохранность registry data.
- Документация операторского flow для полной проектной установки и обновления.

### Не входит

- Смена семантики глобальной live-copy установки.
- Автоматический destructive cleanup project data или legacy-контуров.
- Сетевой publish, PR/MR и изменение remote-настроек.

## Контекст

- источник постановки: пользовательское ожидание, что установка или обновление проектной части системы выполняется полностью, без ошибок и со всеми проверками.
- связанная бизнес-область: `task-knowledge install apply --project-root ...`.
- исходный наблюдаемый риск: установка может вернуть `ok`, но оператору нужно дополнительно помнить отдельные проверки полноты проекта.
- основной контекст сессии: новая задача.

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | Install runtime получает post-install verification и verify-only режим. |
| Конфигурация / схема данных / именуемые сущности | Добавляется install verification contract без новых runtime-зависимостей. |
| Интерфейсы / формы / страницы | Не меняются. |
| Интеграции / обмены | Target project install/update flow получает обязательную проверку результата. |
| Документация | README/SKILL/deployment docs уточняют полный flow проектной установки. |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0038-project-install-verification-contract/`
- файл плана: `plan.md`
- файл SDD: `sdd.md`
- файл verification matrix: `artifacts/verification-matrix.md`
- канонический нормативный contract: `README.md`, `SKILL.md`, `references/deployment.md`, install runtime.
- связанные коммиты / PR / ветки: `task/task-2026-0038-project-install-verification-contract`
- связанные операции в `knowledge/operations/`, если есть: `—`

## Контур публикации

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | — | `—` | `—` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |

## Текущий этап

Локальный finalize выполнен: task-ветка влита в base-ветку, рабочий контекст переведён на base-ветку, `push` остаётся отдельным шагом.
## Стратегия проверки

### Покрывается кодом или тестами

- `python3 -m unittest discover -s tests -v`
- `python3 -m compileall -q scripts tests`
- `bash scripts/check-docs-localization.sh`
- `git diff --check`
- `python3 scripts/task_knowledge_cli.py --json install verify-project --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --source-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --force`
- `make install-global-dry-run`
- `make install-global`
- `make verify-global-install`

### Остаётся на ручную проверку

- Проверить новый project install flow в реальном внешнем consumer repo при следующем рабочем обновлении.

## Критерии готовности

- `install apply` включает post-install verification и падает при неполной проектной установке.
- Verify-only режим доступен из legacy facade и unified CLI.
- Project data не перезаписывается и проверяется на наличие.
- Force-update шаблоны проверяются на совпадение с source assets.
- Документация описывает полный flow и не смешивает его с global install.

## Итоговый список ручных проверок

- Проверить новый project install flow в реальном внешнем consumer repo при следующем рабочем обновлении.

## Итог

Добавлен post-install verifier проектной установки и read-only режим `verify-project` для legacy facade и unified CLI.
`install apply` теперь добавляет `project_verify` в payload и не может вернуть успешный результат при ошибке post-install verification.
Project data сохраняется, force-updatable managed-шаблоны проверяются на актуальность, а live-copy обновлена и проверена через global install flow.
