# План: TASK-2026-0042

## Цель

Устранить friction между pip-installable package и skill-копией. Сделать runtime-модули нормальным Python-пакетом, сохранив совместимость с `make install-local` и `make install-global`.

## Этапы

1. Спроектировать новую структуру каталогов (`src/task_knowledge/` с runtime-подпакетами).
2. Перенести `scripts/install_skill_runtime/` → `src/task_knowledge/install_runtime/` и т.д.
3. Обновить `pyproject.toml`: `[tool.setuptools.packages.find]`, `package-dir`, entrypoints.
4. Обновить все внутренние импорты в runtime и тестах.
5. Обновить `Makefile`: убрать `scripts/` из PYTHONPATH-хаков, если есть.
6. Обновить `task_knowledge_cli.py` и legacy-facades (если ещё не удалены в TASK-2026-0041).
7. Прогнать `make check`, `make check-strict`, `make verify-global-install`.

## Проверки

- [ ] `python3 -m unittest discover -s tests` проходит.
- [ ] `make check` проходит.
- [ ] `make install-local` работает и `task-knowledge --help` доступен.
- [ ] `make install-global` + `make verify-global-install` проходят.
- [ ] Нет импортов из `scripts.*` в production-коде.
- [ ] `pyproject.toml` валиден и setuptools находит все пакеты.
