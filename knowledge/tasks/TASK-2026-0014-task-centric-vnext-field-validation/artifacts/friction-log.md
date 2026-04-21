# Журнал friction по field validation

| ID | Сигнал | Где проявился | Evidence | Классификация | Решение |
|----|--------|---------------|----------|---------------|---------|
| `FR-001` | `task_workflow.py --create-branch` останавливается на dirty tree после `install` и создания первых task-файлов | `clean/generic` | JSON-ошибка helper: `Рабочее дерево грязное; автоматическое переключение task-ветки остановлено.` | `documentation fix + roadmap signal` | Публично задокументирован validated bootstrap: ручная `task/...` ветка + `--register-if-missing`; сигнал возвращён в roadmap как кандидат на future simplification first-task bootstrap |
| `FR-002` | При отсутствии `AGENTS.md` installer создаёт snippet-файл, а не управляет файлом напрямую | `clean/generic` | создан `AGENTS.task-centric-knowledge.generic.md` | `expected behavior` | Добавлено явное описание snippet-flow в adoption docs |
| `FR-003` | Полный checkout bulky `1c`-репозитория в `tmpfs` не нужен и может упереться в объём среды | предварительная попытка с `ERP` | checkout в `/tmp` завершился `fatal: unable to checkout working tree`; `df -h /tmp` показал заполненный `tmpfs` | `documentation fix + roadmap signal` | Зафиксирован pattern non-tmpfs sparse validation для governance/adoption сценариев больших `1c`-репозиториев |
| `FR-004` | `current-task` на shared `main` возвращает `ambiguous/branch_tie` и поднимает legacy warnings | `mixed_system/generic`, `compatible/1c` | `task_query status/current-task --format json` | `expected behavior` | Документация явно закрепляет warning-first semantics и отсутствие молчаливого выбора задачи |
| `FR-005` | `mixed_system` cleanup-plan не выдаёт auto-delete targets и оставляет legacy-контур в `manual_review` | `mixed_system/generic` | `target_count=0`, `count=0`, `manual_review=docs/roadmap` | `expected behavior` | Зафиксировано как корректный governance outcome без cleanup-confirm |
| `FR-006` | `compatible` cleanup-plan показывает ровно один allowlist-target `knowledge/MIGRATION-SUGGESTION.md` | `compatible/1c` | `target_count=1`, `count=1`, `scope_locked=true` | `expected behavior` | Добавлено в adoption docs как пример безопасного allowlist cleanup для upgrade-среды |

## Подтверждённые сигналы для roadmap

- упростить или лучше направить bootstrap первой задачи после clean install;
- считать sparse/non-tmpfs validation для больших `1c`-репозиториев поддержанным operational pattern;
- сохранять warning-first политику read-model на shared `main` и не добавлять молчаливый auto-pick задачи.
