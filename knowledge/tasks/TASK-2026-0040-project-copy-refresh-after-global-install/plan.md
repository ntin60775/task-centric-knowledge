# План задачи TASK-2026-0040

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0040` |
| Parent ID | `—` |
| Версия плана | `1` |
| Связь с SDD | `не требуется` |
| Дата обновления | `2026-04-28` |

## Цель

Обновить текущую project copy из актуальной глобальной live-copy навыка и подтвердить, что installed project state полностью совпадает с выбранным `generic` profile.

## Границы

### Входит

- Выполнить `install apply --force` для текущего репозитория.
- Проверить результат через `verify-project --force`.
- Выполнить controlled compatibility-backfill, если refresh выявит pending legacy-задачи.
- Обновить task-local truth после выполнения.

### Не входит

- Изменение source runtime-кода.
- Обновление project copy в других репозиториях.
- Сетевые действия и `push`.

## Планируемые изменения

### Код

- Изменений кода не планируется.

### Конфигурация / схема данных / именуемые сущности

- Обновляется project-managed часть `AGENTS.md` и repo upgrade-state.
- Новые runtime/package зависимости: `нет`.

### Документация

- Обновляется `AGENTS.md`.
- Добавлены task-local `task.md` и `plan.md`.

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- `нет`

### Границы, которые должны остаться изолированными

- `knowledge/tasks/registry.md`, `knowledge/modules/registry.md` и существующие task-каталоги остаются project data и не перезаписываются install-helper-ом.
- Глобальная live-copy считается входным источником и в этой задаче не изменяется.
- Закрытые historical-задачи получают только migration note без переписывания protected metadata.

### Критический функционал

- Installed project state должен пройти `verify-project --force`.
- Managed refresh не должен затронуть project data.
- Repo upgrade-state должен вернуться в `fully-upgraded` / `single-writer`.

### Основной сценарий

- Оператор обновляет глобальную live-copy, затем применяет актуальный managed refresh к текущему проекту и проверяет совпадение с profile.

### Исходный наблюдаемый симптом

- `verify-project --force` вернул ошибку `Managed-блок AGENTS.md не соответствует выбранному profile`.

## Риски и зависимости

- Если не выполнить force-refresh, текущий репозиторий останется с устаревшим managed-блоком.
- Если не проверить `verify-project --force`, drift может остаться незамеченным.

## Проверки

### Что можно проверить кодом или тестами

- `task-knowledge install verify-project --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --source-root /home/prog7/.agents/skills/task-centric-knowledge --profile generic --force`
- `task-knowledge --json workflow backfill --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --task-dir <task-dir> --scope compatibility`
- `bash scripts/check-docs-localization.sh`
- `git diff --check`
- `task-knowledge --json task status --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge`

### Что остаётся на ручную проверку

- `не требуется`

## Шаги

- [x] Открыть task-ветку и task-local артефакты.
- [x] Зарегистрировать задачу в `registry.md`.
- [x] Выполнить `install apply --force` для текущего репозитория.
- [x] Проверить installed project state через `verify-project --force`.
- [x] Довести repo upgrade-state до `fully-upgraded` через controlled compatibility-backfill.
- [x] Прогнать localization guard и git whitespace check.
- [ ] Выполнить local finalize.

## Критерии завершения

- Project copy обновлена из глобальной live-copy.
- `verify-project --force` зеленый.
- Repo upgrade-state зеленый: `fully-upgraded`, `single-writer`, `legacy_pending_count=0`.
- Рабочее дерево после local finalize чистое на `main`.
