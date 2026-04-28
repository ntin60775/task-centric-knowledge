# Матрица проверки по задаче TASK-2026-0038

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0038` |
| Связанный SDD | `../sdd.md` |
| Версия | `1` |
| Дата обновления | `2026-04-28` |

## 1. Канонические инварианты

| Invariant ID | Описание | Источник истины | Где может сломаться |
|--------------|----------|-----------------|---------------------|
| `INV-01` | `install apply` выполняет post-install verification. | install runtime | Apply без финальной проверки. |
| `INV-02` | Все managed target files существуют. | manifest assets | Неполное копирование. |
| `INV-03` | Force-updatable templates актуальны после `--force`. | source assets | Stale templates. |
| `INV-04` | Project data сохраняется. | project data policy | Потеря registry data. |
| `INV-05` | Managed AGENTS block/snippet валиден. | profile assets | Missing/invalid agents contour. |
| `INV-06` | Verify-only режим read-only. | CLI contract | Verify мутирует проект. |
| `INV-07` | Cleanup не выполняется внутри apply/verify. | cleanup contract | Скрытое удаление. |
| `INV-08` | Docs разделяют project/global install. | README/SKILL/deployment | Оператор смешивает контуры. |

## 2. Матрица покрытия

| Invariant ID | Сценарий нарушения или переход | Автопроверка / команда | Статус покрытия | Примечание |
|--------------|--------------------------------|------------------------|-----------------|------------|
| `INV-01` | Apply возвращает ok без post-check. | `python3 -m unittest tests.test_install_skill -v`; `python3 -m unittest discover -s tests -v` | `covered` | Покрыт прямой gating-test на ошибку post-install verifier-а. |
| `INV-02` | Нет managed target file. | `python3 -m unittest tests.test_install_skill -v`; `python3 -m unittest discover -s tests -v` | `covered` | Negative verify scenario. |
| `INV-03` | Stale template после `--force`. | `python3 -m unittest tests.test_install_skill -v`; self-check `install verify-project --force` | `covered` | Проверена content parity; self-check поймал и затем закрыл stale README. |
| `INV-04` | Registry overwritten при `--force`. | `python3 -m unittest tests.test_install_skill -v`; `python3 -m unittest discover -s tests -v` | `covered` | Existing tests + verifier. |
| `INV-05` | AGENTS block/snippet отсутствует или stale. | `python3 -m unittest tests.test_install_skill -v`; `python3 -m unittest discover -s tests -v` | `covered` | Проверены managed-block и snippet scenarios. |
| `INV-06` | Verify-only меняет файлы. | `python3 -m unittest tests.test_install_skill -v`; `python3 -m unittest discover -s tests -v` | `covered` | Snapshot до/после. |
| `INV-07` | Apply/verify удаляет target-only файл. | `python3 -m unittest tests.test_install_skill -v`; `make verify-global-install` | `covered` | Target-only object сохраняется; cleanup не встроен в apply/verify. |
| `INV-08` | Docs не описывают full project flow. | `bash scripts/check-docs-localization.sh`; `git diff --check` | `covered` | README/SKILL/deployment обновлены. |

## 3. Остаточный риск и ручной остаток

- Проверка на реальном внешнем consumer repo остаётся ручным остатком до следующего рабочего обновления.
- Текущий standalone-репозиторий проверен через `install verify-project --force`, но это не заменяет отдельный внешний consumer scenario.

## 4. Правило завершения

- Задача не завершается, пока все planned-пункты не переведены в `covered` или обоснованный `manual-residual`.
