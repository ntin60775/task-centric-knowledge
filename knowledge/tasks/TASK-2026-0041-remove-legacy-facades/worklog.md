# Worklog TASK-2026-0041

## 2026-05-06

### Этап 1: Удаление facade-файлов и legacy-ветки `--mode`
- Удалены `scripts/install_skill.py`, `scripts/task_workflow.py`, `scripts/task_query.py`.
- Удалена функция `_run_legacy_install_cli` и legacy-ветка `--mode` из `scripts/task_knowledge_cli.py`.
- Упрощён `scripts/install_skill_runtime/cli.py`: оставлена только `print_text_report`.
- Удалён re-export `main` из `scripts/install_skill_runtime/__init__.py`.

### Этап 2: Обновление pyproject.toml
- Убраны `install_skill`, `task_query`, `task_workflow` из `py-modules`.
- Оставлен только `task_knowledge_cli`.

### Этап 3: Обновление references
- Заменены все вызовы `python3 scripts/install_skill.py` → `task-knowledge install ...`.
- Заменены все вызовы `python3 scripts/task_workflow.py` → `task-knowledge workflow ...`.
- Заменены все вызовы `python3 scripts/task_query.py` → `task-knowledge task ...`.
- Обновлены `references/adoption.md`, `references/deployment.md`, `references/task-workflow.md`.
- Обновлены `references/core-model.md`, `references/roadmap.md`, `references/upgrade-transition.md`, `references/consumer-runtime-v1.md`.

### Этап 4: Обновление README.md, SKILL.md, Makefile, managed-блоки
- Обновлены примеры и упоминания facade-скриптов в `README.md`.
- Обновлены команды и управляемые ресурсы в `SKILL.md`.
- Обновлены `assets/agents-managed-block-generic.md` и `assets/agents-managed-block-1c.md`.

### Этап 5: Обновление тестов
- Удалены/адаптированы architecture-тесты facade-скриптов.
- `test_install_skill.py`, `test_install_skill_governance.py`: переключены на `install_skill_runtime/__init__.py`.
- `test_task_query.py`: переключён на `task_knowledge_cli.py` с unified CLI синтаксисом.
- `test_task_workflow.py`: переключён на импорты `task_workflow_runtime` напрямую.
- `test_global_skill_install.py`, `test_consumer_runtime_contract.py`: обновлены пути.
- Исправлен pre-existing тест `test_install_deploys_testing_contract_templates` (локализация шаблона).

### Этап 6: Исправление runtime-зависимостей от удалённых facade
- Обновлено `REQUIRED_RELATIVE_PATHS` в `scripts/install_skill_runtime/models.py`.
- Обновлено `embedded_runtime_ready` в `scripts/install_skill_runtime/environment.py`.

### Этап 7: Верификация
- `python3 -m unittest discover -s tests -v`: **260/260 зелёных**.
- `make install-local`: успешно.
- `task-knowledge --help`, `doctor`, `install check`, `task status`, `workflow sync`: работают.
- `artifacts/verification-matrix.md` обновлён, все инварианты покрыты.

### Исправление упавших тестов
- Причина: `test_install_skill_governance.py` использовал `importlib.import_module("install_skill_runtime.doctor")`, но `install_module` загружен через `load_module` под другим именем, поэтому патчи применялись к другому экземпляру модуля.
- Исправление: `doctor_runtime = install_module.doctor` вместо отдельного импорта.
