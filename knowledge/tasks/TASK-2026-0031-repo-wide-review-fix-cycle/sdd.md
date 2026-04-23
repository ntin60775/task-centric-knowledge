# Спецификация TASK-2026-0031 — repo-wide-review-fix-cycle

## Контекст

Пользователь запросил новый полный review-fix цикл по всему репозиторию `task-centric-knowledge` с использованием экспертных субагентов и с требованием не останавливаться, пока реальные ошибки не будут устранены.

На старте:

1. Предыдущая задача `TASK-2026-0030` закрыла известные runtime/test hardening issues, но этот fix-pass не заменяет новый независимый обзор всего проекта.
2. На `main` нет одной активной задачи: `current-task` на этой ветке неоднозначен для исторически завершённых задач, поэтому repo-wide review нужно вести в новом отдельном task-контуре.
3. Проект содержит несколько связанных поверхностей: install/doctor, workflow/finalize/publish helper, task query/runtime, borrowings layer, Module Core, file-local contracts, release/reference docs и тестовую инфраструктуру.
4. Для этой задачи нельзя считать успехом один локальный прогон; нужен повторяющийся review-fix цикл с независимыми findings от экспертов, regression coverage и чистым verify/truth closeout.

## Границы изменения

### Разрешённые связи

- Допустимы точечные исправления в `scripts/`, `tests/`, `references/` и task-артефактах, если они устраняют реальные дефекты или evidence drift.
- Допустимо расширять regression coverage и усиливать fail-safe runtime behavior в существующих helper-ах и read-model слоях.
- Допустимо обновлять task-local verify-артефакты по мере нахождения и закрытия новых defects.

### Запрещённые связи

- Не добавлять новые runtime/package зависимости без отдельного обоснования в этой задаче.
- Не менять product scope, сетевой publish behavior или внешние API-contracts без прямой необходимости для исправления дефекта.
- Не считать косметические или purely stylistic правки частью обязательного review-fix результата.

## Инварианты

- `INV-01`: каждый реальный medium/high finding из repo-wide review либо исправлен, либо доказательно снят как ложный до закрытия задачи.
- `INV-02`: install/workflow/query/module/borrowings/release поверхности после исправлений не должны возвращать misleading diagnostics или ломать существующий behaviour в покрытых сценариях.
- `INV-03`: полный `unittest discover`, compileall и smoke-поверхности CLI должны оставаться зелёными после каждого завершённого fix-pass.
- `INV-04`: тесты и CLI, которые по контракту должны запускаться standalone, не должны зависеть от побочного порядка импорта или внешнего side-effect контекста.
- `INV-05`: task truth и verify-артефакты должны оставаться синхронизированными с фактическими findings, проверками и финальным branch-state.

## Реализация

- Сначала открывается отдельная task-ветка и materialize task pack для repo-wide review-fix цикла.
- Далее запускаются независимые review-pass от экспертных субагентов по разным подсистемам проекта параллельно с локальным audit.
- Каждый найденный defect закрывается отдельной правкой с regression coverage или с доказательным explain-why-false в task-local артефактах.
- После каждого пакета исправлений review-pass повторяется до clean verdict.
- В конце выполняются полный verify, task-artifact sync и local finalize обратно в `main`.

Фактически закрытые пакеты дефектов:

- изолированный bootstrap для standalone запуска `test_task_workflow_markdown.py` и `test_task_workflow_publish.py`;
- path-safety в `module_core`: запрет выхода за `project_root` для passport/file-local refs и фильтрация внешних evidence-paths из governed surface;
- усиление `release-contract` regression-тестов против drift в `references/core-model.md`;
- точная диагностика `doctor publish_remote` без ложного timeout-hint для обычных remote/config ошибок;
- warnings в `task_query` для `SDD`-задач без обязательных артефактов, точный `task_not_found` и policy-aware suppression после `note-only` backfill;
- controlled `note-only compatibility-backfill` для historical `TASK-2026-0004` и `TASK-2026-0006` через supported workflow;
- сохранение архитектурного import-graph `task_query` read-model без прямой зависимости от `legacy_upgrade`.

## Проверки

См. `artifacts/verification-matrix.md` и раздел `Стратегия проверки` в `task.md`.
