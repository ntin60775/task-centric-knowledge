# План: TASK-2026-0041

## Цель

Упрощение entrypoint-контура: один канонический CLI и один набор runtime-модулей. Устранение дублирования и путаницы между legacy-facade и unified CLI.

## Этапы

1. Провести аудит всех импортов и вызовов legacy-фасадов внутри репозитория.
2. Заменить внутренние вызовы `install_skill.py`, `task_workflow.py`, `task_query.py` на `task_knowledge_cli.py` или прямые runtime-импорты.
3. Обновить тесты: удалить тесты legacy-facade, перенести необходимые сценарии на unified CLI.
4. Удалить файлы `scripts/install_skill.py`, `scripts/task_workflow.py`, `scripts/task_query.py`.
5. Обновить `Makefile`, `pyproject.toml`, `README.md`, `SKILL.md`, `references/deployment.md`, `references/adoption.md`.
6. Прогнать полный тестовый контур (`make check`, `make check-strict`).

## Проверки

- [ ] `python3 -m unittest discover -s tests` проходит без регрессии.
- [ ] `make check` проходит.
- [ ] `make check-strict` проходит (если dev-зависимости доступны).
- [ ] Файлы legacy-фасадов отсутствуют в `scripts/`.
- [ ] `task-knowledge --help` возвращает полный набор команд.
- [ ] Cross-references в документации консистентны.
