# Verification matrix TASK-2026-0030

| Инвариант | Сценарий нарушения | Проверка/команда | Статус покрытия |
|-----------|--------------------|------------------|-----------------|
| `INV-01` | `git init` создаёт `master`, тесты ждут `main`. | Diff-аудит `git branch -M main` в temp-repo helper-ах; `python3 -m unittest discover -s tests -v`. | passed |
| `INV-02` | Две unrelated задачи на одной ветке ошибочно резолвятся или становятся `unresolved`. | `test_current_task_keeps_ambiguity_for_unrelated_tasks_on_same_branch`; targeted regression; full discover. | passed |
| `INV-03` | Parent/subtask shared branch с final noise ошибочно становится ambiguous/unresolved. | `test_current_task_prefers_non_final_candidates_on_shared_branch`; targeted regression; full discover. | passed |
| `INV-04` | CLI/test subprocess зависает и блокирует regression-run. | Diff-аудит `timeout=SUBPROCESS_TIMEOUT_SECONDS` в subprocess helper-ах; `python3 -m unittest discover -s tests -v`. | passed |
| `INV-05` | Runtime git/command helper зависает или ломает существующую модель ошибок. | Diff-аудит bounded timeout в `git_ops.py`, `grace.py`, `doctor.py`; `python3 -m unittest discover -s tests -v`; CLI smoke. | passed |
| `INV-06` | Исправление ломает импорт/синтаксис или широкий regression-контур. | `python3 -m compileall -q scripts tests`; `python3 -m unittest discover -s tests -v`. | passed |
