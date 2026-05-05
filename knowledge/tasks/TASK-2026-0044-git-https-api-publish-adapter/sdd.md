# SDD по задаче TASK-2026-0044

## Паспорт SDD

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0044` |
| Статус | `черновик` |
| Версия | `1` |
| Дата обновления | `2026-05-06` |

## 0. Инварианты и verification matrix

### Полный invariant set

- `INV-01`: `GitHubAPIAdapter` и `GitLabAPIAdapter` реализуют интерфейс `ForgeAdapter` (`create_publication`, `read_publication`, `update_publication`, `ensure_auth`, `ensure_cli`).
- `INV-02`: HTTPS адаптеры не требуют `gh`/`glab` CLI и работают через REST API.
- `INV-03`: `resolve_forge_adapter` выбирает CLI-адаптер первым, HTTP-адаптер вторым, при отсутствии обоих возвращает ошибку.
- `INV-04`: Токен аутентификации (`GITHUB_TOKEN`, `GITLAB_TOKEN`) не логируется и не сохраняется в файлы.
- `INV-05`: Существующие CLI-адаптеры (`GitHubAdapter`, `GitLabAdapter`) продолжают работать без изменений.
- `INV-06`: `doctor-deps` классифицирует HTTP adapter зависимости как `conditional` / `blocking_layer = publish/integration`.
- `INV-07`: `create_publication` возвращает корректный `PublicationSnapshot` с URL, статусом и refs.
- `INV-08`: `read_publication` корректно маппит состояния PR/MR из API-ответа в `PublicationSnapshot`.

### Связанные артефакты проверки

- `artifacts/verification-matrix.md`.

## 1. Проблема и цель

### Проблема

Текущий `forge.py` имеет два адаптера:
- `GitHubAdapter` — требует `gh` CLI.
- `GitLabAdapter` — требует `glab` CLI.

`doctor-deps` уже классифицирует `gh`/`glab` как `optional` в слое `publish/integration`, поэтому их отсутствие не блокирует core-функционал. Однако без них publish-контур полностью недоступен. Нужен альтернативный путь через HTTPS API, который требует только `git` и токен доступа.

### Цель

Добавить HTTP-based адаптеры как fallback/альтернативу CLI-адаптерам, чтобы publish-контур работал без `gh`/`glab`.

## 2. Архитектура и границы

### Существующая архитектура

```
resolve_forge_adapter(project_root, host_kind, ...)
  ├── GitHubAdapter(host_kind="github", cli_name="gh")
  │   ├── ensure_cli() → shutil.which("gh")
  │   ├── ensure_auth() → gh auth status
  │   ├── create_publication() → gh pr create ...
  │   ├── read_publication() → gh pr view --json ...
  │   └── update_publication() → gh pr ready ...
  └── GitLabAdapter(host_kind="gitlab", cli_name="glab")
      └── (аналогично)
```

### Целевая архитектура

```
resolve_forge_adapter(project_root, host_kind, ...)
  ├── Пробует CLI-адаптер (gh/glab) — если доступен и auth ok
  ├── Пробует HTTP-адаптер — если есть токен
  └── Ошибка — если ни один не доступен

GitHubAPIAdapter(host_kind="github", cli_name="gh-api")
  ├── ensure_cli() → OK (не требует CLI)
  ├── ensure_auth() → проверка GITHUB_TOKEN или git credential
  ├── create_publication() → POST /repos/:owner/:repo/pulls
  ├── read_publication() → GET /repos/:owner/:repo/pulls/:number
  └── update_publication() → PATCH /repos/:owner/:repo/pulls/:number

GitLabAPIAdapter(host_kind="gitlab", cli_name="glab-api")
  ├── ensure_cli() → OK
  ├── ensure_auth() → проверка GITLAB_TOKEN
  ├── create_publication() → POST /projects/:id/merge_requests
  ├── read_publication() → GET /projects/:id/merge_requests/:iid
  └── update_publication() → PUT /projects/:id/merge_requests/:iid
```

### Определение owner/repo из remote URL

Функция `remote_url()` в `git_ops.py` уже извлекает URL remote. Нужна дополнительная функция для парсинга `owner/repo` из URL:

```
git@github.com:owner/repo.git → owner=owner, repo=repo
https://github.com/owner/repo.git → owner=owner, repo=repo
```

### Аутентификация

- **GitHub**: `Authorization: Bearer $GITHUB_TOKEN` или `Authorization: token $GITHUB_TOKEN`.
- **GitLab**: `PRIVATE-TOKEN: $GITLAB_TOKEN` или `Authorization: Bearer $GITLAB_TOKEN`.

Токен читается из переменной окружения. Если токен не найден, `ensure_auth()` возвращает ошибку с понятным сообщением.

### HTTP-библиотека

Решение: использовать `urllib.request` из stdlib для минимизации зависимостей. Если код получается слишком громоздким, рассмотреть `requests`.

### Что остаётся вне задачи

- Self-hosted forge (можно добавить позже через параметр `--api-url`).
- OAuth flow.
- Интерактивный ввод токена.
- Поддержка Bitbucket, Gitea.

### Допустимые и недопустимые связи

**Допустимые:**
- `forge.py` → `urllib.request` (или `requests`).
- `forge.py` → `git_ops.py` (remote_url, detect_host_kind).
- `doctor.py` → `forge.py` (проверка доступности HTTP adapter).

**Недопустимые:**
- HTTPS adapter не должен импортировать или вызывать `gh`/`glab`.

### Новые зависимости и их обоснование

- `urllib.request` (stdlib) — предпочтительно, не требует внешних зависимостей.
- `requests` (опционально) — только если `urllib` окажется недостаточным для обработки ответов API.

### Наблюдаемые сигналы и диагностические маркеры

- HTTP status code в ответах API (201 — создан, 200 — успех, 401 — нет auth, 404 — не найден).
- Сообщения об ошибках из API (например, "Pull request already exists").

## 3. Изменения данных / схемы / metadata

`нет`

## 4. Новые сущности и интерфейсы

### `GitHubAPIAdapter(ForgeAdapter)`

```python
class GitHubAPIAdapter(ForgeAdapter):
    host_kind = "github"
    cli_name = "gh-api"

    def ensure_cli(self) -> None: ...
    def ensure_auth(self, project_root: Path) -> None: ...
    def create_publication(self, project_root, *, head_branch, base_branch, title, body, draft) -> PublicationSnapshot: ...
    def update_publication(self, project_root, *, reference, head_branch, base_branch) -> PublicationSnapshot: ...
    def read_publication(self, project_root, *, reference, head_branch, base_branch) -> PublicationSnapshot: ...
