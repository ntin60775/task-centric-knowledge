# Финальное сравнение scope с production-team snapshot

## Источник

- Архив: `/home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge-production-team-2026-04-28.zip`
- Рабочая распаковка для анализа: `/tmp/tck-prod-snapshot.RvBWEP`

## Что перенесено

- Global install safety: manifest targets со статусами `blocked-target-*` блокируют apply до любых копирований; `applied=[]`.
- User-site CLI layer: global installer вызывает wrapper-based install и проверяет symlink на wrapper и `.pth`.
- Project install safety: preflight managed targets выполняется до write-шагов, включая assets, `AGENTS.md` или snippet, migration note и repo upgrade-state.
- Workflow safety: `sync`, `backfill`, `publish`, `finalize` используют единый guard `task_dir_outside_project_root`.
- Production rollout wording: обязательный gate отделён от strict static checks; `ruff` и `mypy` описаны как `check-strict`, а не как ложный mandatory gate.
- Managed blocks generic и 1c синхронизированы по policy: verified live-copy перед project upgrade, запрет symlinked managed paths, root-boundary для mutating workflow.

## Что не перенесено

- Каталог `knowledge/` из архива и исторические task-data.
- Repo-local и transient артефакты архива.
- Wholesale overlay snapshot поверх текущего репозитория.
- Обязательный `check-production` с `ruff` и `mypy`: локальная проверка показала красный baseline и отсутствие `mypy`.

## Проверка отсутствия исходных blocker-ов

- `tests.test_global_skill_install.GlobalSkillInstallTests.test_apply_refuses_manifest_target_symlink_before_any_copy` подтверждает, что symlinked manifest target не перезаписывает victim file и не копирует остальные manifest files.
- `tests.test_install_skill.TaskCentricKnowledgeInstallerTests.test_install_rejects_symlinked_knowledge_directory_before_writing_assets` подтверждает, что project install не пишет assets через symlinked `knowledge`.
- `tests.test_task_workflow.TaskCentricKnowledgeWorkflowTests.test_workflow_mutators_reject_symlinked_task_dir_resolving_outside_project` подтверждает единый blocker `task_dir_outside_project_root` для mutating workflow.
