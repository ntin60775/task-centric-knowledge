# Карточка задачи TASK-2026-0040

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0040` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0040` |
| Технический ключ для новых именуемых сущностей | `—` |
| Краткое имя | `project-copy-refresh-after-global-install` |
| Человекочитаемое описание | `Обновить текущую project copy после обновления глобальной установки навыка task-centric-knowledge.` |
| Статус | `завершена` |
| Приоритет | `средний` |
| Ответственный | `не назначен` |
| Ветка | `main` |
| Требуется SDD | `нет` |
| Статус SDD | `не требуется` |
| Ссылка на SDD | `—` |
| Дата создания | `2026-04-28` |
| Дата обновления | `2026-04-28` |

## Цель

Синхронизировать текущую project copy репозитория с уже обновленной глобальной live-copy `task-centric-knowledge`, чтобы `verify-project --force` снова проходил без drift по managed-блоку.

## Границы

### Входит

- Обновить managed-блок `AGENTS.md` из глобальной live-copy.
- Сохранить project data: task-каталоги, registry и модульный registry.
- Проверить project copy через `verify-project --force`.
- Довести repo upgrade-state до `fully-upgraded`, если refresh выявит pending legacy-задачи.
- Прогнать локализационный guard для измененных пользовательских Markdown-текстов.

### Не входит

- Изменение runtime-кода навыка или CLI.
- Обновление других проектов.
- Повторное обновление глобальной live-copy.
- `git push`, удаление веток и cleanup.

## Контекст

- источник постановки: пользователь попросил обновить текущую копию после проверки drift;
- связанная бизнес-область: install/upgrade governance навыка `task-centric-knowledge`;
- исходный наблюдаемый симптом / лог-маркер: `verify-project --force` показал ошибку `Managed-блок AGENTS.md не соответствует выбранному profile`;
- основной контекст сессии: новая локальная task-scoped задача.

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | `нет` |
| Конфигурация / схема данных / именуемые сущности | project-managed блок `AGENTS.md`, repo upgrade-state; новых runtime/package зависимостей нет |
| Интерфейсы / формы / страницы | `нет` |
| Интеграции / обмены | Project install/verify contract текущего репозитория |
| Документация | `AGENTS.md`, task-local артефакты задачи |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0040-project-copy-refresh-after-global-install/`
- файл плана: `plan.md`
- файл SDD: `не требуется`
- заметки миграции: `knowledge/tasks/TASK-2026-0035-native-runtime-surfaces-for-consumers/artifacts/migration/task-centric-knowledge-upgrade.md`, `knowledge/tasks/TASK-2026-0036-ignore-zip-context-artifacts/artifacts/migration/task-centric-knowledge-upgrade.md`, `knowledge/tasks/TASK-2026-0037-global-skill-install-contract/artifacts/migration/task-centric-knowledge-upgrade.md`, `knowledge/tasks/TASK-2026-0038-project-install-verification-contract/artifacts/migration/task-centric-knowledge-upgrade.md`, `knowledge/tasks/TASK-2026-0039-production-team-snapshot-integration/artifacts/migration/task-centric-knowledge-upgrade.md`, `artifacts/migration/task-centric-knowledge-upgrade.md`
- связанные коммиты / PR / ветки: `task/task-2026-0040-project-copy-refresh-after-global-install`

## Контур публикации

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | — | `—` | `—` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |

## Текущий этап

Локальный finalize выполнен: task-ветка влита в base-ветку, рабочий контекст переведён на base-ветку, `push` остаётся отдельным шагом.
## Стратегия проверки

### Покрывается кодом или тестами

- `task-knowledge install verify-project --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --source-root /home/prog7/.agents/skills/task-centric-knowledge --profile generic --force`
- `task-knowledge --json workflow backfill --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --task-dir <task-dir> --scope compatibility`
- `bash scripts/check-docs-localization.sh`
- `git diff --check`
- `task-knowledge --json task status --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge`

### Остаётся на ручную проверку

- `не требуется`

## Критерии готовности

- `verify-project --force` проходит без drift.
- Project data не перезаписаны.
- Repo upgrade-state снова `fully-upgraded` и `single-writer`.
- Измененные пользовательские тексты прошли localization guard.
- Локальный finalize выполнен отдельным task-scoped commit-ом.

## Итоговый список ручных проверок

- `не требуется`

## Итог

Текущая project copy обновлена из глобальной live-copy. Drift managed-блока устранен, `verify-project --force` проходит без ошибок, repo upgrade-state доведен до `fully-upgraded`.
