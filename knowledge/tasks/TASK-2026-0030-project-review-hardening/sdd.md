# SDD TASK-2026-0030 — project-review-hardening

## Контекст

Проект является Python CLI/runtime для task-centric knowledge. Первичное ревью выявило два класса риска:

1. Временные git-репозитории в тестах создавались через `git init` без нормализации ветки. Это делало regression-сценарии зависимыми от глобальной настройки `init.defaultBranch` и ломало проверки, где task metadata ожидает ветку `main`.
2. Ряд subprocess/git-вызовов в тестовом контуре и runtime-helper-ах выполнялся без timeout. При зависшем дочернем процессе regression-run мог блокироваться без диагностичного выхода.

## Границы изменения

### Разрешённые связи

- Тестовые helper-ы могут задавать локальную константу timeout и использовать её в `subprocess.run`.
- Runtime helper-ы могут ограничивать уже существующие локальные git/CLI subprocess-вызовы и возвращать текущую модель ошибок: `RuntimeError`, warning/error payload или `None` для невозможности получить git-состояние.

### Запрещённые связи

- Не добавлять новые runtime/package зависимости.
- Не менять публичный CLI-контракт команд, аргументов и JSON-полей без отдельной задачи.
- Не выполнять сетевые publish-действия и не добавлять сетевую интеграцию.

## Инварианты

- `INV-01`: временные git-репозитории тестов должны иметь детерминированную базовую ветку `main`, независимо от глобального `init.defaultBranch`.
- `INV-02`: две unrelated задачи на одной ветке должны оставаться ambiguous, а не переходить в `unresolved` из-за mismatch имени ветки.
- `INV-03`: parent/subtask shared-branch сценарий должен предпочитать актуальные non-final candidates и не ломаться из-за final noise.
- `INV-04`: subprocess-based тестовые helper-ы не должны блокировать regression-run бесконечно.
- `INV-05`: runtime git/command helper-ы должны иметь bounded timeout и сохранять существующую модель ошибок.
- `INV-06`: исправление не должно ломать импорт, синтаксис и полный unittest regression-контур.

## Реализация

- В `tests/task_workflow_testlib.py`, `tests/test_task_workflow.py`, `tests/test_install_skill_governance.py` и `tests/test_borrowings_runtime.py` нормализована ветка временных git-репозиториев через `git branch -M main`.
- В subprocess-based тестовых helper-ах добавлен `SUBPROCESS_TIMEOUT_SECONDS = 30`.
- В `scripts/task_workflow_runtime/git_ops.py` добавлена timeout-обработка для `run_git` и `run_command` с return code `124` при `check=False` и `RuntimeError` при `check=True`.
- В `scripts/borrowings_runtime/grace.py` добавлена timeout-обработка git status/rev-parse; при timeout helper возвращает тот же safe-failure результат, что и при невозможности получить git-состояние.
- В `scripts/install_skill_runtime/doctor.py` git diagnostics ограничены timeout и возвращают misconfigured diagnostic вместо зависания.

## Проверки

См. `artifacts/verification-matrix.md` и раздел `Стратегия проверки` в `task.md`.
