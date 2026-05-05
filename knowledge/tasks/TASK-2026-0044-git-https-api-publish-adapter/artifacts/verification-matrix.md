# Матрица проверки по задаче TASK-2026-0044

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0044` |
| Связанный SDD | `../sdd.md` |
| Версия | `1` |
| Дата обновления | `2026-05-06` |

## 1. Канонические инварианты

| Invariant ID | Описание | Источник истины | Где может сломаться |
|--------------|----------|-----------------|---------------------|
| `INV-01` | HTTP адаптеры реализуют интерфейс `ForgeAdapter` | `sdd.md §0` | Неполная реализация методов |
| `INV-02` | HTTP адаптеры не требуют `gh`/`glab` | `sdd.md §0` | Жёсткая зависимость от CLI |
| `INV-03` | Правильный приоритет: CLI → HTTP → error | `sdd.md §4` | Неправильный порядок в `resolve_forge_adapter` |
| `INV-04` | Токен не логируется | `sdd.md §0` | Токен в traceback, логах, print |
| `INV-05` | CLI-адаптеры не сломаны | `sdd.md §0` | Регрессия в `GitHubAdapter`/`GitLabAdapter` |
| `INV-06` | `doctor-deps` классифицирует HTTP adapter | `sdd.md §0` | Отсутствует проверка HTTP adapter |
| `INV-07` | `create_publication` возвращает `PublicationSnapshot` | `sdd.md §4` | Неправильный маппинг API-ответа |
| `INV-08` | `read_publication` маппит состояния PR/MR | `sdd.md §4` | Неправильный маппинг состояний |

## 2. Матрица покрытия

| Invariant ID | Сценарий нарушения или переход | Автопроверка / команда | Статус покрытия | Примечание |
|--------------|--------------------------------|------------------------|-----------------|------------|
| `INV-01` | Метод не реализован | `python3 -c "from task_knowledge.workflow_runtime.forge import GitHubAPIAdapter; a = GitHubAPIAdapter(); a.ensure_cli()"` | `planned` | |
| `INV-02` | Импорт `gh` в HTTP adapter | `grep -r "gh\|glab" src/task_knowledge/workflow_runtime/forge.py` (кроме имён CLI-адаптеров) | `planned` | |
| `INV-03` | CLI адаптер не выбран первым | Тест: `resolve_forge_adapter` с `gh` в PATH → CLI adapter | `planned` | |
| `INV-03` | HTTP адаптер не выбран при отсутствии CLI | Тест: `resolve_forge_adapter` без `gh`, с `GITHUB_TOKEN` → HTTP adapter | `planned` | |
| `INV-04` | Токен в выводе ошибки | Тест: перехват исключения, проверка отсутствия токена в `str(exc)` | `planned` | |
| `INV-05` | CLI `create_publication` падает | Существующие тесты `forge.py` проходят | `planned` | |
| `INV-06` | `doctor-deps` не знает про HTTP | `task-knowledge install doctor-deps --project-root .` — проверить наличие HTTP adapter в выводе | `planned` | |
| `INV-07` | `PublicationSnapshot.status` некорректен | Mock HTTP тест: ответ 201 → snapshot.status = `draft` | `planned` | |
| `INV-08` | Состояние `merged` не маппится | Mock HTTP тест: ответ с `merged: true` → snapshot.status = `merged` | `planned` | |
| `INV-08` | Состояние `closed` не маппится | Mock HTTP тест: ответ с `state: closed` → snapshot.status = `closed` | `planned` | |

## 3. Остаточный риск и ручной остаток

- Реальный publish через HTTPS API на тестовом репозитории GitHub (требует токен).
- Реальный publish через HTTPS API на тестовом репозитории GitLab (требует токен).
- Поведение при network errors (timeout, DNS, connection refused).
- Rate limiting GitHub API.

## 4. Правило завершения

- Все строки из `planned` в `covered` (или `manual-residual`).
