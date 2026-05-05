# План: TASK-2026-0044

## Цель

Сделать publish-flow самодостаточным: создание PR/MR должно работать через HTTPS API, если `gh`/`glab` не установлены, но есть `git remote` и токен.

## Этапы

1. Исследовать GitHub REST API и GitLab REST API для создания PR/MR.
2. Добавить `zapros` в `pyproject.toml` как optional или dev-зависимость (решить: core или optional).
3. Спроектировать `HttpsApiAdapter` в отдельном модуле `task_workflow_runtime/https_api_adapter.py` на базе `zapros.Client`.
4. Реализовать middleware для авторизации через `GITHUB_TOKEN` / `GITLAB_TOKEN` environment variables.
5. Реализовать fallback-логику: `gh` → `glab` → `zapros HTTPS API` → error с инструкцией.
6. Обновить `task_knowledge_cli.py` и `publish_flow.py` для использования нового адаптера.
7. Добавить тесты для HTTPS API adapter с `zapros.mock` или `unittest.mock`.
8. Обновить документацию (`README.md`, `references/task-workflow.md`).
9. Прогнать полный тестовый контур.

## Проверки

- [ ] `python3 -m unittest discover -s tests` проходит.
- [ ] Mock-тесты для HTTPS API adapter проходят.
- [ ] Fallback-логика протестирована: при отсутствии `gh`/`glab` используется HTTPS API.
- [ ] Документация описывает новый adapter и требования к токенам.
