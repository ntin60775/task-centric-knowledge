# Acceptance summary по классам сред

## Сводная таблица

| Среда | Класс | Результат | Ключевые подтверждения |
|-------|-------|-----------|------------------------|
| `ui-ux-pro-max-skill-clean` | `clean/generic` | `pass with documented bootstrap caveat` | `install` и `doctor-deps` проходят; snippet-flow при отсутствии `AGENTS.md` подтверждён; первая задача успешно materialized через ручную `task/...` ветку и `task_workflow.py --register-if-missing`; `current-task` и `task show` работают |
| `druzhina-mixed` | `mixed_system/generic` | `pass` | `install --existing-system-mode migrate` materializes managed-блок и `MIGRATION-SUGGESTION.md`; `doctor-deps` без блокеров; `migrate-cleanup-plan` даёт `target_count=0` и `manual_review=docs/roadmap`; read-model остаётся warning-first на `main` |
| `erp-compatible-1c` | `compatible/1c` | `pass with sparse-checkout pattern` | `install --force --profile 1c` обновляет managed-файлы и сохраняет `registry.md`; `doctor-deps --profile 1c` без блокеров; `migrate-cleanup-plan --profile 1c` ограничен одним allowlist-target; read-model честно поднимает ambiguity на shared `main` |

## Общий вердикт

- Track 5 закрыт положительно: skill проверен на трёх репрезентативных классах сред.
- Adoption package воспроизводим, но clean-bootstrap первой задачи требует явного порядка и не должен описываться как полностью автоматический.
- Governance слой ведёт себя безопасно: `project data` не попадает в auto-delete, а cleanup остаётся в модели `plan -> confirm`.
- Read-model на shared `main` остаётся предсказуемым: ambiguity и legacy warnings наблюдаемы и не превращаются в молчаливый выбор активной задачи.
