# Карточка задачи TASK-2026-0026

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0026` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0026` |
| Технический ключ для новых именуемых сущностей | `task-centric-knowledge` |
| Краткое имя | `task-centric-knowledge-standalone-bootstrap` |
| Человекочитаемое описание | Зафиксировать bootstrap нового standalone-репозитория `task-centric-knowledge` после выноса из `ai-agents-rules`. |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `main` |
| Требуется SDD | `нет` |
| Статус SDD | `не требуется` |
| Ссылка на SDD | `—` |
| Дата создания | `2026-04-21` |
| Дата обновления | `2026-04-21` |

## Цель

Принять новый репозиторий как канонический дом `task-centric-knowledge`,
сохранить перенесённую продуктовую историю и подтвердить базовую работоспособность standalone CLI.

## Границы

### Входит

- bootstrap standalone-репозитория;
- проверка CLI/test smoke;
- публикация `main` на GitHub.

### Не входит

- изменение runtime-проекта `task-knowledge-agent-runtime`;
- перенос старой задачи `TASK-2026-0026` из `ai-agents-rules`;
- отдельный release tag.

## Контекст

- источник постановки: split-out задача `TASK-2026-0027` в `ai-agents-rules`;
- связанная бизнес-область: standalone productization `task-centric-knowledge`;
- ограничения и зависимости: SSH remote и внешний publish;
- исходный наблюдаемый симптом / лог-маркер: `не требуется`;
- основной контекст сессии: `новая задача`.

## Текущий этап

Bootstrap репозитория завершён.
Standalone-репозиторий опубликован и запушен,
CLI smoke и тесты выполнены,
task-история доступна через `task-knowledge`.

## Стратегия проверки

### Покрывается кодом или тестами

- `git diff --check`
- `python3 -m unittest discover -s tests`
- `make install-local`
- `task-knowledge --help`
- `task-knowledge task status --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge`

### Остаётся на ручную проверку

- Проверить GitHub-страницу после публикации.

## Критерии готовности

- репозиторий опубликован;
- тесты и CLI smoke выполнены;
- рабочее дерево чистое после push.

## Итоговый список ручных проверок

- Проверить GitHub-страницу после публикации.

## Итог

Репозиторий опубликован:
`https://github.com/ntin60775/task-centric-knowledge`.
SSH-адрес:
`git@github.com:ntin60775/task-centric-knowledge.git`.
Первый commit:
`4e42d8b`.
Временная `gh`-авторизация после публикации очищена.
