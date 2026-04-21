# План задачи TASK-2026-0014

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0014` |
| Parent ID | `—` |
| Версия плана | `2` |
| Связь с SDD | `sdd.md`, `artifacts/verification-matrix.md` |
| Дата обновления | `2026-04-13` |

## Цель

Провести полевую валидацию `vNext` на трёх классах сред и выпустить adoption package,
который описывает не гипотетический quickstart, а реально проверенный порядок установки, bootstrap и governance.

## Границы

### Входит

- validation на изолированных клонах `clean/generic`, `mixed_system/generic`, `compatible/1c`;
- task-local доказательные артефакты: матрица сред, пакет внедрения, журнал friction, итоговая приёмочная сводка;
- синхронизация публичных docs `SKILL.md`, `references/adoption.md`, `references/deployment.md`, `references/task-workflow.md`;
- возврат в roadmap только подтверждённых сигналов.

### Не входит

- реализация новых helper-capability;
- cleanup-confirm в validation-клонах;
- работа по живым рабочим деревьям reference-репозиториев;
- пересборка продуктовой стратегии вне фактов field validation.

## Планируемые изменения

### Документация

- детализировать `task.md`, `plan.md`, `sdd.md` и `artifacts/verification-matrix.md` под реальный execution;
- добавить `artifacts/reference-environments.md`, `artifacts/adoption-package.md`, `artifacts/friction-log.md`, `artifacts/acceptance-summary.md`;
- добавить публичный `skills-global/task-centric-knowledge/references/adoption.md`;
- синхронизировать `SKILL.md`, `references/deployment.md`, `references/task-workflow.md` и обе roadmap.

### Контур валидации

- `clean/generic`: `check -> install -> doctor-deps -> task bootstrap smoke -> task_query`;
- `mixed_system/generic`: `check -> install --existing-system-mode migrate -> doctor-deps -> migrate-cleanup-plan`;
- `compatible/1c`: `check --profile 1c -> install --force --profile 1c -> doctor-deps --profile 1c -> migrate-cleanup-plan --profile 1c -> task_query`.

### Подтверждённые сигналы

- зафиксировать direct-path failure `task_workflow --create-branch` на dirty tree после clean install;
- зафиксировать snippet-flow при отсутствии `AGENTS.md`;
- зафиксировать boundary-condition bulky `1c` checkout в `tmpfs`;
- зафиксировать expected ambiguity/warning behavior на shared `main`.

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- `нет`

### Границы, которые должны остаться изолированными

- `Task Core` и runtime helper не меняются в рамках этой задачи;
- cleanup-governance проверяется только через `migrate-cleanup-plan`, без удаления файлов;
- live working trees исходных репозиториев не используются для mutation.

### Критический функционал

- install/upgrade/migrate сценарии должны отрабатывать предсказуемо на разных классах сред;
- adoption package должен отражать реальный bootstrap-порядок первой задачи;
- roadmap должен получить только подтверждённые сигналы field validation.

### Основной сценарий

- поднять изолированные validation-клоны;
- выполнить `check/install/doctor-deps/migrate-cleanup-plan` по классу среды;
- на `clean`-среде дополнительно проверить первую smoke-задачу и operator read-model;
- оформить evidence и синхронизировать публичные docs.

### Исходный наблюдаемый симптом

- Track 5 существовал как execution-черновик без фактического field evidence вне текущего репозитория.

## Риски и зависимости

- без предыдущих tracks field validation превратится в проверку полусобранного `vNext`;
- проверка на `main` в репозиториях с множеством задач даст ambiguity warnings и не должна трактоваться как runtime-регрессия;
- bulky `1c` checkout внутри `tmpfs` может упереться в объём среды, поэтому для governance-validation нужен non-tmpfs sparse clone;
- direct-path bootstrap первой задачи после `install` может упереться в dirty tree и должен быть документирован как явный порядок действий.

## Связь с SDD

- реализованы этапы `Select environments`, `Adoption package`, `Feedback loop`;
- verification coverage фиксируется в `artifacts/verification-matrix.md`;
- канонический source-of-truth по ядру остаётся в контракте `TASK-2026-0010`.

## Проверки

### Что можно проверить кодом или тестами

- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/ui-ux-pro-max-skill-clean --mode check --format json`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/ui-ux-pro-max-skill-clean --mode install`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/ui-ux-pro-max-skill-clean --mode doctor-deps --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_workflow.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/ui-ux-pro-max-skill-clean --task-dir knowledge/tasks/TASK-2026-9001-ui-ux-pro-max-smoke-validation --register-if-missing --summary "Smoke-проверка первого task-контекста после чистой установки knowledge-системы" --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/ui-ux-pro-max-skill-clean current-task --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/druzhina-mixed current-task --format json`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/druzhina-mixed --mode migrate-cleanup-plan --format json`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/erp-compatible-1c --mode doctor-deps --profile 1c --format json`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/erp-compatible-1c --mode migrate-cleanup-plan --profile 1c --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/erp-compatible-1c status --format json`
- `git diff --check`
- `scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0014-task-centric-vnext-field-validation/task.md knowledge/tasks/TASK-2026-0014-task-centric-vnext-field-validation/plan.md knowledge/tasks/TASK-2026-0014-task-centric-vnext-field-validation/sdd.md knowledge/tasks/TASK-2026-0014-task-centric-vnext-field-validation/artifacts/verification-matrix.md knowledge/tasks/TASK-2026-0014-task-centric-vnext-field-validation/artifacts/reference-environments.md knowledge/tasks/TASK-2026-0014-task-centric-vnext-field-validation/artifacts/adoption-package.md knowledge/tasks/TASK-2026-0014-task-centric-vnext-field-validation/artifacts/friction-log.md knowledge/tasks/TASK-2026-0014-task-centric-vnext-field-validation/artifacts/acceptance-summary.md skills-global/task-centric-knowledge/SKILL.md skills-global/task-centric-knowledge/references/adoption.md skills-global/task-centric-knowledge/references/deployment.md skills-global/task-centric-knowledge/references/task-workflow.md skills-global/task-centric-knowledge/references/roadmap.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/strategy-roadmap.md`

### Что остаётся на ручную проверку

- `не требуется`

## Шаги

- [x] Создать draft-задачу на основе Track 5 из `TASK-2026-0008`.
- [x] Выбрать эталонные репозитории и validation-классы сред.
- [x] Подготовить task-local evidence и публичный adoption package.
- [x] Провести smoke-проверки `clean`, `mixed_system` и `compatible/1c`.
- [x] Зафиксировать friction, expected behavior и подтвердить cleanup-governance.
- [x] Синхронизировать roadmap только подтверждёнными сигналами.
- [x] Прогнать `git diff --check` и localization guard.

## Критерии завершения

- field validation проведена на `clean`, `mixed_system`, `compatible/1c`;
- adoption package описывает реально проверенный порядок действий;
- evidence разделяет runtime-bug, documentation fix и expected governance/read-model behavior;
- roadmap пополнена только подтверждёнными field-сигналами.
