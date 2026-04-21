# Карточка задачи TASK-2026-0012

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0012` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0012` |
| Технический ключ для новых именуемых сущностей | `vnext-governance` |
| Краткое имя | `task-centric-vnext-doctor-cleanup-governance` |
| Человекочитаемое описание | `Governance-слой `doctor-deps` и `migrate-cleanup-plan/confirm` для vNext task-centric-knowledge` |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `task/task-2026-0012-task-centric-vnext-doctor-cleanup-governance` |
| Требуется SDD | `да` |
| Статус SDD | `завершено` |
| Ссылка на SDD | `sdd.md` |
| Дата создания | `2026-04-12` |
| Дата обновления | `2026-04-13` |

## Цель

Реализовать отдельный safety-oriented governance-слой для `doctor-deps` и `migrate-cleanup-plan/confirm`,
чтобы install/upgrade-контур `task-centric-knowledge` стал предсказуемым, диагностируемым и безопасным для project data.

## Границы

### Входит

- классификация зависимостей `required`, `conditional`, `optional`, `not-applicable`;
- различение блокеров `core/local mode` и `publish/integration`;
- реализация `migrate-cleanup-plan` и `migrate-cleanup-confirm`;
- scope-lock, абсолютные пути, `TARGETS`, `TARGET_COUNT`, `COUNT`, `plan_fingerprint`;
- сохранение текущего поведения `check/install`;
- диагностические сообщения install/upgrade-контура.

### Не входит

- массовое upgrade tooling за пределами governance-слоя;
- автоматическое удаление project data без плана;
- memory-layer и operator read-model;
- расширение publish-host parity.

## Контекст

- источник постановки: Track 3 из `TASK-2026-0008`;
- зависимость: `TASK-2026-0010` зафиксировала core governance-инварианты, а `TASK-2026-0011` вынесла runtime helper-а в модульный пакет;
- transport-layer сознательно закреплён внутри `scripts/install_skill.py`, а не в отдельном unified CLI;
- auto-delete v1 ограничен только installer-generated артефактами и не охватывает foreign-system cleanup.

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | `scripts/install_skill.py`, новый пакет `scripts/install_skill_runtime/`, installer tests |
| Governance | каталог зависимостей, cleanup allowlist, scope-lock |
| Safety | fingerprint-confirm, раскрытие абсолютных путей, защита project data |
| Документация | `SKILL.md`, deployment/upgrade refs и task-артефакты |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0012-task-centric-vnext-doctor-cleanup-governance/`
- файл плана: `plan.md`
- файл SDD: `sdd.md`
- матрица проверки: `artifacts/verification-matrix.md`
- стратегический источник: `knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/strategy-roadmap.md`

## Контур публикации

Delivery unit для этой локальной реализации не использовался.

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | — | `—` | `—` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |

## Текущий этап

Реализация завершена:
`install_skill.py` оставлен тонким facade-entrypoint,
install/upgrade governance вынесен в пакет `scripts/install_skill_runtime/`,
добавлены режимы `doctor-deps`, `migrate-cleanup-plan`, `migrate-cleanup-confirm`,
а cleanup-governance ограничен явным allowlist и fingerprint-confirm flow.

## Стратегия проверки

### Покрывается кодом или тестами

- `python3 -m unittest skills-global/task-centric-knowledge/tests/test_install_skill.py`;
- `python3 -m unittest skills-global/task-centric-knowledge/tests/test_install_skill_governance.py`;
- `python3 -m unittest skills-global/task-centric-knowledge/tests/test_install_skill_architecture.py`;
- `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'`;
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules --mode doctor-deps --format json`;
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules --mode migrate-cleanup-plan --format json`;
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --help`;
- `git diff --check`;
- `scripts/check-docs-localization.sh` по изменённым Markdown-файлам задачи и skill-а.

### Остаётся на ручную проверку

- `не требуется`, если автоматический verify-контур и smoke-проверки CLI зелёные.

## Критерии готовности

- `install_skill.py` перестал быть install/governance-монолитом и выполняет только bootstrap, compatibility re-export и CLI-dispatch;
- `doctor-deps` даёт разделение по классам зависимостей и слоям блокировки без ложного падения `core/local mode` из-за отсутствия publish-инструментов;
- `migrate-cleanup-plan` раскрывает только allowlist v1, абсолютные пути, `TARGETS`, `TARGET_COUNT`, `COUNT`, `plan_fingerprint` и точную confirm-команду;
- `migrate-cleanup-confirm` требует `--confirm-fingerprint` и `--yes`, пересчитывает scope и не допускает его расширения;
- verification matrix переведена в `covered` по всем инвариантам.

## Итоговый список ручных проверок

- `не требуется`

## Итог

Governance-контур install/upgrade вынесен в отдельный runtime-пакет `scripts/install_skill_runtime/`
с модулями `models`, `environment`, `doctor`, `cleanup`, `cli`.

`doctor-deps` реализует dependency catalog с различением `core/local mode` и `publish/integration`,
а `migrate-cleanup-plan/confirm` теперь работает только через явный plan/fingerprint/confirm flow
и не удаляет `project data` или foreign-system контуры автоматически.

Существующее поведение `check/install` сохранено,
а новый verify-контур подтверждён полным discover-набором, отдельными governance/architecture тестами,
CLI smoke-проверками и локализационным guard.
