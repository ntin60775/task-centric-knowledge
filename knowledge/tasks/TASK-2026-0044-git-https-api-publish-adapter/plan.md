# План: TASK-2026-0044

## Цель

Сделать publish-flow самодостаточным: создание PR/MR должно работать через HTTPS API, если `gh`/`glab` не установлены, но есть `git remote` и токен.

## Этапы

1. [x] Исследовать GitHub REST API и GitLab REST API для создания PR/MR.
2. [x] Использовать `urllib.request` из stdlib (без внешних зависимостей).
3. [x] Реализовать `GitHubAPIAdapter` и `GitLabAPIAdapter` в `forge.py`.
4. [x] Реализовать авторизацию через `GITHUB_TOKEN` / `GITLAB_TOKEN` переменные окружения.
5. [x] Реализовать fallback-логику в `resolve_forge_adapter`: CLI → HTTP → error.
6. [x] Тесты с `unittest.mock` (23 теста в test_forge_http.py).
7. [x] Обновить документацию (`references/deployment.md`, `references/cli-reference.md`).
8. [x] Прогнать полный тестовый контур (290 тестов, все зелены).

## Проверки

- [x] `python3 -m unittest discover -s tests` проходит (290 тестов).
- [x] Mock-тесты для HTTP адаптеров проходят (23 теста).
- [x] Fallback-логика протестирована: при отсутствии `gh`/`glab` используется HTTP API.
- [x] Документация обновлена.
- [x] Архитектурный тест проходит (import graph не нарушен).
