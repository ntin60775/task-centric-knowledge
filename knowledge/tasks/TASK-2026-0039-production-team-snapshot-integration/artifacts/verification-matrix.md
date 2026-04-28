# Матрица проверки TASK-2026-0039

## Таблица покрытия

| Invariant | Сценарий нарушения | Проверка / команда | Статус покрытия |
|-----------|--------------------|--------------------|-----------------|
| `INV-001` | Global install видит symlink manifest target и всё равно копирует остальные files. | Unit test + temp-dir smoke для `scripts/install_global_skill.py --mode apply`; ожидается `applied=[]` и отсутствие новых файлов. | `planned` |
| `INV-002` | Project install видит symlink/outside-root managed target и всё равно пишет managed files, upgrade-state или AGENTS block. | Unit test для preflight project managed targets; expected no writes before failure. | `planned` |
| `INV-003` | External file behind symlink перезаписывается. | Unit tests проверяют содержимое victim file после failed apply/install. | `planned` |
| `INV-004` | Workflow mutator меняет внешнюю задачу через absolute или symlinked `task_dir`. | Unit tests для `sync`, `backfill`, `publish`, `finalize` с `task_dir_outside_project_root`. | `planned` |
| `INV-005` | Docs требуют `check-production`, который падает из-за lint/typecheck baseline. | `make check-production` или документированное разделение mandatory/strict gates + отдельные команды. | `planned` |
| `INV-006` | Project data перезаписывается при install `--force`. | Existing + updated install tests: registry/module registry/task dirs остаются нетронутыми. | `planned` |
| `INV-007` | Generic и 1c managed blocks расходятся по новой safety policy. | Diff/audit managed blocks + localization guard. | `planned` |
| `INV-008` | Новые user-facing Markdown строки не проходят localization policy. | `bash scripts/check-docs-localization.sh`. | `planned` |

## Фактические прогоны

Пока не выполнялись в рамках реализации задачи. На этапе открытия задачи известны результаты предварительного ревью snapshot:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` в распакованном snapshot: `263 tests`, `OK`.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m ruff check scripts tests` в распакованном snapshot: `FAIL`, `132 errors`.
- `python3 -m mypy --version`: `No module named mypy`.

## Ручной остаток

- Финальное review-сравнение перенесённого scope с архивом `/home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge-production-team-2026-04-28.zip`.
