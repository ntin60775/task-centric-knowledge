# Карточка задачи TASK-2026-0047

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0047` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0047` |
| Технический ключ для новых именуемых сущностей | `—` |
| Краткое имя | `reference-semantic-algorithm-design-integration` |
| Человекочитаемое описание | Интеграция ссылки на semantic-algorithm-design в шаблоны SDD и managed-блоки AGENTS.md. |
| Статус | `завершена` |
| Приоритет | `средний` |
| Ответственный | `не назначен` |
| Ветка | `task/task-2026-0047-reference-semantic-algorithm-design-integration` |
| Требуется SDD | `нет` |
| Статус SDD | `—` |
| Ссылка на SDD | `—` |
| Дата создания | `2026-05-07` |
| Дата обновления | `2026-05-07` |

## Цель

Добавить в task-centric-knowledge нормативную ссылку на навык `semantic-algorithm-design` в шаблоны SDD и managed-блоки `AGENTS.md` (generic и 1c).

## Границы

### Входит

- Обновление `assets/knowledge/tasks/_templates/sdd.md` — добавить примечание о семантическом моделировании.
- Обновление `assets/agents-managed-block-generic.md` — правило в контроль code-related задач.
- Обновление `assets/agents-managed-block-1c.md` — аналогичное правило для 1С-профиля.

### Не входит

- Изменение логики runtime-модулей.
- Создание новых зависимостей.

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0047-reference-semantic-algorithm-design-integration/`
- файл плана: `plan.md`

## Контур публикации

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `DU-1` | Обновление managed-шаблонов и AGENTS.md | `task/task-2026-0047-reference-semantic-algorithm-design-integration` | `main` | `none` | `none` | `merged` | `—` | `TBD` | `не требуется` |

## Текущий этап

Задача завершена. Managed-шаблоны обновлены, ссылка на `semantic-algorithm-design` добавлена в SDD-шаблон и managed-блоки AGENTS.md (generic и 1c).

## Стратегия проверки

### Покрывается кодом или тестами

- `bash scripts/check-docs-localization.sh` — проверка локализации обновлённых артефактов.

### Остаётся на ручную проверку

- Визуальная проверка обновлённых шаблонов на корректность ссылки.

## Итоговый список ручных проверок

- [x] Проверка шаблона `sdd.md` на наличие ссылки на `semantic-algorithm-design`.
- [x] Проверка managed-блоков generic и 1c на наличие правила про семантическое моделирование.

## Итог

Managed-шаблоны `sdd.md`, `agents-managed-block-generic.md` и `agents-managed-block-1c.md` обновлены: добавлена нормативная ссылка на `semantic-algorithm-design`. Ветка слита в `main`.
