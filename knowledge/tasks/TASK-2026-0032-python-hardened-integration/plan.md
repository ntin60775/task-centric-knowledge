# План задачи TASK-2026-0032

## Code-related контракт

- Новые runtime/package зависимости: не планируются; интегрируются только изменения существующего Python/runtime/test контура.
- Изменения import/module-связей: допустимы только если они приходят из hardened snapshot и подтверждены review-pass/тестами.
- Критический функционал: CLI install/query/workflow слои, runtime-пакеты в `scripts/`, тестовый контур и task-артефакты.
- Основной сценарий: разобрать hardened архив, интегрировать полезные изменения в основной repo, найти и исправить defects итеративно, затем закрыть задачу через finalize и merge в `main`.
- Проверки: expert diff-review, targeted regressions по findings, полный `unittest discover`, compileall, `git diff --check`, localization guard и финальная re-check task truth.

## Шаги

- [x] Открыть новую задачу и синхронизировать отдельную task-ветку для integration/review цикла.
- [x] Извлечь архив, получить экспертный diff-аудит и определить точный scope интеграции.
- [x] Интегрировать доработки из hardened snapshot в основной repo без мусора из внешнего `.git`.
- [x] Повторять review-fix цикл до clean verdict и полного покрытия verification matrix.
- [ ] Синхронизировать task-артефакты, закрыть задачу и вернуть результат в `main`.
