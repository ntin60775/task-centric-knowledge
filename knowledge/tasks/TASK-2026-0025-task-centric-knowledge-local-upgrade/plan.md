# План задачи TASK-2026-0025

## Правило

Для задачи существует только один файл плана: `plan.md`.
Если задача декомпозируется, каждая подзадача получает свой собственный `plan.md` внутри своей папки.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0025` |
| Parent ID | `—` |
| Версия плана | `1` |
| Связь с SDD | `не требуется` |
| Дата обновления | `2026-04-20` |

## Цель

Обновить managed knowledge-систему текущего репозитория до актуального состояния,
которое задаёт skill `task-centric-knowledge`,
не затронув существующие task-данные и пользовательские части репозитория вне managed-scope.

## Границы

### Входит

- локальная проверка совместимости существующей системы;
- `install --force` из актуального skill-source;
- диагностика зависимостей и cleanup-governance после upgrade;
- регистрация и сопровождение task-local артефактов перехода.

### Не входит

- сетевые действия, публикация и `push`;
- удаление каких-либо путей без отдельного подтверждённого cleanup-плана;
- функциональные изменения вне managed knowledge-системы.

## Планируемые изменения

### Код

- прямых изменений продуктового кода не планируется;
- ожидаются изменения только в materialized managed-ресурсах репозитория.

### Конфигурация / схема данных / именуемые сущности

- managed-блок `AGENTS.md`;
- файлы `knowledge/README.md`, `knowledge/operations/README.md`, `knowledge/tasks/README.md`;
- шаблоны `knowledge/tasks/_templates/**`, кроме `knowledge/tasks/registry.md` как project data;
- task-local регистрация `TASK-2026-0025`.

### Документация

- `knowledge/tasks/TASK-2026-0025-task-centric-knowledge-local-upgrade/task.md`
- `knowledge/tasks/TASK-2026-0025-task-centric-knowledge-local-upgrade/plan.md`
- обновлённые managed-docs knowledge-системы.

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- `нет`

### Границы, которые должны остаться изолированными

- `knowledge/tasks/registry.md` остаётся project data и не должен быть перезаписан шаблоном;
- существующие task-каталоги `knowledge/tasks/TASK-*` не должны получить silent rewrite;
- пользовательские секции `AGENTS.md` вне managed-блока не должны быть затронуты.

### Критический функционал

- installer должен обновить managed-scope без дублирования блоков;
- повторная диагностика после upgrade должна оставаться зелёной;
- cleanup-governance не должен неожиданно расширять scope удаления.

### Основной сценарий

- проект проходит `check` как `compatible`;
- upgrade применяется через `install --force`;
- оператор проверяет `doctor-deps`, `task show`, `git diff --check` и `migrate-cleanup-plan`;
- задача фиксирует итог перехода как отдельный локальный change-set.

### Исходный наблюдаемый симптом

- текущая knowledge-система уже совместима, но пользователь запросил приведение её к последней версии skill-а.

## Риски и зависимости

- если installer затронет project data, upgrade нельзя считать безопасным;
- если managed-блок `AGENTS.md` задвоится, переход нужно остановить как невалидный;
- если cleanup-plan вернёт неожиданный scope, удаление выполнять нельзя.

## Связь с SDD

- `не требуется`

## Проверки

### Что можно проверить кодом или тестами

- `python3 /home/prog7/.agents/skills/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules --mode check`
- `python3 /home/prog7/.agents/skills/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules --mode install --force`
- `python3 /home/prog7/.agents/skills/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules --mode doctor-deps`
- `python3 /home/prog7/.agents/skills/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules --mode migrate-cleanup-plan`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules task show TASK-2026-0025 --format json`
- `git diff --check`
- `bash scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0025-task-centric-knowledge-local-upgrade/task.md knowledge/tasks/TASK-2026-0025-task-centric-knowledge-local-upgrade/plan.md knowledge/tasks/registry.md`

### Что остаётся на ручную проверку

- `не требуется`

## Шаги

- [x] Выполнить `check` и `doctor-deps` для подтверждения upgrade-контекста.
- [x] Создать и зарегистрировать отдельную задачу под transition версии.
- [x] Применить `install --force` и проверить фактический diff.
- [x] Прогнать post-upgrade diagnostics и cleanup-plan.
- [x] Завершить task-local документацию и локализационный guard.

## Критерии завершения

- upgrade завершён без потери project data;
- новая задача зарегистрирована в `registry.md` и видна операторскому CLI;
- post-upgrade diagnostics не содержат core/local blockers;
- cleanup-plan не требует неожиданных удалений;
- зафиксировано, что materialized managed-scope уже совпадал с актуальной версией skill-а.
