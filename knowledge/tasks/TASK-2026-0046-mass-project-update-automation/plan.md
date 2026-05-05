# План задачи TASK-2026-0046

## Правило

Для задачи существует только один файл плана: `plan.md`.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0046` |
| Parent ID | `—` |
| Версия плана | `1` |
| Связь с SDD | `sdd.md` |
| Дата обновления | `2026-05-06` |

## Цель

Автоматизировать массовое обновление knowledge-системы в установленных проектах через единую команду.

## Границы

### Входит

- Новая подкоманда `task-knowledge install mass-update`.
- Обнаружение проектов с knowledge-системой.
- Пакетное обновление: check → apply → verify.
- Dry-run режим.
- Сводный отчёт.
- Обработка ошибок с продолжением.

### Не входит

- Авто-commit/push.
- Обнаружение не-knowledge проектов.
- Параллельное выполнение.
- Интерактивный выбор.

## Планируемые изменения

### Код

- `src/task_knowledge/install_runtime/mass_update.py` (новый) — логика массового обновления.
- `src/task_knowledge/cli.py` — добавить подкоманду `mass-update`.
- `src/task_knowledge/install_runtime/__init__.py` — экспорт `mass_update`.

### Документация

- `README.md` — добавить пример `mass-update`.
- `references/deployment.md` — обновить секцию production rollout.

## Зависимости и границы

### Новые runtime/package зависимости

`нет`

### Изменения import/module-связей и зависимостей между модулями

- Новый модуль `install_runtime.mass_update` импортирует из `install_runtime` (check, install, verify_project) и `git_ops` (для проверки git-репозиториев).

### Границы, которые должны остаться изолированными

- Install runtime функции (`check`, `install`, `verify_project`) не меняются.
- Mass-update только вызывает их для каждого проекта.

### Критический функционал

- Обнаружение проектов: поиск `AGENTS.md` с managed-блоком knowledge-системы.
- Пакетное обновление: check → apply --force → verify-project --force.
- Dry-run: только check без apply.
- Отчёт: статус каждого проекта (ok/error/skipped).

### Основной сценарий

1. `task-knowledge install mass-update --source-root ~/.agents/skills/task-centric-knowledge --profile generic`.
2. Обнаружение проектов (поиск `AGENTS.md` с `BEGIN_TASK_KNOWLEDGE_SYSTEM#KB01`).
3. Для каждого проекта:
   a. `install check` — проверка.
   b. Если check ok → `install apply --force` — обновление.
   c. `install verify-project --force` — проверка результата.
   d. Запись результата в отчёт.
4. Вывод сводного отчёта.

### Исходный наблюдаемый симптом

`не требуется`

## Риски и зависимости

- **Ложные срабатывания**: `AGENTS.md` с managed-блоком может существовать без полной knowledge-системы.
- **Права доступа**: mass-update может не иметь прав на запись в некоторые проекты.
- **Грязное дерево**: если в проекте есть незакоммиченные изменения, apply не должен их коммитить.
- **Большое количество проектов**: последовательное обновление может быть долгим.

## Связь с SDD

- SDD: `sdd.md` — инварианты, архитектура обнаружения, flow обновления.
- Verification matrix: `artifacts/verification-matrix.md`.
- Этапы SDD:
  1. Проектирование механизма обнаружения.
  2. Реализация `mass_update.py`.
  3. Интеграция в CLI.
  4. Тестирование.
  5. Обновление документации.

## Проверки

### Что можно проверить кодом или тестами

- `python3 -m unittest discover -s tests -v` — тесты mass-update.
- `make check` — source gate.
- `task-knowledge install mass-update --dry-run` на тестовых проектах.
- Доказательство покрытия `artifacts/verification-matrix.md`.

### Что остаётся на ручную проверку

- Массовое обновление на production-проектах.

## Шаги

- [ ] Шаг 1: Спроектировать механизм обнаружения проектов (см. SDD).
- [ ] Шаг 2: Реализовать `src/task_knowledge/install_runtime/mass_update.py`.
- [ ] Шаг 3: Добавить подкоманду `mass-update` в CLI.
- [ ] Шаг 4: Реализовать dry-run и отчётность.
- [ ] Шаг 5: Написать тесты.
- [ ] Шаг 6: Обновить `README.md` и `references/deployment.md`.
- [ ] Шаг 7: Прогнать тесты и проверки.
- [ ] Шаг 8: Доказать покрытие verification matrix.

## Критерии завершения

- `task-knowledge install mass-update` обновляет все обнаруженные проекты.
- Dry-run работает.
- Сводный отчёт информативен.
- Тесты проходят.
- `make check` зелёный.
