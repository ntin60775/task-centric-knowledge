# SDD по задаче TASK-2026-0037

## Паспорт SDD

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0037` |
| Статус | `готово` |
| Версия | `1` |
| Дата обновления | `2026-04-28` |

## 0. Инварианты и verification matrix

### Полный invariant set

- `INV-01`: глобальная установка live-copy имеет source-controlled команду, а не выполняется ручным rsync.
- `INV-02`: live-copy deploy scope включает все обязательные resources standalone source, включая `assets/knowledge/**`.
- `INV-03`: repo-local и transient артефакты не попадают в live-copy scope.
- `INV-04`: user-site CLI layer и live-copy проверяются раздельно; зелёный CLI smoke не подменяет direct-live smoke.
- `INV-05`: проверка live-copy ловит missing/stale required resources до завершения установки.
- `INV-06`: `task-knowledge install apply` остаётся установкой knowledge-системы в target project и не смешивается с global skill install.
- `INV-07`: destructive cleanup live-copy не выполняется без отдельного delete-gate.

### Связанные артефакты проверки

- `artifacts/verification-matrix.md` — матрица `инвариант -> сценарий нарушения -> проверка/команда -> статус покрытия`.

## 1. Проблема и цель

### Проблема

Процедура глобальной установки навыка была не закреплена в source-controlled команде. Из-за этого live-copy в `~/.agents/skills/task-centric-knowledge` могла быть неполной, например без `assets/knowledge/**`, а пользовательский CLI продолжал работать из source repo и маскировал проблему.

### Цель

После реализации глобальная установка навыка должна быть одной проверяемой процедурой: подготовить manifest/scope, синхронизировать live-copy, обновить user-site CLI layer, выполнить direct-live smoke и user-facing CLI smoke, а тесты должны ловить отсутствие обязательных assets.

## 2. Архитектура и границы

Изменение добавляет отдельный global install контур рядом с существующими поверхностями:

- source repo: канонический standalone-дистрибутив;
- слой `live skill copy`: `~/.agents/skills/task-centric-knowledge`;
- user-site CLI layer: `~/.local/bin/task-knowledge` и `task_knowledge_local.pth`;
- слой `target project knowledge`: `task-knowledge install apply --project-root ...`.

### Допустимые и недопустимые связи

- Допустимо: global install helper импортирует constants из `install_skill_runtime.models`, чтобы не дублировать required source resources.
- Допустимо: Makefile вызывает helper.
- Запрещено: install runtime для target projects импортирует global install helper.
- Запрещено: global install helper выполняет destructive delete без отдельного delete-gate.
- Запрещено: `make install-local` считать полной глобальной установкой live-copy.

### Новые зависимости и их обоснование

- `нет`

### Наблюдаемые сигналы и диагностические маркеры

- `assets/knowledge/**` отсутствует в live-copy.
- `task-knowledge --json doctor` зелёный, но прямой live installer из `~/.agents/skills/...` падает или видит другой source root.
- `rsync` dry-run показывает repo-local/transient artifacts в deploy scope.

## 3. Изменения данных / схемы / metadata

Новых схем данных нет. Добавляется deploy manifest/scope для live-copy и task-local verification artifacts.

## 4. Новые сущности и интерфейсы

- цели Makefile:
  - `install-global`
  - `install-global-dry-run`
  - `verify-global-install`
- скрипт helper:
  - `scripts/install_global_skill.py`
- режимы CLI helper:
  - `--mode dry-run`
  - `--mode apply`
  - `--mode verify`

## 5. Изменения в существующих компонентах

- `Makefile`: добавить targets поверх helper-а.
- `README.md`: разделить `install-local`, global live-copy install, target project install.
- `SKILL.md`: заменить неоднозначную формулировку локальной установки на полный global install flow.
- `references/deployment.md`: добавить операторский runbook global install.
- `tests/`: добавить regression coverage deploy scope.

## 6. Этапы реализации и проверки

### Этап 1: Global install helper

- Добавить `scripts/install_global_skill.py`.
- Добавить Makefile targets.
- Проверка: focused tests для helper scope и smoke behavior.
- Аудит: `IMPLEMENTATION_AUDIT`

### Этап 2: Regression coverage

- Добавить tests, которые строят live bundle в temp dir, проверяют `assets/knowledge/**` и negative missing-assets scenario.
- Проверка: `python3 -m unittest tests.test_global_skill_install -v`
- Аудит: `IMPLEMENTATION_AUDIT`

### Этап 3: Документация

- Обновить README/SKILL/deployment.
- Проверка: `bash scripts/check-docs-localization.sh`
- Аудит: `IMPLEMENTATION_AUDIT`

### Финальный этап: Интеграция

- Выполнить full global install apply.
- Прогнать direct-live и user-facing checks.
- Прогнать полный test suite и diff checks.
- Проверка: полный набор из `plan.md` и `artifacts/verification-matrix.md`.
- Аудит: `INTEGRATION_AUDIT`

## 7. Критерии приёмки

1. Есть штатная source-controlled команда полной глобальной установки навыка.
2. Команда проверяет live-copy напрямую, а не только через PATH CLI.
3. Отсутствие `assets/knowledge/**` в live-copy ловится тестом или verify mode.
4. Документация явно разделяет четыре install-поверхности.
5. Full verify loop проходит.

## 8. Стоп-критерии

1. Helper требует network или root-доступ.
2. Helper удаляет live-copy объекты без отдельного delete-gate.
3. Verify зелёный при отсутствующем `assets/knowledge/**`.
4. `task-knowledge install apply` начинает писать в `~/.agents/skills`.

## Связь с остальными файлами задачи

- `task.md` остаётся источником истины по статусу, границам и итоговому состоянию задачи.
- `plan.md` хранит исполнимый план и ссылки на этапы SDD.
- `artifacts/verification-matrix.md` хранит доказательную связку.
