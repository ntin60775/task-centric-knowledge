# SDD по задаче TASK-2026-0046

## Паспорт SDD

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0046` |
| Статус | `черновик` |
| Версия | `1` |
| Дата обновления | `2026-05-06` |

## 0. Инварианты и verification matrix

### Полный invariant set

- `INV-01`: `mass-update` обнаруживает все проекты с установленной knowledge-системой (managed-блок `BEGIN_TASK_KNOWLEDGE_SYSTEM#KB01` в `AGENTS.md`).
- `INV-02`: Каждый проект проходит полный цикл: check → apply --force → verify-project --force.
- `INV-03`: Ошибка в одном проекте не прерывает обработку остальных.
- `INV-04`: `--dry-run` выполняет только check, без apply.
- `INV-05`: Сводный отчёт содержит статус каждого проекта (ok/warning/error/skipped).
- `INV-06`: `project_root` каждого обнаруженного проекта проходит managed-path safety проверки перед обновлением.
- `INV-07`: Существующие функции (`check`, `install`, `verify_project`) не изменяются.
- `INV-08`: `--profile` фильтрует проекты по профилю managed-блока (generic/1c).

### Связанные артефакты проверки

- `artifacts/verification-matrix.md`.

## 1. Проблема и цель

### Проблема

Production rollout (`README.md`) требует ручного обновления каждого проекта:

```bash
make project-install-check PROJECT_ROOT=/abs/project1 ...
make project-install-check PROJECT_ROOT=/abs/project2 ...
...
```

При множестве проектов это трудоёмко и подвержено ошибкам. Нет способа одной командой обновить все проекты.

### Цель

Единая команда `task-knowledge install mass-update` для пакетного обновления всех проектов с установленной knowledge-системой.

## 2. Архитектура и границы

### Механизм обнаружения проектов

Поиск проектов осуществляется через файловую систему. Возможные стратегии:

**Стратегия A (рекомендуемая): Поиск по managed-маркеру**

```python
def discover_projects(search_roots: list[Path]) -> list[Path]:
    projects = []
    for root in search_roots:
        for agents_path in root.rglob("AGENTS.md"):
            if agents_path.is_symlink():
                continue
            content = agents_path.read_text()
            if "BEGIN_TASK_KNOWLEDGE_SYSTEM#KB01" in content:
                projects.append(agents_path.parent)
    return projects
```

`search_roots` по умолчанию:
- `~/.agents/projects/` (типичное место проектов агента).
- Можно передать через `--search-root` (повторяемый параметр).

**Стратегия B (альтернативная): Поиск по `knowledge/tasks/registry.md`**

```python
def discover_projects(search_roots: list[Path]) -> list[Path]:
    projects = []
    for root in search_roots:
        for reg_path in root.rglob("knowledge/tasks/registry.md"):
            if reg_path.is_symlink():
                continue
            projects.append(reg_path.parent.parent.parent)
    return projects
```

Более точный, но медленнее (требует обхода всей файловой системы).

**Решение**: использовать стратегию A (managed-маркер) как первичную, стратегию B как опциональную (`--search-method registry`).

### Flow обновления

```
mass-update --source-root ~/.agents/skills/task-centric-knowledge --profile generic [--dry-run] [--search-root ...]

1. discover_projects(search_roots) → projects[]
2. для каждого project в projects:
   a. preflight: managed-path safety (проверка symlink, выход за root)
   b. если dry-run: только check → запись результата
   c. иначе: check → apply --force → verify-project --force
   d. запись результата (ok/warning/error) с деталями
3. вывод сводного отчёта
```

### Обработка ошибок

| Ситуация | Действие |
|----------|----------|
| check error | Записать error, перейти к следующему проекту |
| apply error | Записать error, перейти к следующему проекту |
| verify error | Записать warning/error, перейти к следующему проекту |
| symlink в managed-path | Записать skipped, перейти к следующему |
| нет прав на запись | Записать error, перейти к следующему |

### Что остаётся вне задачи

- Автоматический commit и push (остаётся ручным шагом).
- Обнаружение проектов без knowledge-системы.
- Параллельное обновление (последовательное для безопасности).
- Обновление глобальной live-copy (это отдельный шаг `make install-global`).

### Допустимые и недопустимые связи

**Допустимые:**
- `mass_update.py` → `install_runtime` (check, install, verify_project).
- `mass_update.py` → `workflow_runtime.git_ops` (для managed-path safety).
- `cli.py` → `mass_update.py`.

**Недопустимые:**
- `mass_update.py` не должен дублировать логику install.
- `mass_update.py` не должен мутировать `pyproject.toml` или другие конфигурационные файлы проектов.

### Новые зависимости и их обоснование

`нет`

### Наблюдаемые сигналы и диагностические маркеры

- Результаты `check`/`apply`/`verify` для каждого проекта (payload из install_runtime).
- Managed-path safety violations (symlink, outside root).

