# SDD: TASK-2026-0041

## Invariant set

- Unified CLI `task_knowledge_cli.py` остаётся единственным пользовательским entrypoint.
- Runtime-модули (`install_skill_runtime`, `task_workflow_runtime`, `module_core_runtime`, `borrowings_runtime`) сохраняют свой public API для прямых импортов.
- JSON-контракт CLI не ломается.
- Тестовое покрытие не снижается: все сценарии legacy-facade покрыты через unified CLI или runtime-модули.
- Документация не содержит ссылок на удалённые entrypoints.

## Допустимые связи

- `task_knowledge_cli.py` → все runtime-модули.
- Тесты → runtime-модули (прямые импорты) или subprocess `task-knowledge`.
- Удалённые фасады не импортируются нигде.

## Недопустимые связи

- Никакой код в репозитории не импортирует `install_skill`, `task_workflow`, `task_query` как модули.
- Никакой Makefile-target или документ не ссылается на `python3 scripts/install_skill.py` и т.д.

## Новые зависимости

Нет.
