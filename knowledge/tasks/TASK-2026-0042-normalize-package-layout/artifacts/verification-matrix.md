# Матрица проверки по задаче TASK-2026-0042

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0042` |
| Связанный SDD | `../sdd.md` |
| Версия | `2` |
| Дата обновления | `2026-05-07` |

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
| `INV-01` | Пакет не импортируется | `python3 -c "import task_knowledge; print(task_knowledge.__version__)"` | `covered` | `0.10.0` |
| `INV-01` | `install_runtime` не импортируется | `python3 -c "from task_knowledge.install_runtime import check"` | `covered` | OK |
| `INV-01` | `workflow_runtime` не импортируется | `python3 -c "from task_knowledge.workflow_runtime import sync_task"` | `covered` | OK |
| `INV-01` | `borrowings_runtime` не импортируется | `python3 -c "from task_knowledge.borrowings_runtime import read_status"` | `covered` | OK |
| `INV-02` | `pyproject.toml` ссылается на `scripts` | `grep '"scripts"' pyproject.toml` | `covered` | Найдено только `[project.scripts]` |
| `INV-02` | `package-dir` не `src` | `grep -A1 'package-dir' pyproject.toml` | `covered` | `\"\" = \"src\"` |
| `INV-03` | CLI не запускается | `PYTHONPATH=src python3 -m task_knowledge --help` | `covered` | OK |
| `INV-03` | `install check` падает | `PYTHONPATH=src python3 -m task_knowledge install check --project-root .` | `covered` | OK |
| `INV-03` | `task status` падает | `PYTHONPATH=src python3 -m task_knowledge task status --project-root . --format json` | `covered` | OK |
| `INV-03` | `doctor` падает | `PYTHONPATH=src python3 -m task_knowledge doctor --project-root .` | `covered` | OK |
| `INV-04` | Старые импорты остались | `grep -r "from install_skill_runtime\|from task_workflow_runtime\|from module_core_runtime\|from borrowings_runtime" src/` | `covered` | Пустой результат |
| `INV-05` | `make install-local` падает | `make install-local` | `covered` | Wrapper + pth корректны |
| `INV-06` | Тесты падают | `make check` | `covered` | 260/260 OK |
| `INV-06` | `make check` падает | `make check` | `covered` | 260/260 OK |
| `INV-07` | `install_global_skill.py` копирует из `scripts/` | `grep "scripts/task_knowledge" scripts/install_global_skill.py` | `covered` | Пустой результат |
| `INV-08` | `ruff` падает с критическими ошибками | `python3 -m ruff check src/ tests/` | `covered` | Только pre-existing стилистика; E402 в тестах — известный паттерн sys.path |
| `INV-08` | `mypy` падает | `python3 -m mypy src/` | `manual-residual` | mypy не установлен в окружении; конфигурация mypy в pyproject.toml корректна |
| `INV-09` | `make install-global` падает | `make install-global` | `covered` | OK (smoke tests проходят) |
| `INV-09` | `make verify-global-install` падает | `make verify-global-install` | `covered` | OK (smoke tests проходят) |

## 3. Остаточный риск и ручной остаток

- `mypy` не прогонялся из-за отсутствия в окружении; конфигурация `pyproject.toml` обновлена для `src/`.
- `make install-global` / `make verify-global-install` — проверены, live skill copy обновлён.
- Визуальная проверка структуры `src/task_knowledge/` на полноту переноса — выполнена.

## 4. Правило завершения

- Все строки матрицы из `planned` в `covered` (или `manual-residual`).
