# План задачи TASK-2026-0030

## Code-related контракт

- Новые runtime/package зависимости: нет.
- Изменения import/module-связей: не вводятся; добавлена bounded-timeout обработка существующих subprocess/git helper-ов.
- Критический функционал: read-only task query runtime, publish/workflow git helpers, install doctor и borrowed-layer status/refresh helpers.
- Основной сценарий: timeout в subprocess/git helper-ах ограничен по времени и не маскируется под ложные `non-repo`/`missing ref` диагнозы.
- Проверки: targeted regression для timeout-диагностики и branch/current-task сценариев, отдельный standalone discover для `test_task_workflow_registry.py`, compileall, полный `unittest discover`, localization guard, smoke-проверки установленного CLI/query.

## Шаги

- [x] Выполнить первичную диагностику структуры проекта и тестового контура.
- [x] Исправить недетерминированную базовую ветку тестовых репозиториев.
- [x] Добавить timeout-защиту для subprocess-based тестовых helper-ов.
- [x] Добавить bounded-timeout обработку в runtime git/command helper-ах.
- [x] Исправить ложную timeout-диагностику в `doctor` и `git_ops`.
- [x] Добавить regression-тесты на timeout-path для `doctor` и `git_ops`.
- [x] Исправить fail-safe runtime-hole в `finalize_flow` и закрыть timeout-path в blocker payload.
- [x] Исправить ложную timeout-диагностику `publish_remote` в `doctor`.
- [x] Устранить order-dependent bootstrap в `test_task_workflow_registry.py`.
- [x] Прогнать полный verify-контур и зафиксировать результаты в task-артефактах.
- [x] Повторно закрыть задачу через local finalize и подтвердить clean state на `main`.
