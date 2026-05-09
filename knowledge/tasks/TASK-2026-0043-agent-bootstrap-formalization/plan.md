# План задачи TASK-2026-0043

## Правило

Для задачи существует только один файл плана: `plan.md`.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0043` |
| Parent ID | `—` |
| Версия плана | `1` |
| Связь с SDD | `sdd.md` |
| Дата обновления | `2026-05-06` |

## Цель

Добавить `task-knowledge bootstrap` — единую команду для развёртывания knowledge-системы в новом проекте без ручных шагов.

## Границы

### Входит

- Новая подкоманда `bootstrap` в unified CLI.
- Автоматизация последовательности: install check → install apply → doctor-deps → создание первой задачи → sync.
- Обработка dirty tree (авто-commit knowledge-файлов).
- Поддержка `--dry-run`.
- Обновление `references/adoption.md`.

### Не входит

- Интерактивные wizard.
- Миграция существующих систем.
- Пользовательское содержимое задач.

## Планируемые изменения

### Код

- `src/task_knowledge/cli.py` — добавить `_add_bootstrap_command()`, `_bootstrap()`.
- Новый модуль `src/task_knowledge/bootstrap.py` — логика bootstrap.
- Доработка `sync_task` для поддержки авто-commit при dirty tree с knowledge-файлами.

### Документация

- `references/adoption.md` — обновить §4 на `task-knowledge bootstrap`.
- `README.md` — добавить пример bootstrap.

## Зависимости и границы

### Новые runtime/package зависимости

`нет`

### Изменения import/module-связей и зависимостей между модулями

- Новый модуль `task_knowledge.bootstrap` импортирует из `install_runtime` и `workflow_runtime`.

### Границы, которые должны остаться изолированными

- Install runtime и workflow runtime не меняют логику, только дополняются при необходимости.

### Критический функционал

- `task-knowledge bootstrap --project-root /abs/project` выполняет полный bootstrap.
- `--dry-run` показывает план без мутации.
- `--profile 1c` работает корректно.

### Основной сценарий

1. `task-knowledge bootstrap --project-root /abs/project --profile generic`.
2. Выполняется `install check` — валидация.
3. Выполняется `install apply --force` — установка knowledge-файлов.
4. Выполняется `doctor-deps` — проверка зависимостей.
5. Если дерево грязное (knowledge-файлы) — авто-commit.
6. Создаётся task-ветка `task/task-2026-0001-...`.
7. Создаётся каталог задачи из шаблонов.
8. `workflow sync --create-branch --register-if-missing`.

### Исходный наблюдаемый симптом

`не требуется`

## Риски и зависимости

- **Dirty tree**: если в проекте уже есть незакоммиченные изменения, bootstrap не должен их коммитить вместе с knowledge-файлами.
- **Существующая knowledge-система**: если `install check` обнаруживает существующую систему, bootstrap должен остановиться или перейти в режим обновления.
- **Отсутствие git**: bootstrap должен явно сообщить, что проект не git-репозиторий.

## Связь с SDD

- SDD: `sdd.md` — инварианты, архитектура bootstrap, этапы.
- Verification matrix: `artifacts/verification-matrix.md`.
- Этапы SDD:
  1. Проектирование bootstrap flow.
  2. Реализация `bootstrap.py`.
  3. Интеграция в unified CLI.
  4. Доработка `sync_task` для авто-commit.
  5. Обновление `references/adoption.md`.
  6. Тестирование и верификация.

## Проверки

### Что можно проверить кодом или тестами

- `python3 -m unittest discover -s tests -v` — тесты bootstrap.
- `make check` — source gate.
- `task-knowledge bootstrap --dry-run` на тестовом проекте.
- `task-knowledge bootstrap` с последующей проверкой `task status`.
- Доказательство покрытия `artifacts/verification-matrix.md`.

### Что остаётся на ручную проверку

- Поведение на не-clean проекте.
- Поведение на проекте без git.

## Шаги

- [ ] Шаг 1: Спроектировать bootstrap flow (см. SDD).
- [ ] Шаг 2: Реализовать `src/task_knowledge/bootstrap.py`.
- [ ] Шаг 3: Добавить подкоманду `bootstrap` в CLI.
- [ ] Шаг 4: Доработать `sync_task` для авто-commit (при необходимости).
- [ ] Шаг 5: Написать тесты для bootstrap.
- [ ] Шаг 6: Обновить `references/adoption.md`.
- [ ] Шаг 7: Обновить `README.md`.
- [ ] Шаг 8: Прогнать тесты и проверки.
- [ ] Шаг 9: Доказать покрытие verification matrix.

## Критерии завершения

- `task-knowledge bootstrap` выполняет полный bootstrap.
- Dry-run работает.
- `references/adoption.md` обновлён.
- Тесты проходят.
- `make check` зелёный.
