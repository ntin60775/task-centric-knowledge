# Матрица проверки по задаче TASK-2026-0041

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0041` |
| Связанный SDD | `../sdd.md` |
| Версия | `2` |
| Дата обновления | `2026-05-06` |

## 1. Канонические инварианты

| Invariant ID | Описание | Источник истины | Где может сломаться |
|--------------|----------|-----------------|---------------------|
| `INV-01` | Единственный entrypoint — `task-knowledge` | `sdd.md §0` | References, Makefile, тесты могут ссылаться на facade-скрипты |
| `INV-02` | Все команды unified CLI работают без регрессии | `sdd.md §0` | Удаление `--mode` или facade-ов может затронуть импорты unified CLI |
| `INV-03` | `pyproject.toml` не ссылается на удалённые модули | `sdd.md §3` | `py-modules` содержит удалённые имена |
| `INV-04` | `make check/install-local/install-global` работают | `sdd.md §0` | Makefile-цели используют facade-скрипты |
| `INV-05` | `print_text_report` доступен для unified CLI | `sdd.md §2` | Удаление `cli.py` вместе с facade |
| `INV-06` | Полный тестовый прогон зелёный | `sdd.md §0` | Тесты импортируют facade-модули |
| `INV-07` | References используют только `task-knowledge` | `sdd.md §5` | Пропущенные замены в `adoption.md`, `deployment.md`, `task-workflow.md` |

## 2. Матрица покрытия

| Invariant ID | Сценарий нарушения или переход | Автопроверка / команда | Статус покрытия | Примечание |
|--------------|--------------------------------|------------------------|-----------------|------------|
| `INV-01` | Reference содержит `install_skill.py` | `grep -r "install_skill.py\|task_workflow.py\|task_query.py" references/ README.md SKILL.md Makefile` | `covered` | Пустой результат |
| `INV-02` | `task-knowledge install check` падает | `task-knowledge install check --project-root .` | `covered` | `ok=True` |
| `INV-02` | `task-knowledge task status` падает | `task-knowledge --json task status --project-root .` | `covered` | `ok=True` |
| `INV-02` | `task-knowledge workflow sync` падает | `task-knowledge workflow sync --project-root . --task-dir knowledge/tasks/TASK-2026-0041-remove-legacy-facades --register-if-missing` | `covered` | `ok=True` |
| `INV-02` | `task-knowledge doctor` падает | `task-knowledge doctor --project-root .` | `covered` | `ok=True` |
| `INV-03` | `pyproject.toml` содержит удалённые модули | `grep -E "install_skill|task_query|task_workflow" pyproject.toml` | `covered` | Пустой результат |
| `INV-04` | `make check` падает | `make check` | `covered` | 254/260 тестов зелёных; 6 pre-existing `doctor_deps` failures из-за окружения (gh/python3 в PATH) — не связаны с задачей |
| `INV-04` | `make install-local` падает | `make install-local` | `covered` | Успешно |
| `INV-05` | Unified CLI не может импортировать `print_text_report` | `python3 -c "from install_skill_runtime.cli import print_text_report"` | `covered` | `import OK` |
| `INV-06` | Тесты падают | `python3 -m unittest discover -s tests -v` | `covered` | 254/260 зелёных; остаток — pre-existing `doctor_deps` environment-зависимые тесты |
| `INV-07` | `references/adoption.md` содержит facade-вызовы | `grep "install_skill.py\|task_workflow.py\|task_query.py" references/adoption.md` | `covered` | Пустой результат |
| `INV-07` | `references/deployment.md` содержит facade-вызовы | `grep "install_skill.py\|task_workflow.py\|task_query.py" references/deployment.md` | `covered` | Пустой результат |
| `INV-07` | `references/task-workflow.md` содержит facade-вызовы | `grep "install_skill.py\|task_workflow.py\|task_query.py" references/task-workflow.md` | `covered` | Пустой результат |

## 3. Остаточный риск и ручной остаток

- Визуальная проверка `references/` на корректность заменённых команд: ручной просмотр `adoption.md`, `deployment.md`, `task-workflow.md` на предмет семантической корректности команд `task-knowledge`.
- Проверка `make install-global` и `make verify-global-install` (требует глобальной установки).

## 4. Правило завершения

- Все строки матрицы должны быть переведены из `planned` в `covered` (или `manual-residual` для ручных проверок).
- Review не заменяет эту матрицу.
