# SDD: TASK-2026-0042

## Invariant set

- `task-knowledge` CLI остаётся доступен после любого способа установки.
- Все runtime-модули импортируются как `task_knowledge.*` или `task_knowledge.install_runtime.*` и т.д.
- `pyproject.toml` описывает package layout корректно для editable и non-editable install.
- Тесты не зависят от хардкоженного `sys.path.insert(0, 'scripts')`.
- Backwards compatibility для consumers: CLI/JSON surface не меняется.

## Допустимые связи

- `src/task_knowledge/` → внутренние подпакеты.
- Тесты → `task_knowledge.*` (импорт пакета).
- `Makefile` → `python3 -m task_knowledge` или `task-knowledge`.

## Недопустимые связи

- Production-код не импортирует `scripts.*`.
- `pyproject.toml` не ссылается на `scripts` как на package root в финальном варианте.

## Новые зависимости

Нет новых runtime-зависимостей. Возможно, потребуется `build` или `wheel` для dev.
