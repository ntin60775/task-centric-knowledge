# Verification Matrix: TASK-2026-0041

| Инвариант | Сценарий нарушения | Проверка | Статус |
|-----------|-------------------|----------|--------|
| Unified CLI — единственный entrypoint | Код или документация ссылается на удалённые фасады | `grep -r "install_skill.py\|task_workflow.py\|task_query.py" --include="*.py" --include="*.md" --include="Makefile" scripts/ tests/ references/ README.md SKILL.md` | pending |
| JSON-контракт стабилен | Ломающее изменение CLI surface | Golden-тесты `test_cli_golden_contracts.py` | pending |
| Тестовое покрытие не снижено | Пропущенные сценарии после удаления фасадов | `python3 -m unittest discover -s tests -v` | pending |
| Сборка проходит | Сломан импорт или entrypoint | `make check` | pending |
