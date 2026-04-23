# План задачи TASK-2026-0028

## Правило

Для задачи существует только один файл плана: `plan.md`.
Если задача декомпозируется, каждая подзадача получает свой собственный `plan.md` внутри своей папки.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0028` |
| Parent ID | `—` |
| Версия плана | `1` |
| Связь с SDD | `sdd.md` |
| Дата обновления | `2026-04-21` |

## Цель

Сделать text-mode formatter install helper-а совместимым и с payload `check/install/doctor-deps`, и с payload cleanup-governance, где upgrade-summary поля отсутствуют.

## Границы

### Входит

- точечная правка `print_text_report()` в `scripts/install_skill_runtime/cli.py`;
- синхронизация установленной копии skill-а;
- task-local evidence по воспроизведению и проверке.

### Не входит

- смена cleanup payload schema;
- перепроектирование текстового отчёта install helper-а;
- новые зависимости и новые команды CLI.

## Планируемые изменения

### Код

- печатать upgrade-summary поля только при их наличии в payload;
- сохранить существующий вывод для `check/install/doctor-deps`;
- проверить cleanup no-op сценарий в repo snapshot и installed copy.

### Конфигурация / схема данных / именуемые сущности

- `нет`

### Документация

- обновить task-local артефакты задачи.

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- `нет`; правка ограничена formatter-функцией в install runtime CLI.

### Границы, которые должны остаться изолированными

- cleanup runtime не должен внезапно требовать upgrade-summary;
- JSON payload не должен меняться ради text formatter-а;
- no-op cleanup с `TARGET_COUNT=0` и `COUNT=0` должен оставаться валидным результатом.

### Критический функционал

- запуск `migrate-cleanup-plan` из установленной копии без traceback.

### Основной сценарий

- оператор запускает cleanup-plan на совместимом проекте без safe-delete целей;
- helper печатает классификацию, результаты и `TARGET_COUNT=0`, `COUNT=0` в text mode;
- процесс завершается без traceback и без ложного требования `compatibility_epoch`.

### Исходный наблюдаемый симптом

- `KeyError: 'compatibility_epoch'` в `print_text_report()` для installed copy skill-а.

## Риски и зависимости

- риск починить только installed copy и оставить repo snapshot несинхронным;
- риск скрыть реальную ошибку formatter-а слишком широким подавлением отсутствующих полей;
- риск не зафиксировать evidence для no-op cleanup сценария.

## Связь с SDD

- SDD обязателен, потому что меняется CLI contract text surface для отдельного runtime path;
- покрытие инвариантов должно быть доказано через `artifacts/verification-matrix.md`.

## Проверки

### Что можно проверить кодом или тестами

- `python3 scripts/install_skill.py --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-knowledge-agent-runtime --mode migrate-cleanup-plan`
- `python3 /home/prog7/.agents/skills/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-knowledge-agent-runtime --mode migrate-cleanup-plan`
- `bash scripts/check-docs-localization.sh`
- `git diff --check`

### Что остаётся на ручную проверку

- публикационный re-check на другом проекте после распространения skill-а, если понадобится.

## Шаги

- [x] Завести task-local contract и verification matrix.
- [x] Исправить formatter в repo snapshot и installed copy.
- [x] Доказать no-op cleanup сценарий в text mode и синхронизировать task-артефакты.

## Критерии завершения

- обе копии skill-а проходят cleanup no-op сценарий без traceback;
- task-артефакты отражают симптом, инварианты и реальные проверки;
- рабочее дерево repo навыка остаётся консистентным после локализационного guard и `git diff --check`.