```

### `GitLabAPIAdapter(ForgeAdapter)`

Аналогичная структура для GitLab REST API v4.

### Вспомогательные функции

- `_parse_github_remote(url) -> (owner, repo)`.
- `_parse_gitlab_remote(url) -> (namespace, project)`.
- `_http_request(method, url, headers, data) -> dict` — обёртка над HTTP.

### Обновление `resolve_forge_adapter`

```python
def resolve_forge_adapter(project_root, host_kind, remote_name, url):
    # 1. Пробуем CLI adapter
    cli_adapter = _try_cli_adapter(host_kind)
    if cli_adapter:
        try:
            cli_adapter.ensure_cli()
            return cli_adapter
        except Exception:
            pass  # fall through to HTTP

    # 2. Пробуем HTTP adapter
    http_adapter = _try_http_adapter(host_kind)
    if http_adapter:
        try:
            http_adapter.ensure_auth(project_root)
            return http_adapter
        except Exception:
            pass

    # 3. Ошибка
    raise RuntimeError("No forge adapter available...")
```

## 5. Изменения в существующих компонентах

### `workflow_runtime/forge.py`

- Добавить `GitHubAPIAdapter` и `GitLabAPIAdapter`.
- Добавить вспомогательные функции HTTP-запросов и парсинга URL.
- Обновить `resolve_forge_adapter` с приоритетами.

### `install_runtime/doctor.py`

- Проверить и при необходимости обновить `doctor_deps` для классификации HTTP adapter зависимостей (urlreachability `api.github.com`).

### Тесты

- Новый файл `tests/test_forge_http.py` с mock HTTP сервером.

## 6. Этапы реализации и проверки

### Этап 1: Проектирование

- Определить точный API-контракт для GitHub и GitLab REST.
- Определить формат маппинга API-ответов в `PublicationSnapshot`.
- Verify: ревью SDD.
- Аудит: `SDD_AUDIT`.

### Этап 2: Реализация GitHubAPIAdapter

- `ensure_auth()` — проверка `GITHUB_TOKEN`.
- `create_publication()` — POST `/repos/:owner/:repo/pulls`.
- `read_publication()` — GET `/repos/:owner/:repo/pulls/:number`.
- `update_publication()` — PATCH (draft → ready).
- Verify: модульные тесты с mock HTTP.
- Аудит: `IMPLEMENTATION_AUDIT`.

### Этап 3: Реализация GitLabAPIAdapter

- Аналогично GitHub, но через GitLab REST API v4.
- Verify: модульные тесты с mock HTTP.
- Аудит: `IMPLEMENTATION_AUDIT`.

### Этап 4: Интеграция в resolve_forge_adapter

- Обновить `resolve_forge_adapter` с приоритетами: CLI → HTTP → error.
- Verify: тесты `resolve_forge_adapter` с разными конфигурациями.
- Аудит: `IMPLEMENTATION_AUDIT`.

### Этап 5: Обновление doctor-deps

- Добавить проверку доступности HTTP adapter (urlreachability).
- Verify: `task-knowledge install doctor-deps --project-root .`.
- Аудит: `IMPLEMENTATION_AUDIT`.

### Этап 6: Обновление документации

- `references/deployment.md`: описание HTTP adapter.
- `README.md`: упоминание.
- Verify: визуальная проверка.
- Аудит: `IMPLEMENTATION_AUDIT`.

### Финальный этап: Интеграция

- Полный тестовый прогон.
- `make check`.
- Интеграционный тест с реальным токеном (опционально, ручная проверка).
- Доказательство покрытия `artifacts/verification-matrix.md`.
- Аудит: `INTEGRATION_AUDIT`.

## 7. Критерии приёмки

1. `GitHubAPIAdapter` создаёт PR через REST API.
2. `GitLabAPIAdapter` создаёт MR через REST API.
3. `resolve_forge_adapter` выбирает HTTP adapter при отсутствии CLI.
4. Токен не логируется.
5. CLI-адаптеры не сломаны.
6. `doctor-deps` корректно классифицирует зависимости.
7. Тесты проходят.
8. Все инварианты покрыты.

## 8. Стоп-критерии

1. GitHub/GitLab API изменяется несовместимым образом.
2. Безопасное хранение токена невозможно гарантировать.
3. HTTP adapter не может быть реализован без внешних зависимостей (если `requests` недоступен, а `urllib` недостаточен).
4. Существующие тесты publish-flow ломаются.

## Связь с остальными файлами задачи

- `task.md` — источник истины.
- `plan.md` — исполнимый план.
- `artifacts/verification-matrix.md` — матрица покрытия.
