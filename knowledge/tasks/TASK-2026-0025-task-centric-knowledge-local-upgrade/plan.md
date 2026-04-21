# План задачи TASK-2026-0025

## Правило

Для задачи существует только один файл плана: `plan.md`.
Если задача декомпозируется, каждая подзадача получает свой собственный `plan.md` внутри своей папки.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0025` |
| Parent ID | `—` |
| Версия плана | `2` |
| Связь с SDD | `не требуется` |
| Дата обновления | `2026-04-21` |

## Цель

Обновить managed knowledge-систему текущего репозитория до актуального состояния,
которое задаёт skill `task-centric-knowledge`,
не затронув существующие task-данные и пользовательские части репозитория вне managed-scope,
а также зафиксировать состояние перехода репозитория и восстановить штатный verify-контур cleanup-governance.

## Границы

### Входит

- локальная проверка совместимости существующей системы;
- `install --force` из актуального skill-source;
- диагностика зависимостей и cleanup-governance после upgrade;
- точечный кодовый фикс install/governance CLI, если upgrade выявит регрессию в штатной verify-команде;
- регистрация и сопровождение task-local артефактов перехода.

### Не входит

- сетевые действия, публикация и `push`;
- удаление каких-либо путей без отдельного подтверждённого cleanup-плана;
- массовый compatibility-backfill legacy-задач;
- функциональные изменения вне managed knowledge-системы и verify/governance-контура.

## Планируемые изменения

### Код

- ожидается точечное изменение `scripts/install_skill_runtime/cli.py`, если cleanup text-surface окажется несовместим с новым payload;
- ожидается регрессионный тест в `tests/test_install_skill_governance.py`;
- материализованные managed-ресурсы репозитория и состояние перехода репозитория могут измениться как результат `install --force`.

### Конфигурация / схема данных / именуемые сущности

- managed-блок `AGENTS.md`;
- файлы `knowledge/README.md`, `knowledge/operations/README.md`, `knowledge/tasks/README.md`;
- шаблоны `knowledge/tasks/_templates/**`, кроме `knowledge/tasks/registry.md` как project data;
- `knowledge/operations/task-centric-knowledge-upgrade.md`;
- task-local регистрация `TASK-2026-0025`.

### Документация

- `knowledge/tasks/TASK-2026-0025-task-centric-knowledge-local-upgrade/task.md`
- `knowledge/tasks/TASK-2026-0025-task-centric-knowledge-local-upgrade/plan.md`
- `knowledge/operations/task-centric-knowledge-upgrade.md`
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
- legacy-задачи не должны получать silent compatibility-backfill в рамках этого upgrade.

### Критический функционал

- installer должен обновить managed-scope без дублирования блоков;
- повторная диагностика после upgrade должна оставаться зелёной;
- `migrate-cleanup-plan` не должен падать в text-режиме на payload без upgrade-полей;
- cleanup-governance не должен неожиданно расширять scope удаления.

### Основной сценарий

- проект проходит `check` как `compatible`;
- upgrade применяется через `install --force`;
- оператор проверяет `doctor-deps`, `git diff --check` и `migrate-cleanup-plan`;
- если cleanup verify падает из-за runtime-regression, фикс ограничивается formatter/test слоем и затем сценарий перепроверяется;
- задача фиксирует итог перехода как отдельный локальный change-set.

### Исходный наблюдаемый симптом

- текущая knowledge-система уже совместима, но пользователь запросил приведение её к последней версии skill-а; после install ожидается governed transition в `module-core-v1` без автоматического historical backfill.

## Риски и зависимости

- если installer затронет project data, upgrade нельзя считать безопасным;
- если managed-блок `AGENTS.md` задвоится, переход нужно остановить как невалидный;
- если cleanup-plan вернёт неожиданный scope, удаление выполнять нельзя;
- если install материализует pending legacy-backfill, это состояние нужно только зафиксировать, а не скрытно разрулить переписыванием исторических задач.

## Связь с SDD

- `не требуется`

## Проверки

### Что можно проверить кодом или тестами

- `python3 /home/prog7/.agents/skills/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --mode check`
- `python3 /home/prog7/.agents/skills/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --mode install --force`
- `python3 /home/prog7/.agents/skills/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --mode doctor-deps`
- `python3 scripts/install_skill.py --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --mode check`
- `python3 scripts/install_skill.py --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --mode migrate-cleanup-plan`
- `python3 -m unittest tests.test_install_skill_governance.InstallSkillGovernanceTests.test_migrate_cleanup_plan_text_cli_does_not_require_upgrade_fields tests.test_install_skill_governance.InstallSkillGovernanceTests.test_migrate_cleanup_plan_discloses_scope_and_protected_paths`
- `python3 -m unittest discover -s tests`
- `git diff --check`
- `bash scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0025-task-centric-knowledge-local-upgrade/task.md knowledge/tasks/TASK-2026-0025-task-centric-knowledge-local-upgrade/plan.md knowledge/operations/task-centric-knowledge-upgrade.md`

### Что остаётся на ручную проверку

- `не требуется`

## Шаги

- [x] Выполнить `check` и `doctor-deps` для подтверждения upgrade-контекста.
- [x] Переиспользовать `TASK-2026-0025` как task-scoped контур повторного локального upgrade.
- [x] Применить `install --force`, сформировать состояние перехода репозитория и проверить фактический diff.
- [x] Прогнать post-upgrade diagnostics и cleanup-plan.
- [x] Исправить CLI-regression text formatter-а для `migrate-cleanup-plan` и закрыть её тестом.
- [x] Завершить task-local документацию и локализационный guard.

## Критерии завершения

- upgrade завершён без потери project data;
- состояние перехода репозитория отражает `module-core-v1 / partially-upgraded / dual-readiness`;
- post-upgrade diagnostics не содержат core/local blockers;
- cleanup-plan не требует неожиданных удалений и не падает в text-режиме;
- pending legacy-backfill зафиксирован явно и не был выполнен молча;
- зафиксирован воспроизводимый test coverage для formatter regression.
