# Матрица проверки по задаче TASK-2026-0042

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0042` |
| Связанный SDD | `../sdd.md` |
| Версия | `1` |
| Дата обновления | `2026-05-06` |

## 1. Канонические инварианты

| Invariant ID | Описание | Источник истины | Где может сломаться |
|--------------|----------|-----------------|---------------------|
| `INV-01` | Все runtime-модули доступны через `task_knowledge.*` | `sdd.md §0` | Неполный перенос, битые импорты |
| `INV-02` | `pyproject.toml` использует src-layout | `sdd.md §3` | Некорректная конфигурация setuptools |
| `INV-03` | Unified CLI работает после переноса | `sdd.md §0` | Битые импорты в cli.py |
| `INV-04` | Внутренние импорты используют `task_knowledge.*` | `sdd.md §5` | Пропущенные старые импорты |
| `INV-05` | `make install-local` работает | `sdd.md §0` | Некорректный `pyproject.toml` |
| `INV-06` | `make check` и тесты проходят | `sdd.md §0` | Битые тесты, несовместимость |
| `INV-07` | `install_global_skill.py` копирует из `src/` | `sdd.md §5` | Устаревшие пути |
| `INV-08` | `ruff` и `mypy` проходят на `src/` | `sdd.md §0` | Несоответствие конфигурации |

## 2. Матрица покрытия

| Invariant ID | Сценарий нарушения или переход | Автопроверка / команда | Статус покрытия | Примечание |
|--------------|--------------------------------|------------------------|-----------------|------------|
| `INV-01` | Пакет не импортируется | `python3 -c "import task_knowledge; print(task_knowledge.__version__)"` | `planned` | |
| `INV-01` | `install_runtime` не импортируется | `python3 -c "from task_knowledge.install_runtime import check"` | `planned` | |
| `INV-01` | `workflow_runtime` не импортируется | `python3 -c "from task_knowledge.workflow_runtime import sync_task"` | `planned` | |
| `INV-01` | `borrowings_runtime` не импортируется | `python3 -c "from task_knowledge.borrowings_runtime import read_status"` | `planned` | |
| `INV-02` | `pyproject.toml` ссылается на `scripts` | `grep '"scripts"' pyproject.toml` | `planned` | Должен найти только `scripts` как `[project.scripts]` |
| `INV-02` | `package-dir` не `src` | `grep -A1 'package-dir' pyproject.toml` | `planned` | Должен показать `"" = "src"` |
| `INV-03` | CLI не запускается | `task-knowledge --help` | `planned` | |
| `INV-03` | `install check` падает | `task-knowledge install check --project-root .` | `planned` | |
| `INV-03` | `task status` падает | `task-knowledge task status --project-root . --format json` | `planned` | |
| `INV-03` | `doctor` падает | `task-knowledge doctor --project-root .` | `planned` | |
| `INV-04` | Старые импорты остались | `grep -r "from install_skill_runtime\|from task_workflow_runtime\|from module_core_runtime\|from borrowings_runtime" src/` | `planned` | Должен вернуть пустой результат (или только абсолютные ссылки) |
| `INV-05` | `make install-local` падает | `make install-local` | `planned` | |
| `INV-06` | Тесты падают | `python3 -m unittest discover -s tests -v` | `planned` | |
| `INV-06` | `make check` падает | `make check` | `planned` | |
| `INV-07` | `install_global_skill.py` копирует из `scripts/` | `grep "scripts/task_knowledge" scripts/install_global_skill.py` | `planned` | Должен вернуть пустой результат |
| `INV-08` | `ruff` падает | `python3 -m ruff check src/ tests/` | `planned` | |
| `INV-08` | `mypy` падает | `python3 -m mypy src/` | `planned` | Только если mypy установлен |

## 3. Остаточный риск и ручной остаток

- Визуальная проверка структуры `src/task_knowledge/` на полноту переноса.
- Проверка `make install-global` и `make verify-global-install`.

## 4. Правило завершения

- Все строки матрицы из `planned` в `covered` (или `manual-residual`).
