# План задачи TASK-2026-0036

## Правило

Для задачи существует только один файл плана: `plan.md`.
Если задача декомпозируется, каждая подзадача получает свой собственный `plan.md` внутри своей папки.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0036` |
| Parent ID | `—` |
| Версия плана | `1` |
| Связь с SDD | `не требуется` |
| Дата обновления | `2026-04-28` |

## Цель

Закрыть config-diff `.gitignore`, который исключает локальные артефакты `zip-context` из рабочего дерева standalone-репозитория.

## Границы

### Входит

- проверить точный diff `.gitignore`;
- открыть task-контур для изменения конфигурации;
- выполнить локальные проверки;
- закоммитить, влить в `main`, запушить `origin/main`;
- удалить согласованные локальные merged-ветки.

### Не входит

- изменение или публикация навыка `zip-context`;
- удаление файловых артефактов;
- изменение unrelated ignore-правил.

## Планируемые изменения

### Код

- `нет`

### Конфигурация / схема данных / именуемые сущности

- `.gitignore`: блок `zip-context:artifacts` для `zip_context_ignore.md` и `output/share/*-zip-context-*.zip`.

### Документация

- `knowledge/tasks/TASK-2026-0036-ignore-zip-context-artifacts/task.md`
- `knowledge/tasks/TASK-2026-0036-ignore-zip-context-artifacts/plan.md`
- `knowledge/tasks/registry.md`

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- `нет`

### Границы, которые должны остаться изолированными

- ignore-правила должны оставаться узкими и не скрывать product/data артефакты;
- cleanup janitor-run не должен удалять файловые артефакты.

### Критический функционал

- чистый `git status` после commit/merge/push/branch-cleanup.

### Основной сценарий

- локальный запуск `zip-context` может создавать служебный ignore-файл и zip-снимки, но они не попадают в tracked diff.

### Исходный наблюдаемый симптом

- pending diff `.gitignore` добавляет правила для `zip_context_ignore.md` и `output/share/*-zip-context-*.zip`.

## Проверки

### Что можно проверить кодом или тестами

- `git diff --check`
- `bash scripts/check-docs-localization.sh`
- `python3 -m unittest discover -s tests`
- `task-knowledge task status --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge`

### Что остаётся на ручную проверку

- `не требуется`

## Шаги

- [x] Проверить текущий git-preflight и diff `.gitignore`
- [x] Открыть task-контур `TASK-2026-0036`
- [x] Прогнать проверки
- [x] Закоммитить задачу
- [x] Влить задачу в `main` и запушить
- [x] Очистить согласованные merged-ветки

## Критерии завершения

- `.gitignore` содержит узкий блок для локальных `zip-context` артефактов;
- task-контур синхронизирован с реестром;
- проверки пройдены;
- `main` опубликован в `origin/main`;
- `git status` чист.
