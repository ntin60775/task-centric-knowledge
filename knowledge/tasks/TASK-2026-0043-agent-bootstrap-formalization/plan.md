# План: TASK-2026-0043

## Цель

Убрать неоднозначность: агент сам выполняет `task-knowledge install apply` и все сопутствующие шаги при первичном развёртывании. Пользователю/человеку не требуется интерактивный wizard.

## Этапы

1. Обновить `references/adoption.md`: заменить упоминания manual steps на agent-driven flow.
2. Обновить `SKILL.md` и `README.md`: явно указать, что bootstrap — это агентская операция.
3. Проверить `AGENTS.md` и managed-блок: добавить правило "первичный bootstrap выполняет агент".
4. При необходимости доработать `install_skill_runtime` или CLI, чтобы `install apply` был полностью автоматизируем (без интерактивных prompt).
5. Прогнать `bash scripts/check-docs-localization.sh` для новых Markdown-артефактов.

## Проверки

- [ ] Документация не содержит ссылок на интерактивный wizard для bootstrap.
- [ ] `task-knowledge install apply --project-root /abs/project --force` выполняется без stdin-взаимодействия.
- [ ] `bash scripts/check-docs-localization.sh` проходит.
