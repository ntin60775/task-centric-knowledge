# Карточка задачи TASK-2026-0030

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0030` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0030` |
| Технический ключ для новых именуемых сущностей | `project-review-hardening` |
| Краткое имя | `project-review-hardening` |
| Человекочитаемое описание | `Ревью проекта, устранение найденных недостатков и стабилизация локального тестового контура task-centric-knowledge.` |
| Справочный режим | `нет` |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `main` |
| Требуется SDD | `да` |
| Статус SDD | `подготовлен` |
| Ссылка на SDD | `knowledge/tasks/TASK-2026-0030-project-review-hardening/sdd.md` |
| Дата создания | `2026-04-22` |
| Дата обновления | `2026-04-23` |

## Цель

Провести ревью проекта, исправить обнаруженные дефекты и добавить проверки, которые фиксируют устранённые регрессии.

## Наблюдаемые симптомы

- Временные git-репозитории в тестах зависели от глобальной настройки `init.defaultBranch`; при `master` ломались сценарии `current-task`, рассчитанные на `main`.
- Часть subprocess/git-вызовов в тестах и runtime-helper-ах не имела timeout-защиты, поэтому зависший дочерний процесс мог блокировать regression-run.
- После первого review-fix цикла выяснилось, что timeout в `doctor`, `git_ops` и `finalize_flow` всё ещё может маскироваться под ложные диагнозы вроде `не git-репозиторий` / `remote не найден` / `branch/ref отсутствует` либо срывать structured `git_runtime_failure` payload.
- Изолированный запуск `test_task_workflow_registry.py` зависел от побочного `sys.path` bootstrap из других тестов и не являлся самостоятельным verify-сценарием.

## Контур публикации

Delivery unit описывает конкретную поставку через ветку и публикацию.
В одном `task.md` допускается `0..N` delivery units.

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | — | `—` | `—` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |

## Текущий этап

Локальный finalize выполнен: task-ветка влита в base-ветку, рабочий контекст переведён на base-ветку, `push` остаётся отдельным шагом.
## Стратегия проверки

### Покрывается кодом или тестами

- `python3 -m compileall -q scripts tests` — пройдено.
- `python3 -m unittest tests.test_install_skill_governance.InstallSkillGovernanceTests.test_doctor_deps_surfaces_git_timeout_without_false_non_repo_diagnostic tests.test_install_skill_governance.InstallSkillGovernanceTests.test_doctor_deps_keeps_non_repo_diagnosis_for_directory_without_git -v` — пройдено.
- `python3 -m unittest tests.test_install_skill_governance.InstallSkillGovernanceTests.test_doctor_deps_surfaces_publish_remote_timeout_without_false_missing_remote_diagnostic -v` — пройдено.
- `python3 -m unittest tests.test_install_skill_governance.InstallSkillGovernanceTests.test_doctor_deps_surfaces_broken_publish_remote_without_false_missing_remote_diagnostic -v` — пройдено.
- `python3 -m unittest tests.test_git_ops_runtime -v` — пройдено.
- `python3 -m unittest tests.test_task_workflow.TaskCentricKnowledgeWorkflowTests.test_finalize_task_reports_git_runtime_failure_when_base_branch_probe_times_out tests.test_task_workflow.TaskCentricKnowledgeWorkflowTests.test_finalize_task_reports_structured_runtime_failure_when_late_preflight_probe_times_out tests.test_task_workflow.TaskCentricKnowledgeWorkflowTests.test_finalize_task_runtime_failure_payload_survives_error_path_branch_probe_timeout -v` — пройдено.
- `python3 -m unittest discover -s tests -p 'test_task_workflow_registry.py' -v` — пройдено.
- `python3 -m unittest discover -s tests -v` — пройдено, `208` тестов за `21.098s`.
- `python3 scripts/task_query.py --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/task-centric-knowledge current-task --format json` — пройдено; `TASK-2026-0030` резолвится по ветке `task/task-2026-0030-project-review-hardening`.
- `make install-local` — пройдено.
- `~/.local/bin/task-knowledge --help` — пройдено.
- `~/.local/bin/task-knowledge task status --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/task-centric-knowledge` — пройдено; сохранились ожидаемые repo-wide warnings upgrade-governance (`legacy_backfill_pending`, `execution_rollout_partial`).
- `git diff --check` — пройдено.
- `bash scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0030-project-review-hardening/task.md knowledge/tasks/TASK-2026-0030-project-review-hardening/plan.md knowledge/tasks/TASK-2026-0030-project-review-hardening/sdd.md knowledge/tasks/TASK-2026-0030-project-review-hardening/artifacts/verification-matrix.md knowledge/tasks/registry.md` — пройдено.

### Остаётся на ручную проверку

- `не требуется` — timeout-path helper-ов, verify-артефакты и isolated regression-контур закрыты локальными проверками.
