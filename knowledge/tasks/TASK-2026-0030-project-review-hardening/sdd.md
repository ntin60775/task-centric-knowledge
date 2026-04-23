# Спецификация TASK-2026-0030 — project-review-hardening

## Контекст

Проект является Python CLI/runtime для task-centric knowledge. Первичное ревью выявило два класса риска:

1. Временные git-репозитории в тестах создавались через `git init` без нормализации ветки. Это делало regression-сценарии зависимыми от глобальной настройки `init.defaultBranch` и ломало проверки, где task metadata ожидает ветку `main`.
2. Ряд subprocess/git-вызовов в тестовом контуре и runtime-helper-ах выполнялся без timeout. При зависшем дочернем процессе regression-run мог блокироваться без диагностичного выхода.
3. После первого fix-pass сохранилась ложная диагностика timeout-сценариев: `doctor` мог сообщать `не git-репозиторий` или `remote не найден`, а `git_ops` при `check=False` мог маскировать timeout под отсутствие ветки, ref или remote.
4. `finalize_flow` и `test_task_workflow_registry.py` сохраняли fail-safe пробелы: structured blocker-payload мог сорваться при повторном timeout в error-path, а isolated discover отдельного registry-test зависел от побочного `sys.path` bootstrap.

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
- `INV-07`: `doctor-deps` должен отличать timeout git-проверок от реальных `non-repo` и `missing remote` сценариев и не выдавать ложную remediation.
- `INV-08`: timeout в `run_git(..., check=False)` и `run_command(..., check=False)` должен подниматься как runtime-ошибка, а не интерпретироваться вызывающим кодом как `missing ref/branch/remote`.
- `INV-09`: local `finalize` обязан возвращать structured `git_runtime_failure` payload даже при timeout в позднем preflight, error-path и remote-проверке.
- `INV-10`: `tests/test_task_workflow_registry.py` должен запускаться standalone через `unittest discover` без скрытой зависимости от импорта других тестов.

## Реализация

- В `tests/task_workflow_testlib.py`, `tests/test_task_workflow.py`, `tests/test_install_skill_governance.py` и `tests/test_borrowings_runtime.py` нормализована ветка временных git-репозиториев через `git branch -M main`.
- В subprocess-based тестовых helper-ах добавлен `SUBPROCESS_TIMEOUT_SECONDS = 30`.
- В `scripts/task_workflow_runtime/git_ops.py` timeout-обработка ужесточена: `run_git` и `run_command` поднимают `RuntimeError` даже при `check=False`, чтобы timeout не маскировался под штатный `returncode != 0`.
- В `scripts/borrowings_runtime/grace.py` добавлена timeout-обработка git status/rev-parse; при timeout helper возвращает тот же safe-failure результат, что и при невозможности получить git-состояние.
- В `scripts/install_skill_runtime/doctor.py` git diagnostics ограничены timeout, `_git_repository_check()` различает machine-readable timeout reason и реальный `non-repo` сценарий, а `_first_remote()` больше не маскирует timeout или сбой `git remote get-url` под отсутствие remote.
- В `scripts/task_workflow_runtime/finalize_flow.py` добавлены safe-helper-ы для branch/remote failure-path и structured blocker-payload для поздних git timeout.
- `tests/test_task_workflow_registry.py` получил собственный `scripts/` bootstrap и теперь проходит isolated discover без порядка импорта.
- Добавлены регрессии `tests/test_git_ops_runtime.py`, новые doctor-сценарии в `tests/test_install_skill_governance.py` и timeout/failure-path сценарии в `tests/test_task_workflow.py`.

## Проверки

См. `artifacts/verification-matrix.md` и раздел `Стратегия проверки` в `task.md`.
