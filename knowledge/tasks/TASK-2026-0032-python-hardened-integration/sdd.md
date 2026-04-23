# Спецификация TASK-2026-0032 — python-hardened-integration

## Контекст

Пользователь передал внешний архив `task-centric-knowledge-python-hardened.zip` и потребовал выполнить полный цикл `integrate -> review -> fix -> repeat`, а затем закрыть задачу и смержить итог в `main`.

На старте:

1. Основной репозиторий находится на чистой `main`, а активная задача на этой ветке неоднозначна, значит нужен новый task-контур.
2. Архив содержит отдельный git snapshot с собственным `.git/`, поэтому прямое копирование содержимого рискованно: можно затащить лишний branch/history noise.
3. Пользователь явно попросил использовать экспертных субагентов, поэтому анализ diff-а и первичный code review должен идти как минимум двумя независимыми read-only pass.
4. Успехом считается не просто импорт файлов, а clean verdict после повторяемого review-fix цикла и корректный merge обратно в `main`.

## Границы изменения

### Разрешённые связи

- допустимо интегрировать изменения кода, тестов, reference/docs и task-артефактов, если они реально присутствуют в hardened snapshot и проходят review-fix цикл;
- допустимо отбрасывать архивный `.git`, временные артефакты и любые не относящиеся к продукту следы внешнего snapshot;
- допустимо добавлять или усиливать regression-тесты по найденным дефектам.

### Запрещённые связи

- нельзя переносить `.git/`, служебные lock/log/metadata файлы архива или использовать их как источник истины для основного репозитория;
- нельзя закрывать задачу при наличии unresolved findings от локального или экспертного review-pass;
- нельзя считать архив безусловно корректным только потому, что он назван `hardened`.

## Инварианты

- `INV-01`: в основной репозиторий интегрируются только продуктовые изменения из архива; git metadata, мусор и посторонние артефакты не попадают в итоговый diff.
- `INV-02`: каждый medium/high finding из локального или экспертного review-pass либо исправлен, либо доказательно снят как ложный до закрытия задачи.
- `INV-03`: после каждого завершённого fix-pass общий verify-контур (`unittest`, compileall, targeted regressions, doc/task checks) остаётся зелёным.
- `INV-04`: task truth (`task.md`, `plan.md`, `sdd.md`, `verification-matrix.md`, `registry.md`) синхронизирован с фактическими findings, проверками и финальным branch-state.
- `INV-05`: итоговая задача закрывается только после local finalize/merge в `main`, а не на промежуточной task-ветке.

## Реализация

- Открыть отдельную task-ветку и materialize task pack для integration/review цикла.
- Извлечь архив в изолированную временную директорию, не затрагивая основной repo.
- Получить независимые экспертные отчёты: git/diff аудит и code review по доработкам.
- Интегрировать в основной repo только релевантные изменения из archive snapshot.
- После каждого пакета правок повторять review-pass и усиливать regression coverage до clean verdict.
- В конце прогнать полный verify-контур, синхронизировать task-артефакты и закрыть задачу через merge в `main`.

## Фактически закрытые пакеты

- Packaging/Python-entrypoint: добавлены `scripts/task_knowledge/{__init__.py,__main__.py}`, package entrypoint в `pyproject.toml`, golden/static contract tests и offline-friendly fallback в `Makefile` через wrapper + `.pth` shim.
- CLI/parser hardening: `scripts/task_knowledge_cli.py` декомпозирован на секции `doctor/install/task/module/file/workflow/borrowings` без смены CLI namespace.
- Runtime decomposition: из архива перенесены безопасные refactor-пакеты в `finalize_flow.py`, `publish_flow.py`, `sync_flow.py`, `module_core_runtime/read_model.py`, но с сохранением уже существующих защит текущего `main`.
- Review-fix пакет по findings: при переносе не были приняты архивные regressions в `git_ops.py`, `install_skill_runtime/doctor.py`, `file_local_contracts.py`; в merged `read_model.py` сохранена строгая фильтрация project-root, а в `finalize_flow.py` дополнительно возвращён safe fallback для branch/remote probes в error-path.
- Verify/evidence пакет: добавлены golden JSON fixtures, новый `tests/test_cli_golden_contracts.py`, усиленный `tests/test_python_hardening_contracts.py`, smoke на `python -m task_knowledge` и offline install path через `make install-local`.

## Проверки

См. `artifacts/verification-matrix.md` и раздел `Стратегия проверки` в `task.md`.
