# План: TASK-2026-0047

## Цель

Связать task-centric-knowledge с semantic-algorithm-design на уровне рекомендации: code-related задачи с нетривиальной алгоритмической логикой должны использовать семантическое моделирование до написания кода.

## Этапы

1. Обновить `assets/knowledge/tasks/_templates/sdd.md` — добавить примечание о семантическом моделировании в раздел инвариантов.
2. Обновить `assets/agents-managed-block-generic.md` — добавить правило в контроль code-related задач.
3. Обновить `assets/agents-managed-block-1c.md` — аналогичное правило для 1С-профиля.
4. Прогнать `bash scripts/check-docs-localization.sh`.
5. Смержить ветку в `main`.

## Проверки

- [ ] `bash scripts/check-docs-localization.sh` проходит.
- [ ] Шаблон `sdd.md` содержит ссылку на `semantic-algorithm-design`.
- [ ] Managed-блоки generic и 1c содержат правило про семантическое моделирование.
