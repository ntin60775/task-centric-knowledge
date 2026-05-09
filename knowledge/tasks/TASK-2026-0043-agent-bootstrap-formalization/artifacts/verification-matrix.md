# Матрица проверки по задаче TASK-2026-0043

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0043` |
| Связанный SDD | `../sdd.md` |
| Версия | `2` |
| Дата обновления | `2026-05-09` |

## 0. Semantic model validation

Семантическая модель bootstrap flow валидирована через `semantic_model_validator.py`:
- **Статус**: `pass` (ошибок: 0, предупреждений: 0)
- **Модель**: `semantic-model-bootstrap.json`
- **Инварианты**: 8 подтверждены валидатором
- **Переходов**: 14 (из них 4 терминальных)
- **Edge cases**: 18, все покрыты (`modeled: true`)

### Наблюдаемые сигнатуры

| Сигнатура | Описание |
|-----------|----------|
| `bootstrap_preflight_git_missing` | проект не является git-репозиторием |
| `bootstrap_preflight_dirty_non_knowledge` | дерево грязное чужими изменениями |
| `bootstrap_install_success` | install check + apply завершены успешно |
| `bootstrap_doctor_deps_ok` | doctor-deps не обнаружил проблем |
| `bootstrap_auto_commit_done` | knowledge-файлы закоммичены автоматически |
| `bootstrap_first_task_created` | первая задача создана из шаблонов |
| `bootstrap_sync_success` | workflow sync завершён успешно |
| `bootstrap_error` | любая ошибка в процессе |

## 1. Канонические инварианты

| Invariant ID | Описание | Источник истины | Где может сломаться |
|--------------|----------|-----------------|---------------------|
| `INV-01` | Bootstrap одной командой без ручных шагов | `sdd.md §0`, `semantic-model-bootstrap.json` | Modeled: T0→T12 полный цикл | `covered` | Подтверждено валидатором |
| `INV-02` | Dry-run без мутации | `sdd.md §0`, `semantic-model-bootstrap.json` | Modeled: T8 skip commit при dry_run | `covered` | Подтверждено валидатором |
| `INV-03` | Чистый проект: установка + первая задача | `sdd.md §0`, `semantic-model-bootstrap.json` | Modeled: T0→T1→T4→T9→T10→T12 | `covered` | Подтверждено валидатором |
| `INV-04` | Совместимая система обновляется | `sdd.md §2`, `semantic-model-bootstrap.json` | Modeled: T1 condition 'compatible' | `covered` | Подтверждено валидатором |
| `INV-05` | Чужие dirty changes не коммитятся | `sdd.md §2`, `semantic-model-bootstrap.json` | Modeled: T7 abort при non-knowledge dirty | `covered` | Подтверждено валидатором |
| `INV-06` | Отсутствие git — ошибка | `sdd.md §2`, `semantic-model-bootstrap.json` | Modeled: T3 abort при не-git | `covered` | Подтверждено валидатором |
| `INV-07` | Профиль 1c применяется корректно | `sdd.md §0`, `semantic-model-bootstrap.json` | Modeled: EC-07, EC-08 | `covered` | Подтверждено валидатором |
| `INV-08` | `task status` корректен после bootstrap | `sdd.md §0`, `semantic-model-bootstrap.json` | Modeled: ST_success postcondition | `covered` | Подтверждено валидатором |

## 2. Матрица покрытия

| Invariant ID | Сценарий нарушения или переход | Автопроверка / команда | Статус покрытия | Примечание |
|--------------|--------------------------------|------------------------|-----------------|------------|
| `INV-01` | Ручной шаг всё ещё нужен | Интеграционный тест: bootstrap в `/tmp/test` | `covered` | Semantic model + unit тесты |
| `INV-02` | Dry-run мутирует файлы | `task-knowledge bootstrap --dry-run` + проверка отсутствия файлов | `covered` | Semantic model подтверждает T8 |
| `INV-03` | Чистый проект не получает knowledge | Интеграционный тест: bootstrap + `task-knowledge task status` | `covered` | Semantic model подтверждает T9→T10→T12 |
| `INV-04` | Совместимая система перезаписывается | Тест: повторный bootstrap на проекте с knowledge | `covered` | Semantic model T1 condition |
| `INV-05` | Чужие изменения коммитятся | Тест: bootstrap при наличии `src/main.py` (dirty) | `covered` | Semantic model подтверждает T7 |
| `INV-06` | Не-git проект не вызывает ошибку | Тест: bootstrap в не-git каталоге | `covered` | Semantic model подтверждает T3 |
| `INV-07` | Профиль 1c даёт не тот блок | Тест: bootstrap `--profile 1c` + проверка `AGENTS.md` | `covered` | Semantic model EC-07, EC-08 |
| `INV-08` | `task status` некорректен | `task-knowledge task status --project-root /tmp/test --format json` | `covered` | Semantic model ST_success postcondition |

## 3. Остаточный риск и ручной остаток

- Поведение bootstrap на смешанной системе (`mixed_system`) — ручная проверка.
- Поведение bootstrap при отсутствии прав на запись.

## 4. Правило завершения

- Все строки из `planned` в `covered` (или `manual-residual`).
