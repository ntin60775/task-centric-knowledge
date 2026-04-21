# SDD по задаче TASK-2026-0028

## Паспорт SDD

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0028` |
| Статус | `готов` |
| Версия | `1` |
| Дата обновления | `2026-04-21` |

## 0. Инварианты и verification matrix

### Полный invariant set

- `INV-01`: text formatter install helper-а корректно работает и для payload с upgrade-summary, и для payload без этих полей.
- `INV-02`: cleanup-governance no-op с `TARGET_COUNT=0` и `COUNT=0` считается валидным результатом, а не ошибкой formatter-а.
- `INV-03`: repo snapshot и установленная копия skill-а должны быть синхронизированы по фиксируемой formatter-логике.

### Связанные артефакты проверки

- `artifacts/verification-matrix.md`

## 1. Проблема и цель

### Проблема

Установленная копия `task-centric-knowledge` содержит устаревшую версию `print_text_report()`, которая безусловно читает поля `compatibility_epoch`, `upgrade_status`, `execution_rollout`, `legacy_pending_count`, `reference_manual_count`. Cleanup-payload эти поля не возвращает, из-за чего `migrate-cleanup-plan` падает с `KeyError`.

### Цель

Сделать formatter tolerant к optional upgrade-summary полям и подтвердить это на реальном no-op cleanup сценарии.

## 2. Архитектура и границы

- источник изменения: `scripts/install_skill_runtime/cli.py`;
- cleanup runtime и payload builder не меняются;
- JSON payload остаётся неизменным, правится только text surface;
- installed copy в `~/.agents/skills/task-centric-knowledge` временно синхронизируется вручную до следующего штатного обновления skill-а.

### Допустимые и недопустимые связи

- допустимо: условная печать optional полей по наличию в payload;
- недопустимо: молча добавлять фиктивные upgrade-summary поля в cleanup payload;
- недопустимо: менять cleanup fingerprint, confirm command или delete policy ради formatter-фикса.

### Новые зависимости и их обоснование

- `нет`

### Наблюдаемые сигналы и диагностические маркеры

- исходный маркер ошибки: `KeyError: 'compatibility_epoch'`;
- ожидаемый корректный сигнал: успешный text output с `TARGET_COUNT=0`, `COUNT=0`, `SAFE_DELETE=0`, `MANUAL_REVIEW=0`.

## 3. Изменения данных / схемы / metadata

- task-centric runtime schema не меняется;
- меняется только поведение text formatter-а при отсутствии части ключей в payload.

## 4. Новые сущности и интерфейсы

- новых сущностей `нет`

## 5. Изменения в существующих компонентах

- `print_text_report()` начинает печатать upgrade-summary поля только если они действительно пришли в payload.

## 6. Этапы реализации и проверки

### Этап 1: Task-local contract

- завести `task.md`, `plan.md`, `sdd.md`, `artifacts/verification-matrix.md`;
- Проверка: наличие task-артефактов и строки в `registry.md`

### Этап 2: Formatter fix

- выровнять `scripts/install_skill_runtime/cli.py` в repo snapshot и installed copy;
- Проверка: diff показывает одинаковую tolerant-логику в обеих копиях

### Этап 3: Regression verify

- выполнить `migrate-cleanup-plan` для repo snapshot и installed copy;
- выполнить localization guard и `git diff --check`;
- Проверка: нет traceback, cleanup no-op печатается корректно

## 7. Критерии приёмки

1. Установленная копия skill-а больше не падает на `migrate-cleanup-plan`.
2. Repo snapshot и installed copy синхронизированы по formatter-фиксу.
3. Verification matrix закрыта фактически прогнанными командами.

## 8. Стоп-критерии

1. Для фикса требуется менять cleanup payload schema вместо formatter-а.
2. Возникает расхождение между repo snapshot и installed copy после локального синка.
3. Localization guard или `git diff --check` не удаётся пройти без дополнительных неучтённых правок.
