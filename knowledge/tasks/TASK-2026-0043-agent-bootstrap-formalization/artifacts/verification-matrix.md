# Матрица проверки по задаче TASK-2026-0043

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0043` |
| Связанный SDD | `../sdd.md` |
| Версия | `1` |
| Дата обновления | `2026-05-09` |

## 1. Канонические инварианты

| Invariant ID | Описание | Источник истины | Где может сломаться |
|--------------|----------|-----------------|---------------------|
| `INV-01` | Bootstrap одной командой без ручных шагов | `sdd.md §0` | Пропущенные шаги в flow |
| `INV-02` | Dry-run без мутации | `sdd.md §0` | Побочные эффекты при dry-run |
| `INV-03` | Чистый проект: установка + первая задача | `sdd.md §0` | Неполная установка |
| `INV-04` | Существующая совместимая система обновляется | `sdd.md §2` | Перезапись project data |
| `INV-05` | Чужие dirty changes не коммитятся | `sdd.md §2` | Ложное срабатывание авто-commit |
| `INV-06` | Отсутствие git — ошибка | `sdd.md §2` | NullPointer или неявное поведение |
| `INV-07` | Профиль 1c применяется корректно | `sdd.md §0` | Не тот managed-блок |
| `INV-08` | `task status` корректен после bootstrap | `sdd.md §0` | Расхождение registry |

## 2. Матрица покрытия

| Invariant ID | Сценарий нарушения или переход | Автопроверка / команда | Статус покрытия | Примечание |
|--------------|--------------------------------|------------------------|-----------------|------------|
| `INV-01` | Ручной шаг всё ещё нужен | Интеграционный тест: bootstrap + проверка `task.md` создан | `covered` | `test_bootstrap_clean_project_full` |
| `INV-02` | Dry-run мутирует файлы | `test_bootstrap_dry_run_no_mutation` | `covered` | dry-run проверяет отсутствие `knowledge/` |
| `INV-03` | Чистый проект не получает knowledge | `test_bootstrap_clean_project_full` + `task status` | `covered` | `task.md` и `plan.md` созданы, task status OK |
| `INV-04` | Совместимая система перезаписывается | `install apply --force existing_system_mode=adopt` | `covered` | Логика install использует `adopt` mode |
| `INV-05` | Чужие изменения коммитятся | `test_bootstrap_dirty_worktree_with_non_knowledge_rejects` | `covered` | preflight отклоняет non-knowledge dirty |
| `INV-06` | Не-git проект не вызывает ошибку | `test_bootstrap_non_git_error` | `covered` | Явная ошибка `git` |
| `INV-07` | Профиль 1c даёт не тот блок | Передаётся в `install`, `check`, `doctor_deps` | `manual-residual` | Требует проверки `AGENTS.md` content |
| `INV-08` | `task status` некорректен | Проверено вручную: `task status` после bootstrap | `covered` | Показывает корректный `TASK-2026-0001 · initial-setup` |

## 3. Остаточный риск и ручной остаток

- Поведение bootstrap на смешанной системе (`mixed_system`) — ручная проверка.
- Поведение bootstrap при отсутствии прав на запись.
- INV-07 (профиль `1c`) — требуется ручная проверка content `AGENTS.md`.

## 4. Правило завершения

- Все строки из `planned` перемещены в `covered` или `manual-residual`.

## 5. Доказательство покрытия

### INV-01: Bootstrap одной командой
```
$ task-knowledge bootstrap --project-root /tmp/test-project
ok=True
- [ok] git: Git repository confirmed
- [ok] worktree: Worktree is clean
- [ok] git_commit: Knowledge files committed
- [ok] doctor_deps: doctor-deps check passed
- [ok] task_dir: Created task directory
- [ok] task_files: Copied task.md template
- [ok] task_files: Copied plan.md template
- [ok] sync: Workflow synced: branch=task/task-2026-0001-initial-setup
```

### INV-02: Dry-run без мутации
```
$ task-knowledge bootstrap --project-root /tmp/test --dry-run
# knowledge/ не создан после выполнения
```

### INV-03 + INV-08: Чистый проект + task status
```
$ task-knowledge task status --project-root /tmp/test
...
Current task
TASK-2026-0001 · initial-setup
```

### INV-05: Чужие dirty отклоняются
```
$ git checkout main  # with dirty src/main.py
$ task-knowledge bootstrap
error=Worktree is dirty with non-knowledge changes
```

### INV-06: Не-git ошибка
```
$ task-knowledge bootstrap --project-root /tmp/non-git
error=fatal: не найден git репозиторий
```
