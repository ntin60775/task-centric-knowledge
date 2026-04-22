# План задачи TASK-2026-0030

## Code-related контракт

- Новые runtime/package зависимости: нет.
- Изменения import/module-связей: не вводятся; добавлена bounded-timeout обработка существующих subprocess/git helper-ов.
- Критический функционал: read-only task query runtime, publish/workflow git helpers, install doctor и borrowed-layer status/refresh helpers.
- Основной сценарий: `current-task` корректно определяется на стандартной branch-схеме, а тестовые репозитории не зависят от глобальной настройки default branch.
- Проверки: compileall, targeted regression для branch/current-task сценариев, полный `unittest discover`, smoke-проверки установленного CLI.

## Шаги

- [x] Выполнить первичную диагностику структуры проекта и тестового контура.
- [x] Исправить недетерминированную базовую ветку тестовых репозиториев.
- [x] Добавить timeout-защиту для subprocess-based тестовых helper-ов.
- [x] Добавить bounded-timeout обработку в runtime git/command helper-ах.
- [x] Прогнать доступные проверки и зафиксировать результаты.
