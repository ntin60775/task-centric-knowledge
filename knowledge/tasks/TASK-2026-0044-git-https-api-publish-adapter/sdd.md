# SDD: TASK-2026-0044

## Invariant set

- Publish-flow не требует `gh` или `glab` как обязательных зависимостей.
- HTTPS API adapter использует `zapros` (https://github.com/kap-sh/zapros) — лёгкий typed HTTP-клиент с middleware-архитектурой. `requests` и `httpx` остаются запрещены.
- Аутентификация — только через environment variables (`GITHUB_TOKEN`, `GITLAB_TOKEN`), без stdin-запросов.
- При отсутствии токена и CLI-tools возвращается явный blocker-report, а не exception.
- CLI/JSON surface publish-контура не ломается.

## Допустимые связи

- `forge.py` (или новый модуль `https_api_adapter.py`) → `zapros.Client` / `zapros.AsyncClient`.
- `publish_flow.py` → `forge.resolve_adapter()` с fallback-цепочкой.
- Тесты → `unittest.mock` для HTTP-ответов.

## Недопустимые связи

- Нельзя добавить `requests` или `httpx` в runtime. `zapros` — единственный допустимый HTTP-клиент.
- Нельзя хардкодить credentials в коде.

## Новые зависимости

`zapros` (MIT, Python ≥3.10, зависимости: `h11`, `pywhatwgurl`, `typing-extensions`).
