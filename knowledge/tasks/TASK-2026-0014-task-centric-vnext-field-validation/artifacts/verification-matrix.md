# Матрица проверки по задаче TASK-2026-0014

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0014` |
| Связанный SDD | `../sdd.md` |
| Версия | `2` |
| Дата обновления | `2026-04-13` |

## Канонические инварианты

| Invariant ID | Описание | Проверка | Статус |
|--------------|----------|----------|--------|
| `INV-0014-01` | Validation покрывает `clean`, `mixed_system` и `compatible` классы сред | `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/ui-ux-pro-max-skill-clean --mode check --format json`, `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/druzhina-mixed --mode check --format json`, `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/erp-compatible-1c --mode check --profile 1c --format json`, `artifacts/reference-environments.md` | `covered` |
| `INV-0014-02` | Adoption package воспроизводим и не скрывает bootstrap-порядок | `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/ui-ux-pro-max-skill-clean --mode install`, `python3 skills-global/task-centric-knowledge/scripts/task_workflow.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/ui-ux-pro-max-skill-clean --task-dir knowledge/tasks/TASK-2026-9001-ui-ux-pro-max-smoke-validation --register-if-missing --summary "Smoke-проверка первого task-контекста после чистой установки knowledge-системы" --format json`, `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/ui-ux-pro-max-skill-clean current-task --format json`, `artifacts/adoption-package.md`, `skills-global/task-centric-knowledge/references/adoption.md` | `covered` |
| `INV-0014-03` | Friction log отделяет expected behavior, documentation fixes и кандидаты в roadmap | `artifacts/friction-log.md`, `artifacts/acceptance-summary.md` | `covered` |
| `INV-0014-04` | Roadmap пополняется только подтверждёнными сигналами field validation | `rg -n \"TASK-2026-0014|bootstrap-порядок|sparse-checkout|shared `main`\" knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/strategy-roadmap.md skills-global/task-centric-knowledge/references/roadmap.md` | `covered` |
| `INV-0014-05` | Validation не расширяет scope спекулятивно и не выполняет destructive cleanup | `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/druzhina-mixed --mode migrate-cleanup-plan --format json`, `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/erp-compatible-1c --mode migrate-cleanup-plan --profile 1c --format json`, `git diff --check` | `covered` |

## Проверки уровня задачи

- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/ui-ux-pro-max-skill-clean --mode check --format json`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/ui-ux-pro-max-skill-clean --mode install`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/ui-ux-pro-max-skill-clean --mode doctor-deps --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_workflow.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/ui-ux-pro-max-skill-clean --task-dir knowledge/tasks/TASK-2026-9001-ui-ux-pro-max-smoke-validation --register-if-missing --summary "Smoke-проверка первого task-контекста после чистой установки knowledge-системы" --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/ui-ux-pro-max-skill-clean current-task --format json`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/druzhina-mixed --mode install --existing-system-mode migrate`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/druzhina-mixed --mode migrate-cleanup-plan --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/druzhina-mixed current-task --format json`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/erp-compatible-1c --mode install --force --profile 1c`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/erp-compatible-1c --mode doctor-deps --profile 1c --format json`
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/erp-compatible-1c --mode migrate-cleanup-plan --profile 1c --format json`
- `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/.codex/memories/task-2026-0014-validation-v2/erp-compatible-1c status --format json`

## Правило завершения

- Задача не считается завершённой, пока все инварианты не переведены в `covered`.
- Review не заменяет эту матрицу.