## 3. Изменения данных / схемы / metadata

`нет`

## 4. Новые сущности и интерфейсы

### `task_knowledge install mass-update` CLI

```
task-knowledge install mass-update
  --source-root PATH          # Путь к source-root (live-copy)
  [--profile generic|1c]     # Фильтр профиля
  [--dry-run]                # Только check, без apply
  [--search-root PATH ...]   # Корни для поиска проектов (повторяемый)
  [--search-method agents|registry]  # Метод обнаружения
  [--json]                   # Машиночитаемый вывод
```

### `task_knowledge/install_runtime/mass_update.py`

Функции:
- `mass_update(source_root, *, profile, dry_run, search_roots, search_method) -> dict` — основная функция.
- `discover_projects(search_roots, *, search_method) -> list[Path]` — обнаружение проектов.
- `_update_project(source_root, project_root, profile, *, dry_run) -> dict` — обновление одного проекта.
- `_build_summary(results: list[dict]) -> dict` — построение сводного отчёта.

### Сводный отчёт

```json
{
  "ok": true,
  "command": "install mass-update",
  "profile": "generic",
  "dry_run": false,
  "source_root": "/home/user/.agents/skills/task-centric-knowledge",
  "projects_total": 5,
  "projects_ok": 3,
  "projects_warning": 1,
  "projects_error": 1,
  "projects_skipped": 0,
  "results": [
    {
      "project_root": "/abs/project1",
      "status": "ok",
      "check": {...},
      "apply": {...},
      "verify": {...}
    }
  ]
}
```

## 5. Изменения в существующих компонентах

### `src/task_knowledge/cli.py`

- Добавить `_add_install_mass_update_command()` в `_add_install_commands()`.
- Добавить обработчик `mass-update` в `_install()`.

### `src/task_knowledge/install_runtime/__init__.py`

- Экспортировать `mass_update`.

### `README.md`

- Добавить пример `mass-update` в секцию production rollout.

### `references/deployment.md`

- Обновить секцию production rollout с `mass-update`.

## 6. Этапы реализации и проверки

### Этап 1: Проектирование

- Определить точный механизм обнаружения проектов.
- Определить формат сводного отчёта.
- Определить edge cases (symlink, права, dirty tree).
- Verify: ревью SDD.
- Аудит: `SDD_AUDIT`.

### Этап 2: Реализация обнаружения проектов

- `discover_projects()` с поддержкой `agents` и `registry` методов.
- Verify: модульные тесты на тестовой файловой структуре.
- Аудит: `IMPLEMENTATION_AUDIT`.

### Этап 3: Реализация массового обновления

- `mass_update()` с циклом по проектам.
- `_update_project()` с check → apply → verify.
- Обработка ошибок с продолжением.
- Verify: интеграционные тесты с временными проектами.
- Аудит: `IMPLEMENTATION_AUDIT`.

### Этап 4: Интеграция в CLI

- Добавить подкоманду `mass-update` в `cli.py`.
- Реализовать `--dry-run`, `--search-root`, `--search-method`, `--json`.
- Verify: `task-knowledge install mass-update --help`.
- Аудит: `IMPLEMENTATION_AUDIT`.

### Этап 5: Тестирование

- Тесты для `discover_projects`.
- Тесты для `mass_update` с mock проектами.
- Тесты для dry-run.
- Verify: `python3 -m unittest discover -s tests -v`.
- Аудит: `IMPLEMENTATION_AUDIT`.

### Этап 6: Обновление документации

- `README.md`: пример `mass-update`.
- `references/deployment.md`: секция production rollout.
- Verify: визуальная проверка.
- Аудит: `IMPLEMENTATION_AUDIT`.

### Финальный этап: Интеграция

- Полный тестовый прогон.
- `make check`.
- Ручной тест на реальных проектах.
- Доказательство покрытия `artifacts/verification-matrix.md`.
- Аудит: `INTEGRATION_AUDIT`.

## 7. Критерии приёмки

1. `mass-update` обнаруживает все проекты с managed-блоком.
2. Каждый проект проходит check → apply → verify.
3. Ошибка в одном проекте не прерывает обработку остальных.
4. Dry-run выполняет только check.
5. Сводный отчёт содержит полную информацию.
6. `--profile` фильтрует проекты.
7. Тесты проходят.
8. Все инварианты покрыты.

## 8. Стоп-критерии

1. Обнаружение проектов даёт ложные срабатывания (не-knowledge проекты).
2. Массовое обновление повреждает project data (registry.md).
3. Managed-path safety не может быть гарантирована для всех проектов.
4. Производительность неприемлема для большого числа проектов (>100).

## Связь с остальными файлами задачи

- `task.md` — источник истины.
- `plan.md` — исполнимый план.
- `artifacts/verification-matrix.md` — матрица покрытия.
