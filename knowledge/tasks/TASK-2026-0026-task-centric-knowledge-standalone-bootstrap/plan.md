# План задачи TASK-2026-0026

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0026` |
| Parent ID | `—` |
| Версия плана | `1` |
| Связь с SDD | `не требуется` |
| Дата обновления | `2026-04-21` |

## Цель

Довести standalone bootstrap до опубликованного и проверенного состояния.

## Шаги

- [ ] Проверить структуру repo-root
- [ ] Прогнать тесты и CLI smoke
- [ ] Настроить SSH remote и запушить `main`

## Проверки

- `git diff --check`
- `python3 -m unittest discover -s tests`
- `make install-local`
- `task-knowledge --help`
- `task-knowledge task status --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge`

## Критерии завершения

- repo опубликован;
- проверки выполнены;
- task-история доступна через CLI.
