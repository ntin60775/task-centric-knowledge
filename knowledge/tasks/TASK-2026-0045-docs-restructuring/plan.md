# План: TASK-2026-0045

## Цель

Сделать `README.md` лаконичным и понятным для новых пользователей, не перегружая его справочными деталями.

## Этапы

1. Создать `docs/cli-reference.md` и перенести туда все примеры команд, таблицы опций и JSON-контракты из `README.md`.
2. Сократить `README.md` до: что это, quickstart (3 команды), philosophy, ссылки на `SKILL.md`, `docs/cli-reference.md`, `references/`.
3. Обновить cross-references в `SKILL.md`, `references/adoption.md`, `references/deployment.md`.
4. Проверить, что все внутренние Markdown-ссылки работают.
5. Прогнать `bash scripts/check-docs-localization.sh`.

## Проверки

- [ ] `README.md` не длиннее 80 строк.
- [ ] `docs/cli-reference.md` содержит все команды и примеры.
- [ ] Все ссылки внутри репозитория валидны.
- [ ] `bash scripts/check-docs-localization.sh` проходит.
