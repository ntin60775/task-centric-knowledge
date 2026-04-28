# Матрица проверки TASK-2026-0039

## Таблица покрытия

| Invariant | Сценарий нарушения | Проверка / команда | Статус покрытия |
|-----------|--------------------|--------------------|-----------------|
| `INV-001` | Global install видит symlink manifest target и всё равно копирует остальные files. | `test_apply_refuses_manifest_target_symlink_before_any_copy`; `python3 -m unittest discover -s tests -v`. | `covered` |
| `INV-002` | Project install видит symlink/outside-root managed target и всё равно пишет managed files, upgrade-state или AGENTS block. | `test_install_rejects_symlinked_knowledge_directory_before_writing_assets`; `test_install_force_rejects_managed_file_symlink_without_overwriting_target`; `python3 -m unittest discover -s tests -v`. | `covered` |
| `INV-003` | External file behind symlink перезаписывается. | Global/project symlink tests проверяют неизменность `victim.txt`. | `covered` |
| `INV-004` | Workflow mutator меняет внешнюю задачу через absolute или symlinked `task_dir`. | `test_sync_task_rejects_absolute_task_dir_outside_project_before_mutation`; `test_workflow_mutators_reject_symlinked_task_dir_resolving_outside_project`. | `covered` |
| `INV-005` | Docs требуют `check-production`, который падает из-за lint/typecheck baseline. | `Makefile`, `README.md`, `references/deployment.md`: mandatory `check-production` отделён от optional `check-strict`; `python3 -m ruff check scripts tests` зафиксирован как красный baseline, `python3 -m mypy scripts` недоступен. | `covered` |
| `INV-006` | Project data перезаписывается при install `--force`. | Existing install tests на `knowledge/tasks/registry.md`, `knowledge/modules/registry.md` и task dirs; полный unittest suite. | `covered` |
| `INV-007` | Generic и 1c managed blocks расходятся по новой safety policy. | `assets/agents-managed-block-generic.md` и `assets/agents-managed-block-1c.md` обновлены одинаковыми safety rules; `bash scripts/check-docs-localization.sh`. | `covered` |
| `INV-008` | Новые user-facing Markdown строки не проходят localization policy. | `bash scripts/check-docs-localization.sh`. | `covered` |

## Фактические прогоны

- Компиляция: `python3 -m compileall -q scripts tests` -> `OK`.
- Полный unit suite: `python3 -m unittest discover -s tests -v` -> `Ran 263 tests`, `OK`.
- Проверка whitespace: `git diff --check` -> `OK`.
- Проверка локализации: `bash scripts/check-docs-localization.sh` -> `Проверка локализации пройдена.`
- Проверка read model: `task-knowledge --json task status --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge` -> `ok=true`, current task resolved by branch.
- Optional strict lint: `python3 -m ruff check scripts tests` -> `FAIL`, `134 errors`; это зафиксировано как optional `check-strict`, не mandatory production gate.
- Optional strict typecheck: `python3 -m mypy scripts` -> `FAIL`, `No module named mypy`; это зафиксировано как optional `check-strict`, не mandatory production gate.

## Ручной остаток

- Финальное review-сравнение перенесённого scope с архивом выполнено в `artifacts/snapshot-scope-review.md`.
