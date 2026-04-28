# Матрица проверки по задаче TASK-2026-0037

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0037` |
| Связанный SDD | `../sdd.md` |
| Версия | `1` |
| Дата обновления | `2026-04-28` |

## 1. Канонические инварианты

| Invariant ID | Описание | Источник истины | Где может сломаться |
|--------------|----------|-----------------|---------------------|
| `INV-01` | Глобальная установка live-copy имеет source-controlled команду. | `Makefile`, `scripts/install_global_skill.py` | Ручной rsync вне repo. |
| `INV-02` | Live-copy deploy scope включает все required resources, включая `assets/knowledge/**`. | `scripts/install_skill_runtime/models.py`, helper manifest | Неполный sync scope. |
| `INV-03` | Repo-local/transient artifacts не попадают в live-copy. | helper exclude policy | Sync из raw working tree. |
| `INV-04` | User-site CLI и live-copy проверяются отдельно. | helper verify mode, docs | CLI из source repo маскирует live-copy дефект. |
| `INV-05` | Missing/stale required resources ловятся verify mode и тестами. | tests, helper verify | Файл есть/нет не проверен после sync. |
| `INV-06` | `task-knowledge install apply` остаётся target-project install. | docs/tests existing install runtime | Смешение install surfaces. |
| `INV-07` | Destructive cleanup live-copy не выполняется без отдельного delete-gate. | helper implementation | Небезопасный `--delete` или `rm`. |

## 2. Матрица покрытия

| Invariant ID | Сценарий нарушения или переход | Автопроверка / команда | Статус покрытия | Примечание |
|--------------|--------------------------------|------------------------|-----------------|------------|
| `INV-01` | Нет штатной команды global install. | `python3 -m unittest tests.test_global_skill_install -v`; `make install-global-dry-run` | `covered` | Makefile/helper surface закреплён. |
| `INV-02` | Live-copy без `assets/knowledge/**`. | `python3 -m unittest tests.test_global_skill_install -v`; `make verify-global-install` | `covered` | Negative scenario ловит missing asset. |
| `INV-03` | В live-copy попали `.git`, `knowledge/`, `output/`, `.codex`, pycache. | `python3 -m unittest tests.test_global_skill_install -v`; `make verify-global-install` | `covered` | Scope проверяется в temp target, target-only artifacts выводятся warning. |
| `INV-04` | CLI из source repo маскирует broken live-copy. | `make verify-global-install`; `task-knowledge --json doctor --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --source-root /home/prog7/.agents/skills/task-centric-knowledge` | `covered` | Проверяются direct-live smoke, wrapper/`.pth` и фактический `runtime_root`. |
| `INV-05` | Verify mode зелёный при missing required file. | `python3 -m unittest tests.test_global_skill_install -v`; `make verify-global-install` | `covered` | Verify mode сравнивает manifest с source repo. |
| `INV-06` | `install apply` начинает обновлять `~/.agents/skills`. | `python3 -m unittest discover -s tests -v`; docs guard | `covered` | Поверхности разделены в README/SKILL/deployment docs. |
| `INV-07` | Helper удаляет target-only файл без gate. | `python3 -m unittest tests.test_global_skill_install -v`; audit helper implementation | `covered` | Helper не удаляет target-only файлы; cleanup live-copy был выполнен отдельным delete-gate на один файл. |

## 3. Остаточный риск и ручной остаток

- `INV-04`: видимость обновлённой live-copy в новой Codex-сессии может зависеть от host cache; остаётся ручная проверка после перезапуска host-а.
- Фактически пройдено: `make install-global`, `make verify-global-install`, `python3 -m unittest discover -s tests -v`, `python3 -m compileall -q scripts tests`, `git diff --check`, `bash scripts/check-docs-localization.sh`.

## 4. Правило завершения

- Задача не завершается, пока все planned-пункты не переведены в `covered` или обоснованный `manual-residual`.
