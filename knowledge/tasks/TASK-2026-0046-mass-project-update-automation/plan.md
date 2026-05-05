# План: TASK-2026-0046

## Цель

Избавить пользователя от ручного запуска `task-knowledge install apply` в каждом проекте после `make install-global`.

## Этапы

1. Спроектировать механизм хранения списка установленных проектов (например, `~/.agents/skills/task-centric-knowledge/projects.json` или scan `~/.agents/skills/task-centric-knowledge/.installed-projects`).
2. Добавить опцию регистрации проекта при `install apply` (или автоматическую регистрацию).
3. Реализовать команду `task-knowledge projects update` (или `task-knowledge install update-all`), которая:
   - читает список проектов;
   - для каждого проекта выполняет `install check` → `install apply --force` → `install verify-project --force`;
   - собирает отчёт с ok/error по каждому проекту;
   - не мутирует проект при ошибке verification.
4. Добавить `--dry-run` режим для предпросмотра.
5. Обновить `Makefile`: добавить `make projects-update` или аналог.
6. Обновить документацию (`README.md`, `SKILL.md`, `references/deployment.md`).
7. Добавить тесты для нового контура.
8. Прогнать полный тестовый контур.

## Проверки

- [ ] `python3 -m unittest discover -s tests` проходит.
- [ ] Команда `task-knowledge projects update --dry-run` выводит план без мутаций.
- [ ] Обновление нескольких тестовых проектов в `tempfile` проходит успешно.
- [ ] При ошибке verification в одном проекте остальные продолжают обновляться.
- [ ] Документация описывает новую команду.
