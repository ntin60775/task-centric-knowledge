# План задачи TASK-2026-0041

## Правило

Для задачи существует только один файл плана: `plan.md`.
Если задача декомпозируется, каждая подзадача получает свой собственный `plan.md` внутри своей папки.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0041` |
| Parent ID | `—` |
| Версия плана | `1` |
| Связь с SDD | `sdd.md` |
| Дата обновления | `2026-05-06` |

## Цель

Удалить legacy-фасады и перевести весь операторский контур на единый `task-knowledge` CLI без обратной совместимости с facade-скриптами.

## Границы

### Входит

- Удаление `scripts/install_skill.py`, `scripts/task_workflow.py`, `scripts/task_query.py`.
- Удаление legacy-ветки `--mode` из `task_knowledge_cli.py`.
- Обновление `pyproject.toml` (py-modules).
- Обновление references: `adoption.md`, `deployment.md`, `task-workflow.md`.
- Обновление `README.md`, `SKILL.md`, `Makefile`.
- Обновление тестов при необходимости.

### Не входит

- Изменение runtime-модулей.
- Изменение логики unified CLI (кроме удаления `--mode`).
- Рефакторинг package layout (это TASK-2026-0042).

## Планируемые изменения

### Код

- `scripts/install_skill.py` — удалить.
- `scripts/task_workflow.py` — удалить.
- `scripts/task_query.py` — удалить.
- `scripts/task_knowledge_cli.py` — удалить `_run_legacy_install_cli`, вызов при `--mode` в `main()`.
- `scripts/install_skill_runtime/cli.py` — проверить, нужен ли `main(argv, script_path=...)` после удаления facade; возможно удалить `script_path` параметр.

### Конфигурация / схема данных / именуемые сущности

- `pyproject.toml` — убрать `install_skill`, `task_query`, `task_workflow` из `py-modules`.

### Документация

- `references/adoption.md` — замена `python3 scripts/install_skill.py` → `task-knowledge install ...`, `python3 scripts/task_workflow.py` → `task-knowledge workflow ...`, `python3 scripts/task_query.py` → `task-knowledge task ...`.
- `references/deployment.md` — замена facade-вызовов на unified CLI.
- `references/task-workflow.md` — замена facade-вызовов на unified CLI.
- `references/task-routing.md` — проверка на наличие facade-ссылок.
- `references/upgrade-transition.md` — проверка на наличие facade-ссылок.
- `references/consumer-runtime-v1.md` — проверка на наличие facade-ссылок.
- `README.md` — удаление упоминаний facade-скриптов, актуализация примеров.
- `SKILL.md` — актуализация при необходимости.
- `Makefile` — замена целей с facade-скриптов на `task-knowledge`.

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- Удаление import-ов facade-модулей из `pyproject.toml`.
- Проверка, что тесты не импортируют facade-скрипты напрямую.

### Границы, которые должны остаться изолированными

- Runtime-модули (`install_skill_runtime/`, `task_workflow_runtime/`, etc.) не меняются.
- `scripts/install_skill_runtime/cli.py` сохраняет функцию `print_text_report` для unified CLI.

### Критический функционал

- `task-knowledge install apply/check/verify-project/doctor-deps` работают.
- `task-knowledge task status/current/show` работают.
- `task-knowledge workflow sync/backfill/finalize/publish` работают.
- `task-knowledge doctor` работает.
- `make check` проходит.
- `make install-local` и `make install-global` работают.

### Основной сценарий

1. Удалить facade-файлы и legacy-ветку `--mode`.
2. Обновить `pyproject.toml`.
3. Обновить references и документацию.
4. Обновить `Makefile`.
5. Прогнать тесты и проверки.
6. Зафиксировать результат.

### Исходный наблюдаемый симптом

`не требуется`

## Риски и зависимости

- **Зависимость от TASK-2026-0042**: если нормализация package layout ещё не выполнена, удаление facade-ов может усложнить последующий перенос runtime-модулей. Рекомендуется выполнить TASK-2026-0042 первой или как минимум синхронизировать порядок.
- **Тесты**: если тесты напрямую импортируют facade-скрипты, потребуется их обновление.
- **Внешние потребители**: если кто-то использует facade-скрипты напрямую (а не через unified CLI), удаление сломает их workflow. Нужно проверить references на наличие таких сценариев.

## Связь с SDD

- SDD: `sdd.md` — содержит инварианты, архитектуру удаления, этапы и критерии приёмки.
- Verification matrix: `artifacts/verification-matrix.md`.
- Этапы SDD:
  1. Удаление facade-файлов и legacy-ветки `--mode`.
  2. Обновление `pyproject.toml`.
  3. Обновление references и документации.
  4. Обновление `Makefile`.
  5. Тестирование и верификация.
  6. Финальный аудит.

## Проверки

### Что можно проверить кодом или тестами

- `python3 -m unittest discover -s tests -v` — полный тестовый прогон.
- `make check` — обязательный source gate.
- `python3 -m ruff check scripts/ tests/` — линтинг.
- `git diff --check` — проверка синтаксиса.
- `make install-local` — установка CLI layer.
- `task-knowledge --help` — проверка unified CLI.
- `task-knowledge doctor --project-root .` — проверка окружения.
- `task-knowledge install check --project-root .` — проверка install-контура.
- `task-knowledge task status --project-root .` — проверка read-model.
- Доказательство покрытия `artifacts/verification-matrix.md` через фактические прогоны.

### Что остаётся на ручную проверку

- Визуальная проверка references на отсутствие facade-скриптов.
- Проверка `make install-global` и `make verify-global-install`.

## Шаги

- [ ] Шаг 1: Удалить `scripts/install_skill.py`, `scripts/task_workflow.py`, `scripts/task_query.py` и legacy-ветку `--mode` в `task_knowledge_cli.py`.
- [ ] Шаг 2: Обновить `pyproject.toml`.
- [ ] Шаг 3: Обновить `references/adoption.md`, `references/deployment.md`, `references/task-workflow.md`.
- [ ] Шаг 4: Проверить и обновить `references/task-routing.md`, `references/upgrade-transition.md`, `references/consumer-runtime-v1.md`.
- [ ] Шаг 5: Обновить `README.md` и `SKILL.md`.
- [ ] Шаг 6: Обновить `Makefile`.
- [ ] Шаг 7: Обновить тесты при необходимости.
- [ ] Шаг 8: Прогнать полный тестовый набор и проверки.
- [ ] Шаг 9: Доказать покрытие verification matrix.

## Критерии завершения

- Все три facade-файла удалены.
- `pyproject.toml` чист от facade-модулей.
- Все references используют `task-knowledge`.
- `make check` зелёный.
- Полный тестовый прогон зелёный.
- `make install-local` и `task-knowledge --help` работают.
- Verification matrix полностью покрыта.
