# План задачи TASK-2026-0031

## Code-related контракт

- Новые runtime/package зависимости: не планируются.
- Изменения import/module-связей: допустимы только точечные исправления дефектов и regression coverage в существующих слоях.
- Критический функционал: install/doctor, workflow/finalize/publish helper, task query/runtime, borrowings/module/file/read-model, release/reference contract и test infrastructure.
- Основной сценарий: repo-wide review-fix цикл находит реальные дефекты во всех затронутых подсистемах, устраняет их и заканчивается clean verdict без новых behavioural regressions.
- Проверки: повторяющиеся expert review-pass, targeted regression под найденные дефекты, полный `unittest discover`, compileall, CLI smoke, `git diff --check`, localization guard и task-truth re-query.

## Шаги

- [x] Открыть новую repo-wide задачу и синхронизировать отдельную task-ветку.
- [x] Собрать первичные findings локально и от субагентов по всем основным подсистемам проекта.
- [x] Исправить первый пакет дефектов и добавить regression coverage.
- [x] Повторять review-fix цикл до отсутствия реальных findings в expert review-pass.
- [x] Прогнать полный verify-контур, синхронизировать task-артефакты и закрыть задачу через local finalize.
