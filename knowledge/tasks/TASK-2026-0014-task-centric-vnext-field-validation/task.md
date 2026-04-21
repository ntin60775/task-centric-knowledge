# Карточка задачи TASK-2026-0014

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0014` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0014` |
| Технический ключ для новых именуемых сущностей | `vnext-field-validation` |
| Краткое имя | `task-centric-vnext-field-validation` |
| Человекочитаемое описание | `Полевая валидация и пакет внедрения для vNext task-centric-knowledge на внешних репозиториях` |
| Статус | `завершена` |
| Приоритет | `средний` |
| Ответственный | `Codex` |
| Ветка | `task/task-2026-0014-task-centric-vnext-field-validation` |
| Требуется SDD | `да` |
| Статус SDD | `завершено` |
| Ссылка на SDD | `sdd.md` |
| Дата создания | `2026-04-12` |
| Дата обновления | `2026-04-13` |

## Цель

Проверить продуктовую форму `vNext task-centric-knowledge` на изолированных репозиториях трёх классов сред,
собрать журнал friction и зафиксировать воспроизводимый adoption package,
который опирается на реальные сигналы внедрения, а не на локальную интуицию.

## Границы

### Входит

- изолированная field validation на `clean/generic`, `mixed_system/generic`, `compatible/1c`;
- reference environment matrix, adoption package, acceptance summary и friction log;
- обновление `SKILL.md`, `references/deployment.md`, `references/task-workflow.md` и нового `references/adoption.md`;
- синхронизация roadmap только подтверждёнными сигналами из полевых прогонов;
- документирование bootstrap-порядка первой задачи, миграционного сценария и cleanup-governance.

### Не входит

- runtime-расширения helper-а без отдельной задачи;
- выполнение `migrate-cleanup-confirm` в validation-клонах;
- работа в живых рабочих деревьях `druzhina` и `ERP`;
- повторное стратегическое переосмысление `vNext`.

## Контекст

