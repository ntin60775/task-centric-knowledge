# План задачи TASK-2026-0033

## Code-related контракт

- Новые runtime/package зависимости: не планируются; допускаются только уже интегрированные в проект поверхности без расширения dependency graph.
- Изменения import/module-связей: допустимы только точечные fix-правки и regression coverage в существующих слоях.
- Критический функционал: install-local и packaging fallback, `task-knowledge` CLI, workflow/finalize/publish helper, task query/read-model, module/file-local contracts, governance/doctor и test infrastructure.
- Основной сценарий: проект проходит новый repo-wide review-fix цикл после `TASK-2026-0032`, все реальные defects устраняются, verify остаётся зелёным, а задача закрывается только после clean verdict.
- Проверки: экспертные review-pass, targeted regressions, полный `unittest discover`, compileall, CLI smoke, `git diff --check`, localization guard и task-truth re-query.

## Шаги

- [x] Открыть и синхронизировать новую repo-wide задачу на отдельной task-ветке.
- [x] Собрать первичные findings локально и от экспертных субагентов по всем основным подсистемам проекта.
- [x] Исправить найденные defects и обновить regression coverage.
- [x] Повторять review-fix цикл до clean verdict без реальных findings.
- [x] Прогнать полный verify-контур, синхронизировать task-артефакты и закрыть задачу через local finalize.
