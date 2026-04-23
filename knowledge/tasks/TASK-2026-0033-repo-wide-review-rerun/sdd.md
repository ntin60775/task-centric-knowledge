# Спецификация TASK-2026-0033 — repo-wide-review-rerun

## Контекст

Пользователь запросил повторить полный review-fix цикл по всему репозиторию `task-centric-knowledge` уже после интеграции python-hardened snapshot в `TASK-2026-0032`.

На старте:

1. `TASK-2026-0031` уже давал clean verdict для предыдущего состояния репозитория, но с тех пор проект получил новые packaging, CLI, runtime и regression surfaces.
2. `TASK-2026-0032` интегрировал внешний hardened snapshot выборочно и закрыл найденные дефекты интеграции, но это не заменяет новый независимый обзор всего текущего дерева.
3. Для нового цикла нужен отдельный task-контур и собственный verify-trail, чтобы findings и закрывающие проверки не смешивались с предыдущими review-задачами.
4. Пользователь явно требует повторять цикл до полного отсутствия реальных ошибок, а не ограничиваться одним зелёным прогоном тестов.

## Границы изменения

### Разрешённые связи

- Допустимы точечные исправления в `scripts/`, `tests/`, `Makefile`, `pyproject.toml`, `references/` и task-артефактах, если они устраняют реальные дефекты или evidence drift.
- Допустимо расширять regression coverage и усиливать fail-safe поведение существующих helper-ов, query/read-model слоя и packaging surface.
- Допустимо обновлять task-local verify-артефакты по мере нахождения и закрытия новых defects.

### Запрещённые связи

- Не добавлять новые runtime/package зависимости без отдельного обоснования в этой задаче.
- Не менять product scope и сетевое publish behavior без прямой необходимости для исправления доказанного дефекта.
- Не считать purely stylistic или cosmetic правки обязательной частью review-fix результата.

## Инварианты

- `INV-01`: каждый реальный medium/high finding из нового repo-wide review либо исправлен, либо доказательно снят как ложный до закрытия задачи.
- `INV-02`: install/workflow/query/module/doctor/packaging поверхности после fix-pass не должны выдавать misleading diagnostics или ломать покрытые сценарии.
- `INV-03`: полный `unittest discover`, compileall и затронутые CLI smoke-поверхности остаются зелёными после каждого завершённого пакета исправлений.
- `INV-04`: новый packaging/entrypoint слой не должен зависеть от сетевого bootstrap или побочного порядка импорта в локально поддерживаемых сценариях.
- `INV-05`: task truth и verify-артефакты остаются синхронизированными с фактическими findings, проверками и финальным branch-state.

## Реализация

- Сначала materialize task pack и синхронизируется `TASK-2026-0033` с уже созданной task-веткой.
- Затем запускаются независимые expert review-pass по разным зонам проекта параллельно с локальным baseline verify.
- Каждый реальный defect закрывается кодовой правкой и regression coverage либо отдельным доказательным снятием в артефактах задачи.
- После каждого fix-пакета review-pass и verify повторяются до clean verdict.
- В конце выполняются полный verify, task-artifact sync и local finalize обратно в `main`.

## Фактически закрытые пакеты дефектов

- `install-local` теперь различает managed Python, отсутствие `pip` и отсутствие `setuptools`; в этих режимах канонический bootstrap уходит в wrapper + `.pth`, а не падает на `pip install --user --editable .`.
- Unified workflow CLI теперь сохраняет `command=workflow` и `action=<subcommand>` на failure path и дополняет тем же discriminator success-path для `sync`.
- Runtime `file-local-policy` и `Module Core` read-model больше не режут валидные top-level governed files вроде `Makefile`; сохраняется запрет на absolute/outside-project refs.
- Unified CLI parser закреплён на `prog=task-knowledge`, поэтому `task-knowledge --help`, `python3 scripts/task_knowledge_cli.py --help` и `python3 -m task_knowledge --help` показывают один и тот же канонический usage surface.
- Regression suite усилен исполняемыми тестами на managed `install-local`, workflow error JSON, top-level governed files и canonical help surface; именно этот coverage-gap позволял дефектам проходить зелёным до текущего цикла.
- Повторный expert review от `Volta` и `Pasteur` после fix-пакета вернул clean verdict по обеим зонам без новых findings.

## Фактические проверочные пакеты

- Полный `python3 -m unittest discover -s tests -v`.
- `python3 -m compileall -q scripts tests`.
- Точечные suites по слоям, где будут найдены defects.
- CLI smoke для `task-knowledge` и legacy entrypoints, если изменятся packaging/query/workflow поверхности.
- `git diff --check`.
- Localization guard для новых task-артефактов и обновлённого `registry.md`.
