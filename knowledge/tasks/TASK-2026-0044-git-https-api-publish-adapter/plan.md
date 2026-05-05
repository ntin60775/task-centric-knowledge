# План: TASK-2026-0044

## Цель

Сделать publish-flow самодостаточным: создание PR/MR должно работать через HTTPS API, если `gh`/`glab` не установлены, но есть `git remote` и токен.

## Этапы

1. Исследовать GitHub REST API и GitLab REST API для создания PR/MR.
2. Спроектировать `HttpsApiAdapter` в `task_workflow_runtime/forge.py` (или отдельный модуль).
3. Реализовать аутентификацию через `GITHUB_TOKEN` / `GITLAB_TOKEN` environment variables.
4. Реализовать fallback-логику: `gh` → `glab` → `HTTPS API` → error с инструкцией.
5. Обновить `task_knowledge_cli.py` и `publish_flow.py` для использования нового адаптера.
6. Добавить тесты для HTTPS API adapter (mock-уровень).
7. Обновить документацию (`README.md`, `references/task-workflow.md`).
8. Прогнать полный тестовый контур.

## Проверки

- [ ] `python3 -m unittest discover -s tests` проходит.
- [ ] Mock-тесты для HTTPS API adapter проходят.
- [ ] Fallback-логика протестирована: при отсутствии `gh`/`glab` используется HTTPS API.
- [ ] Документация описывает новый adapter и требования к токенам.