- источник постановки: Track 5 из `TASK-2026-0008`;
- задача зависит от результатов `TASK-2026-0010` ... `TASK-2026-0013`;
- главный смысл: проверить, что `vNext` годится не только для этого одного репозитория;
- финальный validation-root: `/home/prog7/.codex/memories/task-2026-0014-validation-v2/`;
- классы сред:
  - `clean/generic` → `ui-ux-pro-max-skill@main` (`b7e3af8`);
  - `mixed_system/generic` → `druzhina@main` (`7ff5c62`);
  - `compatible/1c` → `ERP@main` (`65d4934cc`) через sparse-checkout `AGENTS.md + knowledge/**`.

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Внедрение | validated adoption package, bootstrap-порядок первой задачи, migration notes |
| Product feedback | журнал friction, разделение expected behavior и confirmed follow-up signals |
| Документация | task-local evidence, `references/adoption.md`, обновления `SKILL.md` и workflow docs |
| Roadmap | синхронизированы подтверждённые сигналы field validation |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0014-task-centric-vnext-field-validation/`
- файл плана: `plan.md`
- файл SDD: `sdd.md`
- матрица проверки: `artifacts/verification-matrix.md`
- матрица сред валидации: `artifacts/reference-environments.md`
- пакет внедрения: `artifacts/adoption-package.md`
- friction log: `artifacts/friction-log.md`
- итоговая приёмочная сводка: `artifacts/acceptance-summary.md`
- публичный quickstart: `skills-global/task-centric-knowledge/references/adoption.md`
- публичные синхронизированные docs: `skills-global/task-centric-knowledge/SKILL.md`, `skills-global/task-centric-knowledge/references/deployment.md`, `skills-global/task-centric-knowledge/references/task-workflow.md`
- стратегический источник: `knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/strategy-roadmap.md`

## Контур публикации

Delivery unit для этой задачи не требуется.

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | — | `—` | `—` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |

## Текущий этап

Field validation завершена.
Подтверждены три класса сред, документирован рабочий bootstrap-порядок первой задачи после чистой установки,
зафиксирован expected cleanup-governance для `mixed_system` и `compatible`,
а roadmap пополнена только сигналами, которые проявились в реальных прогонах.

## Стратегия проверки

### Покрывается кодом или тестами

- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/ui-ux-pro-max-skill-clean --mode check --format json`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/ui-ux-pro-max-skill-clean --mode install`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/ui-ux-pro-max-skill-clean --mode doctor-deps --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_workflow.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/ui-ux-pro-max-skill-clean --task-dir knowledge/tasks/TASK-2026-9001-ui-ux-pro-max-smoke-validation --register-if-missing --summary "Smoke-проверка первого task-контекста после чистой установки knowledge-системы" --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/ui-ux-pro-max-skill-clean current-task --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/ui-ux-pro-max-skill-clean task show TASK-2026-9001 --format json`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/druzhina-mixed --mode check --format json`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/druzhina-mixed --mode install --existing-system-mode migrate`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/druzhina-mixed --mode doctor-deps --format json`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/druzhina-mixed --mode migrate-cleanup-plan --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/druzhina-mixed current-task --format json`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/erp-compatible-1c --mode check --profile 1c --format json`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/erp-compatible-1c --mode install --force --profile 1c`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/erp-compatible-1c --mode doctor-deps --profile 1c --format json`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/erp-compatible-1c --mode migrate-cleanup-plan --profile 1c --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/erp-compatible-1c status --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/erp-compatible-1c current-task --format json`
- `git diff --check`
- `scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0014-task-centric-vnext-field-validation/task.md knowledge/tasks/TASK-2026-0014-task-centric-vnext-field-validation/plan.md knowledge/tasks/TASK-2026-0014-task-centric-vnext-field-validation/sdd.md knowledge/tasks/TASK-2026-0014-task-centric-vnext-field-validation/artifacts/verification-matrix.md knowledge/tasks/TASK-2026-0014-task-centric-vnext-field-validation/artifacts/reference-environments.md knowledge/tasks/TASK-2026-0014-task-centric-vnext-field-validation/artifacts/adoption-package.md knowledge/tasks/TASK-2026-0014-task-centric-vnext-field-validation/artifacts/friction-log.md knowledge/tasks/TASK-2026-0014-task-centric-vnext-field-validation/artifacts/acceptance-summary.md skills-global/task-centric-knowledge/SKILL.md skills-global/task-centric-knowledge/references/adoption.md skills-global/task-centric-knowledge/references/deployment.md skills-global/task-centric-knowledge/references/task-workflow.md skills-global/task-centric-knowledge/references/roadmap.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/strategy-roadmap.md`

### Остаётся на ручную проверку

- `не требуется`

## Критерии готовности

- подтверждены три класса validation environments;
- adoption package воспроизводим и синхронизирован в публичных reference docs;
- friction log отделяет expected behavior, documentation fixes и confirmed roadmap signals;
- cleanup-governance доказан `migrate-cleanup-plan` без выполнения delete-команд;
- roadmap пополняется только подтверждёнными сигналами.

## Итоговый список ручных проверок

- `не требуется`

## Итог

Проверка проведена на трёх изолированных средах: `clean/generic`, `mixed_system/generic` и `compatible/1c`.
Подтверждено, что install/upgrade/migrate контур воспроизводим, `doctor-deps` отделяет core/local и publish/integration,
cleanup-governance не затрагивает `project data`, а read-model на shared `main` корректно поднимает ambiguity и legacy warnings.
Главный friction clean-adoption оказался не в runtime, а в bootstrap-порядке:
после `install` и создания первых task-файлов helper не переключает ветку на грязном дереве,
поэтому валидированный путь для первой задачи — ручное создание `task/...` ветки и затем `task_workflow.py --register-if-missing`.
Для крупных `1c`-репозиториев подтверждён ещё один boundary-condition:
governance/adoption validation нужно проводить вне `tmpfs` или через sparse-checkout `AGENTS.md + knowledge/**`,
поскольку полный checkout bulky-репозитория в `/tmp` не является необходимым и может упираться в объём среды.
