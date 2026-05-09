# План задачи TASK-2026-0044

## Правило

Для задачи существует только один файл плана: `plan.md`.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0044` |
| Parent ID | `—` |
| Версия плана | `1` |
| Связь с SDD | `sdd.md` |
| Дата обновления | `2026-05-06` |

## Цель

Добавить HTTPS API adapter для GitHub/GitLab как альтернативу CLI-тулзам `gh`/`glab`.

## Границы

### Входит

- Новые адаптеры `GitHubAPIAdapter`, `GitLabAPIAdapter` в `forge.py`.
- Интеграция в `resolve_forge_adapter` с приоритетами.
- Обновление `doctor-deps`.
- Тесты с mock HTTP.

### Не входит

- Self-hosted forge с нестандартными endpoint.
- OAuth flow.
- Интерактивный ввод токена.
- Изменение publish-flow логики.

## Планируемые изменения

### Код

- `src/task_knowledge/workflow_runtime/forge.py` — новые классы `GitHubAPIAdapter`, `GitLabAPIAdapter`.
- `src/task_knowledge/workflow_runtime/forge.py` — обновление `resolve_forge_adapter`.
- `src/task_knowledge/install_runtime/doctor.py` — обновление классификации зависимостей (если нужно).
- Новые тесты в `tests/` для HTTP адаптеров.

### Документация

- `references/deployment.md` — описание HTTP adapter.
- `README.md` — упоминание HTTP adapter.
- `references/task-workflow.md` — обновление при необходимости.

## Зависимости и границы

### Новые runtime/package зависимости

- `requests` (библиотека HTTP) — или использование `urllib.request` из stdlib для минимизации зависимостей. Решение принять на этапе реализации.

### Изменения import/module-связей и зависимостей между модулями

- `forge.py` получает новые классы.
- `publish_flow.py` не меняется (работает через `ForgeAdapter` интерфейс).
- `doctor.py` может обновиться для классификации `requests`.

### Границы, которые должны остаться изолированными

- Существующие `GitHubAdapter` и `GitLabAdapter` (CLI-based) не меняются.
- Publish-flow логика не меняется.
- HTTPS adapter не требует `gh`/`glab`.

### Критический функционал

- `create_publication()` через HTTPS API создаёт PR/MR.
- `read_publication()` через HTTPS API читает состояние PR/MR.
- `update_publication()` через HTTPS API переводит draft в ready.
- `ensure_auth()` проверяет наличие токена.

### Основной сценарий

1. Оператор выполняет `task-knowledge workflow publish ... --create-publication`.
2. `resolve_forge_adapter` проверяет наличие `gh`/`glab`.
3. Если CLI доступен и аутентифицирован → `GitHubAdapter`/`GitLabAdapter`.
4. Если CLI недоступен → проверяет наличие `GITHUB_TOKEN`/`GITLAB_TOKEN`.
5. Если токен доступен → `GitHubAPIAdapter`/`GitLabAPIAdapter`.
6. Adapter выполняет HTTPS запрос к API.
7. Результат маппится в `PublicationSnapshot`.

### Исходный наблюдаемый симптом

`не требуется`

## Риски и зависимости

- **Сетевая доступность**: HTTPS API требует сетевого доступа к `api.github.com` / `gitlab.com/api/v4`.
- **Rate limiting**: GitHub API имеет rate limits для неаутентифицированных запросов.
- **Токен-безопасность**: токен не должен логироваться или сохраняться в файлы.
- **Зависимость `requests`**: если использовать `requests`, это новая runtime-зависимость. Альтернатива — `urllib.request` из stdlib.

## Связь с SDD

- SDD: `sdd.md` — инварианты, архитектура адаптера, API-контракты.
- Verification matrix: `artifacts/verification-matrix.md`.
- Этапы SDD:
  1. Проектирование HTTP adapter интерфейса.
  2. Реализация `GitHubAPIAdapter`.
  3. Реализация `GitLabAPIAdapter`.
  4. Интеграция в `resolve_forge_adapter`.
  5. Обновление `doctor-deps`.
  6. Тестирование с mock HTTP.
  7. Интеграционное тестирование.

## Проверки

### Что можно проверить кодом или тестами

- `python3 -m unittest discover -s tests -v` — тесты адаптеров.
- Mock HTTP тесты для GitHub/GitLab API.
- `task-knowledge install doctor-deps --project-root .` — проверка классификации.
- Доказательство покрытия `artifacts/verification-matrix.md`.

### Что остаётся на ручную проверку

- Реальный publish через HTTPS API.
- Поведение при отсутствии токена.
- Поведение при network errors.

## Шаги

- [ ] Шаг 1: Спроектировать HTTP adapter (см. SDD).
- [ ] Шаг 2: Реализовать `GitHubAPIAdapter` в `forge.py`.
- [ ] Шаг 3: Реализовать `GitLabAPIAdapter` в `forge.py`.
- [ ] Шаг 4: Интегрировать в `resolve_forge_adapter` с приоритетами.
- [ ] Шаг 5: Обновить `doctor-deps` (при необходимости).
- [ ] Шаг 6: Написать тесты с mock HTTP.
- [ ] Шаг 7: Обновить документацию.
- [ ] Шаг 8: Прогнать тесты и проверки.
- [ ] Шаг 9: Доказать покрытие verification matrix.

## Критерии завершения

- `GitHubAPIAdapter` и `GitLabAPIAdapter` работают.
- `resolve_forge_adapter` выбирает правильный adapter.
- CLI-адаптеры не сломаны.
- Тесты проходят.
- `doctor-deps` корректен.
