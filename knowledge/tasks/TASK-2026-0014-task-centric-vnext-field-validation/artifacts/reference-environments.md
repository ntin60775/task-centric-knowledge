# Эталонные среды field validation

## Финальный execution-root

- основной validation-root: `/home/prog7/.codex/memories/task-2026-0014-validation-v2/`
- вспомогательный `TMPDIR`: `/home/prog7/.codex/memories/task-2026-0014-tmp/`

Промежуточная попытка валидировать bulky `ERP` внутри `/tmp` была остановлена:
полный checkout упёрся в заполнение `tmpfs` и не нужен для governance/adoption validation.
Итоговый `1c`-сценарий проверялся на non-tmpfs sparse-клоне.

## Матрица сред

| Класс среды | Исходный репозиторий | Baseline | Изолированная копия | Профиль | Проверенный контур | Итог |
|-------------|----------------------|----------|----------------------|---------|--------------------|------|
| `clean` | `/home/prog7/РабочееПространство/work/AI/ui-ux-pro-max-skill` | `main@b7e3af8` | `/home/prog7/.codex/memories/task-2026-0014-validation-v2/ui-ux-pro-max-skill-clean` | `generic` | `check -> install -> doctor-deps -> bootstrap первой задачи -> task_query` | `pass with documented bootstrap caveat` |
| `mixed_system` | `/home/prog7/РабочееПространство/projects/PetProjects/druzhina` | `main@7ff5c62` | `/home/prog7/.codex/memories/task-2026-0014-validation-v2/druzhina-mixed` | `generic` | `check -> install --existing-system-mode migrate -> doctor-deps -> migrate-cleanup-plan -> task_query` | `pass` |
| `compatible` | `/home/prog7/РабочееПространство/projects/1C_Projects/ERP` | `main@65d4934cc` | `/home/prog7/.codex/memories/task-2026-0014-validation-v2/erp-compatible-1c` | `1c` | `check -> install --force -> doctor-deps -> migrate-cleanup-plan -> task_query` | `pass with sparse-checkout pattern` |

## Детали по средам

### `clean/generic`

- `AGENTS.md` отсутствовал, installer создал `AGENTS.task-centric-knowledge.generic.md`.
- После `install` task-контур пуст, `task_query status` возвращает `current_task_unresolved/no_tasks`.
- Прямой запуск `task_workflow.py --create-branch` после `install` и создания первых task-файлов остановился на dirty tree.
- Валидированный порядок:
  1. вручную создать `task/...` ветку;
  2. создать каталог задачи из шаблонов;
  3. вызвать `task_workflow.py --register-if-missing`;
  4. проверить `current-task` и `task show`.

### `mixed_system/generic`

- `install --existing-system-mode migrate` materialized managed-блок и `knowledge/MIGRATION-SUGGESTION.md`.
- `doctor-deps` показал `Core/local blockers: 0; publish/integration issues: 0`.
- `migrate-cleanup-plan` дал `target_count=0`, `count=0`, `manual_review=docs/roadmap`.
- `current-task` на ветке `main` вернул `ambiguous/branch_tie` и существующие drift warnings, что соответствует warning-first read-model policy.

### `compatible/1c`

- Для field validation использовался sparse-checkout `AGENTS.md + knowledge/**`; этого достаточно для install/upgrade/read-model/governance сценариев.
- `install --force --profile 1c` обновил managed-файлы и оставил `knowledge/tasks/registry.md` как project data.
- `doctor-deps --profile 1c` показал `Core/local blockers: 0; publish/integration issues: 0`.
- `migrate-cleanup-plan --profile 1c` выдал ровно один allowlist-target: `knowledge/MIGRATION-SUGGESTION.md`.
- `status/current-task` на shared `main` вернули ambiguity и legacy warnings, не выбрав задачу молча.
