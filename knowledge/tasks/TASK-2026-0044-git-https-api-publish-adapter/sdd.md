# SDD: TASK-2026-0044

## Invariant set

- Publish-flow не требует `gh` или `glab` как обязательных зависимостей.
- HTTPS API adapter использует только стандартную библиотеку (`urllib` или `http.client`) или `urllib3` из stdlib-backport, но предпочтительно `urllib.request`.
- Аутентификация — только через environment variables (`GITHUB_TOKEN`, `GITLAB_TOKEN`), без stdin-запросов.
- При отсутствии токена и CLI-tools возвращается явный blocker-report, а не exception.
- CLI/JSON surface publish-контура не ломается.

## Допустимые связи

- `forge.py` (или новый модуль) → `urllib.request` / `http.client`.
- `publish_flow.py` → `forge.resolve_adapter()` с fallback-цепочкой.
- Тесты → `unittest.mock` для HTTP-ответов.

## Недопустимые связи

- Нельзя добавить heavy dependency типа `requests` или `httpx` в runtime.
- Нельзя хардкодить credentials в коде.

## Новые зависимости

Нет новых runtime-зависимостей (stdlib only).
