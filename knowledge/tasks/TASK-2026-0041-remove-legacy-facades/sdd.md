# SDD по задаче TASK-2026-0041

## Паспорт SDD

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0041` |
| Статус | `черновик` |
| Версия | `1` |
| Дата обновления | `2026-05-06` |

## 0. Инварианты и verification matrix

### Полный invariant set

- `INV-01`: Unified CLI `task-knowledge` является единственным операторским entrypoint. Ни один reference, Makefile-цель или тест не вызывает facade-скрипты напрямую.
- `INV-02`: Все существующие команды unified CLI работают без регрессии после удаления facade-ов: `install`, `task`, `workflow`, `module`, `file`, `borrowings`, `doctor`.
- `INV-03`: `pyproject.toml` не содержит ссылок на удалённые facade-модули (`install_skill`, `task_query`, `task_workflow`).
- `INV-04`: `make check`, `make install-local`, `make install-global` выполняются без ошибок после удаления.
- `INV-05`: `scripts/install_skill_runtime/cli.py` сохраняет функцию `print_text_report`, используемую unified CLI.
- `INV-06`: Тестовый набор (`python3 -m unittest discover -s tests -v`) проходит полностью.
- `INV-07`: References (`adoption.md`, `deployment.md`, `task-workflow.md`) содержат только вызовы `task-knowledge`, а не `python3 scripts/*.py`.

### Связанные артефакты проверки

- `artifacts/verification-matrix.md` — матрица `инвариант -> сценарий нарушения -> проверка/команда -> статус покрытия`.

## 1. Проблема и цель

### Проблема

После внедрения unified CLI `task-knowledge` (TASK-2026-0037) три legacy-фасада сохраняются как обратносовместимый слой:

- `scripts/install_skill.py` (60 строк) — тонкая обёртка над `install_skill_runtime`.
- `scripts/task_workflow.py` (31 строка) — тонкая обёртка над `task_workflow_runtime`.
- `scripts/task_query.py` (18 строк) — тонкая обёртка над `task_workflow_runtime.query_cli`.

Кроме того, unified CLI содержит legacy-ветку `--mode`, которая делегирует вызов в старый `install_skill_runtime.cli.main()`.

Наличие этих фасадов:
- создаёт множественность entrypoint'ов, путающую операторов;
- усложняет `pyproject.toml`, который вынужден перечислять facade-модули;
- заставляет references поддерживать два способа вызова;
- увеличивает поверхность для ошибок (facade может разойтись с runtime).

### Цель

Единственным операторским entrypoint должен быть `task-knowledge`. Все facade-скрипты удаляются, legacy-ветка `--mode` удаляется, документация переводится на unified CLI.

## 2. Архитектура и границы

### Текущая архитектура (до)

```
operator → scripts/install_skill.py → install_skill_runtime
operator → scripts/task_workflow.py → task_workflow_runtime
operator → scripts/task_query.py    → task_workflow_runtime.query_cli
operator → task-knowledge           → unified CLI → runtime modules
operator → task-knowledge --mode ... → legacy install_skill_runtime.cli.main()
```

### Целевая архитектура (после)

```
operator → task-knowledge → unified CLI → runtime modules
```

### Что остаётся вне задачи

- Runtime-модули не меняются.
- `scripts/install_skill_runtime/cli.py` сохраняется, так как unified CLI использует `print_text_report` из него.
- `scripts/install_global_skill.py` не трогается — это отдельный скрипт глобальной установки.
- `scripts/task_knowledge_cli.py` остаётся основным entrypoint, меняется только удаление legacy-ветки.

### Допустимые и недопустимые связи

новых допустимых связей нет.

Недопустимые связи:
- Ни один модуль не должен импортировать facade-скрипты (`install_skill`, `task_workflow`, `task_query`) как модули.
- `pyproject.toml` не должен ссылаться на удалённые модули.
- References не должны содержать вызовы `python3 scripts/*.py` для facade-скриптов.

### Новые зависимости и их обоснование

`нет`

### Наблюдаемые сигналы и диагностические маркеры

`не требуется`

## 3. Изменения данных / схемы / metadata

- `pyproject.toml`: удалить `"install_skill"`, `"task_query"`, `"task_workflow"` из `py-modules`.

## 4. Новые сущности и интерфейсы

`нет`

## 5. Изменения в существующих компонентах

### `scripts/task_knowledge_cli.py`

- Удалить функцию `_run_legacy_install_cli` и вызов этой функции в `main()` при обнаружении `--mode` в `argv`.
- Удалить импорт `from install_skill_runtime.cli import main as legacy_install_main` и `from install_skill_runtime.cli import print_text_report as print_install_text_report` (последний нужен — проверить используется ли).
- После: функция `main()` начинается с парсинга аргументов без проверки на `--mode`.

### `scripts/install_skill_runtime/cli.py`

- Проверить, используется ли `main(argv, script_path=...)` где-либо кроме facade (который удаляется).
- Если `script_path` параметр больше не нужен, упростить сигнатуру `main()`.

### `pyproject.toml`

Было:
```toml
py-modules = ["install_skill", "task_query", "task_workflow", "task_knowledge_cli"]
```

Стало:
```toml
py-modules = ["task_knowledge_cli"]
```

### `references/adoption.md`

Все вызовы `python3 scripts/install_skill.py` заменить на `task-knowledge install ...`.
Все вызовы `python3 scripts/task_workflow.py` заменить на `task-knowledge workflow ...`.
Все вызовы `python3 scripts/task_query.py` заменить на `task-knowledge task ...`.

Пример замены:
```bash
# Было
python3 scripts/install_skill.py --project-root /abs/project --mode check
# Стало
task-knowledge install check --project-root /abs/project
```

### `references/deployment.md`

Аналогичная замена facade-ссылок на unified CLI.

### `references/task-workflow.md`

Аналогичная замена facade-ссылок на unified CLI.

### `README.md`

- Удалить упоминания facade-скриптов.
- Все примеры должны использовать `task-knowledge`.

### `Makefile`

- Проверить все цели на использование `python3 scripts/install_skill.py`, `python3 scripts/task_workflow.py`, `python3 scripts/task_query.py`.
- Заменить на соответствующие вызовы `task-knowledge`.

### Тесты

- Проверить `tests/` на прямые импорты facade-модулей.
- При обнаружении — обновить на импорты из runtime-модулей.

## 6. Этапы реализации и проверки

### Этап 1: Удаление facade-файлов и legacy-ветки

- Удалить `scripts/install_skill.py`.
- Удалить `scripts/task_workflow.py`.
- Удалить `scripts/task_query.py`.
- Удалить `_run_legacy_install_cli()` и legacy-ветку `--mode` из `scripts/task_knowledge_cli.py`.
- Проверить `scripts/install_skill_runtime/cli.py` на возможность упрощения `main()`.
- Verify: `git diff --check`, `python3 -m ruff check scripts/`
- Аудит: `IMPLEMENTATION_AUDIT`

### Этап 2: Обновление pyproject.toml

- Убрать `install_skill`, `task_query`, `task_workflow` из `py-modules`.
- Verify: `python3 -c "import task_knowledge_cli"` (должен работать).
- Аудит: `IMPLEMENTATION_AUDIT`

### Этап 3: Обновление references

- `references/adoption.md`: полный перевод на `task-knowledge`.
- `references/deployment.md`: полный перевод на `task-knowledge`.
- `references/task-workflow.md`: полный перевод на `task-knowledge`.
- Проверить `references/task-routing.md`, `references/upgrade-transition.md`, `references/consumer-runtime-v1.md` на facade-ссылки.
- Verify: `grep -r "install_skill.py\|task_workflow.py\|task_query.py" references/` должен вернуть пустой результат (или только исторические упоминания).
- Аудит: `IMPLEMENTATION_AUDIT`

### Этап 4: Обновление README, SKILL.md и Makefile

- `README.md`: обновить все примеры.
- `SKILL.md`: проверить и обновить при необходимости.
- `Makefile`: обновить цели.
- Verify: `grep -r "install_skill.py\|task_workflow.py\|task_query.py" README.md SKILL.md Makefile` — пустой результат.
- Аудит: `IMPLEMENTATION_AUDIT`

### Этап 5: Обновление тестов

- Проверить тесты на прямые импорты facade-модулей.
- Обновить при необходимости.
- Verify: `python3 -m pytest tests/ -x --tb=short` (или unittest).
- Аудит: `IMPLEMENTATION_AUDIT`

### Финальный этап: Интеграция

- Полный тестовый прогон: `python3 -m unittest discover -s tests -v`.
- `make check` — обязательный source gate.
- `make install-local` — установка CLI layer.
- `task-knowledge --help` — проверка unified CLI.
- `task-knowledge doctor --project-root .` — проверка окружения.
- `task-knowledge install check --project-root .` — проверка install-контура.
- `task-knowledge task status --project-root . --format json` — проверка read-model.
- `task-knowledge workflow sync --project-root . --task-dir knowledge/tasks/TASK-2026-0041-remove-legacy-facades --register-if-missing` — проверка workflow.
- Доказательство покрытия `artifacts/verification-matrix.md`.
- Verify: все команды выше должны вернуть `ok: true`.
- Аудит: `INTEGRATION_AUDIT`

## 7. Критерии приёмки

1. Три facade-файла удалены из `scripts/`.
2. `pyproject.toml` не содержит `install_skill`, `task_query`, `task_workflow` в `py-modules`.
3. `task_knowledge_cli.py` не содержит `_run_legacy_install_cli` и проверки на `--mode`.
4. `references/adoption.md`, `references/deployment.md`, `references/task-workflow.md` не содержат вызовов `python3 scripts/*.py`.
5. `README.md` и `SKILL.md` не упоминают facade-скрипты как действующий интерфейс.
6. `Makefile` цели используют `task-knowledge`, а не facade-скрипты.
7. `make check` проходит без ошибок.
8. `make install-local` завершается успешно, `task-knowledge --help` работает.
9. Полный тестовый прогон (`python3 -m unittest discover -s tests -v`) зелёный.
10. Все инварианты из verification matrix покрыты и доказаны.

## 8. Стоп-критерии

1. Обнаружены внешние зависимости от facade-скриптов, которые нельзя безопасно обновить.
2. Тесты ломаются и не могут быть исправлены без изменения runtime-модулей.
3. `make install-global` или `make verify-global-install` ломаются.
4. Любой инвариант не может быть доказан в рамках задачи.

## Связь с остальными файлами задачи

- `task.md` — источник истины по статусу и границам задачи.
- `plan.md` — исполнимый план и ссылки на этапы SDD.
- `artifacts/verification-matrix.md` — доказательная матрица покрытия инвариантов.
- `worklog.md` — фиксация прохождения этапов.
- `decisions.md` — осознанные отклонения от SDD.
