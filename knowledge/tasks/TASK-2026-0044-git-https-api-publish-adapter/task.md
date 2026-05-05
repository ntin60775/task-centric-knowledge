# Карточка задачи TASK-2026-0044

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0044` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0044` |
| Технический ключ для новых именуемых сущностей | `git-https-adapter` |
| Краткое имя | `git-https-api-publish-adapter` |
| Человекочитаемое описание | Git + HTTPS API publish adapter без обязательной зависимости от `gh`/`glab`. |
| Статус | `готова к работе` |
| Приоритет | `высокий` |
| Ответственный | `не назначен` |
| Ветка | `task/task-2026-0044-git-https-api-publish-adapter` |
| Требуется SDD | `да` |
| Статус SDD | `черновик` |
| Ссылка на SDD | `sdd.md` |
| Дата создания | `2026-05-06` |
| Дата обновления | `2026-05-06` |

## Цель

Создать новый forge adapter (`GitHubAPIAdapter`, `GitLabAPIAdapter`), который работает напрямую через Git + HTTPS API (REST) без обязательной зависимости от CLI-тулзов `gh`/`glab`. Текущие `GitHubAdapter` и `GitLabAdapter` должны остаться опциональными. `doctor-deps` должен корректно классифицировать отсутствие `gh`/`glab` как `optional` для publish-слоя (уже сделано), а новый adapter должен быть `conditional` (требуется `git` + доступ к API, но не требует `gh`/`glab`).

## Подсказка по статусу

- `черновик` — задача в процессе начального анализа, плана или спецификации.
- `готова к работе` — план утверждён, SDD готов, можно начинать реализацию.
- `в работе` — активная реализация.
- `на проверке` — ожидание review или тестирования.
- `ждёт пользователя` — ожидание решения или ввода пользователя.
- `заблокирована` — блокирована внешним фактором.
- `завершена` — задача закрыта, все delivery units в `merged` или `closed`.
- `отменена` — задача отменена.

## Git-подсказка

## Границы

### Входит

- Новый базовый класс `GitHTTPSAdapter` или адаптеры `GitHubAPIAdapter` / `GitLabAPIAdapter` в `workflow_runtime/forge.py`.
- Реализация `create_publication()` через HTTPS API (GitHub REST API `/repos/:owner/:repo/pulls`, GitLab REST API `/projects/:id/merge_requests`).
- Реализация `read_publication()` через HTTPS API.
- Реализация `update_publication()` (draft → ready) через HTTPS API.
- Аутентификация через `GITHUB_TOKEN` / `GITLAB_TOKEN` переменные окружения или git credential helper.
- Авто-определение host из git remote URL (уже есть в `git_ops.py`).
- Интеграция в `resolve_forge_adapter` с правильным приоритетом (CLI adapter первый, HTTP adapter резервный).
- Обновление `doctor-deps` для классификации HTTP adapter как `conditional`.
- Тесты для новых адаптеров.

### Не входит

- Поддержка GitHub Enterprise / GitLab self-hosted с нестандартными API endpoint (опционально, при необходимости).
- OAuth flow для получения токенов (токен должен быть предоставлен пользователем).
- Интерактивный ввод токена.
- Поддержка других forge (Bitbucket, Gitea) — только GitHub и GitLab как в существующих адаптерах.
- Изменение publish-flow логики.

## Контекст

- источник постановки: устранение жёсткой зависимости от `gh`/`glab` CLI для publish-контура. В `doctor-deps` уже разделены `core/local mode` и `publish/integration`: отсутствие `gh`/`glab` не блокирует core. Задача добавляет альтернативный путь publish без CLI.
- связанная бизнес-область: publish-контур, CI/CD интеграция.
- ограничения и зависимости: требуется `requests` (или `urllib` из stdlib). Зависит от структуры `forge.py` и `publish_flow.py`.
- исходный наблюдаемый симптом / лог-маркер: `не требуется`
- основной контекст сессии: `текущая задача`

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | `workflow_runtime/forge.py` — новые адаптеры, `workflow_runtime/publish_flow.py` — интеграция, `install_runtime/doctor.py` — обновление doctor-deps |
| Конфигурация / схема данных / именуемые сущности | Возможно `pyproject.toml` (если добавляется `requests`) |
| Интерфейсы / формы / страницы | `нет` |
| Интеграции / обмены | GitHub REST API, GitLab REST API |
| Документация | `references/deployment.md`, `README.md`, `references/task-workflow.md` |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0044-git-https-api-publish-adapter/`
- файл плана: `plan.md`
- файл SDD: `sdd.md`
- файл verification matrix: `artifacts/verification-matrix.md`
- существующий forge adapter: `src/task_knowledge/workflow_runtime/forge.py`

## Контур публикации

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | — | `—` | `—` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |

## Текущий этап

Спецификация и планирование.

## Стратегия проверки

### Покрывается кодом или тестами

- `python3 -m unittest discover -s tests -v` — тесты новых адаптеров.
- `make check` — source gate.
- Интеграционный тест с mock HTTP сервером.
- `task-knowledge install doctor-deps --project-root .` — проверка классификации зависимостей.
- Доказательство покрытия `artifacts/verification-matrix.md`.

### Остаётся на ручную проверку

- Реальный publish через HTTPS API на тестовом репозитории GitHub/GitLab.
- Поведение при отсутствии токена.
- Поведение при network errors.

## Критерии готовности

- `GitHubAPIAdapter` и `GitLabAPIAdapter` реализованы и проходят тесты.
- `resolve_forge_adapter` корректно выбирает HTTP adapter при отсутствии CLI.
- `doctor-deps` классифицирует HTTP adapter зависимости.
- Существующие CLI-адаптеры не сломаны.
- Тесты проходят.

## Итоговый список ручных проверок

- Реальный publish на GitHub/GitLab через HTTPS API.
- Поведение при отсутствии токена.
- Поведение при network errors.

## Итог

Заполняется при завершении.
