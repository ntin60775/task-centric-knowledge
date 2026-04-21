# План задачи TASK-2026-0011

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0011` |
| Parent ID | `—` |
| Версия плана | `3` |
| Связь с SDD | `sdd.md`, `artifacts/verification-matrix.md` |
| Дата обновления | `2026-04-13` |

## Цель

Провести модульную декомпозицию helper-а `task-centric-knowledge` без поведенческой регрессии для `sync`, delivery units и publish-flow.

## Границы

### Входит

- проектирование целевого разреза модулей;
- перенос логики из монолита в доменные и инфраструктурные слои;
- адаптация test-suite;
- тонкий CLI entrypoint поверх модульного runtime.

### Не входит

- новые пользовательские capability;
- расширение host-parity сверх текущего поведения;
- отдельный read-model layer.

## Планируемые изменения

### Код

- создать пакет `scripts/task_workflow_runtime/` с модулями `models.py`, `git_ops.py`, `task_markdown.py`, `registry_sync.py`, `forge.py`, `sync_flow.py`, `publish_flow.py`, `cli.py`, `__init__.py`;
- перенести dataclass-типизацию, normalizers и branch/unit naming в `models.py`;
- перенести git/remote/worktree/delivery-branch операции в `git_ops.py`;
- перенести чтение и обновление `task.md`, delivery table и summary extraction в `task_markdown.py`;
- перенести summary-preflight, freshness/history, registry update и merge delivery metadata в `registry_sync.py`;
- перенести forge adapters и publication snapshot logic в `forge.py`;
- оставить в `sync_flow.py` и `publish_flow.py` только orchestration-слой use-case функций;
- сократить `scripts/task_workflow.py` до bootstrap `sys.path`, compatibility re-export и вызова `main()`.

### Тесты

- сохранить `tests/test_task_workflow.py` как black-box regression через file-based import entrypoint;
- добавить модульные тесты `test_task_workflow_markdown.py`, `test_task_workflow_registry.py`, `test_task_workflow_publish.py`, `test_task_workflow_architecture.py`;
- вынести общий git/test harness в вспомогательный test-модуль без дублирования setup.

## Риски и зависимости

- неправильный разрез может только усложнить helper;
- без предварительного `core contract` модули могут закрепить неверные ownership boundaries;
- есть риск сломать subtle branch-aware и preflight-сценарии.

## Проверки

### Что можно проверить кодом или тестами

- `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_workflow.py`;
- `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'`;
- `python3 skills-global/task-centric-knowledge/scripts/task_workflow.py --help`;
- архитектурный import-graph тест;
- `git diff --check`.

### Что остаётся на ручную проверку

- `не требуется`, если архитектурный тест подтверждает тонкий facade и отсутствие циклов.

## Шаги

- [x] Создать draft-задачу на основе Track 2 из `TASK-2026-0008`.
- [x] Зафиксировать отдельную task-ветку `task/task-2026-0011-task-centric-vnext-helper-modularization`.
- [x] Утвердить модульный разрез и ownership для helper-кода.
- [x] Вынести runtime в пакет `scripts/task_workflow_runtime/`.
- [x] Сохранить compatibility surface в `scripts/task_workflow.py`.
- [x] Перенести и расширить unit-тесты.
- [x] Прогнать regression, import-graph и CLI smoke.
- [x] Закрыть verification matrix и синхронизировать итог task-артефактов.

## Критерии завершения

- helper декомпозирован на осмысленные модули;
- regression coverage подтверждает совместимость и остаётся зелёной как минимум на текущих `44` сценариях;
- новый разрез уменьшает change amplification, а не маскирует его.
