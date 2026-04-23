# Карточка задачи TASK-2026-0028

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0028` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0028` |
| Технический ключ для новых именуемых сущностей | `cleanup-cli-payload-compat` |
| Краткое имя | `cleanup-cli-payload-compat` |
| Человекочитаемое описание | Починить совместимость текстового CLI-вывода install helper-а с cleanup-payload, у которого нет upgrade-summary полей. |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `агент` |
| Ветка | `task/task-2026-0028-cleanup-cli-payload-compat` |
| Требуется SDD | `да` |
| Статус SDD | `готов` |
| Ссылка на SDD | `sdd.md` |
| Дата создания | `2026-04-21` |
| Дата обновления | `2026-04-21` |

## Цель

Устранить регрессию, при которой `migrate-cleanup-plan` и `migrate-cleanup-confirm` падают в текстовом режиме вывода из-за ожидания upgrade-summary полей, отсутствующих в cleanup-payload.

## Подсказка по статусу

Использовать только одно из значений:

- `черновик`
- `готова к работе`
- `в работе`
- `на проверке`
- `ждёт пользователя`
- `заблокирована`
- `завершена`
- `отменена`

## Git-подсказка

- Поле `Ветка` хранит текущую активную ветку рабочего контекста, а не обязательную долгоживущую task-ветку.
- На старте задачи это обычно `task/...`.
- Во время поставки helper может переводить `Ветка` в delivery-ветку вида `du/<task-id-lower>-uNN-<slug>`.
- При каждом создании или переключении ветки нужно синхронизировать это поле и строку в `registry.md`.

## Границы

### Входит

- `scripts/install_skill_runtime/cli.py` в repo навыка;
- установленная копия skill-а в `~/.agents/skills/task-centric-knowledge`;
- task-local артефакты и проверки дефекта на внешнем целевом проекте.

### Не входит

- изменение структуры cleanup-payload;
- изменение cleanup-scope, fingerprint-логики или auto-delete policy;
- сетевые публикации и merge/push.

## Контекст

- исходный наблюдаемый симптом: `KeyError: 'compatibility_epoch'` при запуске `migrate-cleanup-plan` из установленной копии skill-а;
- repo навыка уже содержит правильную tolerant-логику для optional upgrade-summary полей;
- нужно выровнять установленную копию с repo и зафиксировать это отдельной задачей.

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | Текстовый formatter install helper-а |
| Конфигурация / схема данных / именуемые сущности | `нет` |
| Интерфейсы / формы / страницы | `нет` |
| Интеграции / обмены | CLI surface `migrate-cleanup-plan` / `migrate-cleanup-confirm` |
| Документация | task-артефакты задачи |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0028-cleanup-cli-payload-compat/`
- файл плана: `plan.md`
- файл SDD: `sdd.md`
- файл verification matrix: `artifacts/verification-matrix.md`
- связанный внешний целевой проект для воспроизведения: `/home/prog7/РабочееПространство/projects/PetProjects/task-knowledge-agent-runtime`

## Контур публикации

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | — | `—` | `—` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |

## Текущий этап

Дефект закрыт: repo snapshot подтверждён как уже корректный, установленная копия в `~/.agents/skills/task-centric-knowledge` синхронизирована с ним, cleanup no-op корректно печатается в text mode.

## Стратегия проверки

### Покрывается кодом или тестами

- `python3 scripts/install_skill.py --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-knowledge-agent-runtime --mode migrate-cleanup-plan`
- `python3 /home/prog7/.agents/skills/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-knowledge-agent-runtime --mode migrate-cleanup-plan`
- `bash scripts/check-docs-localization.sh`
- `git diff --check`

### Остаётся на ручную проверку

- при необходимости проверить тот же сценарий на ещё одном совместимом проекте после публикации skill-а

## Критерии готовности

- text formatter install helper-а не падает на cleanup-payload без upgrade-summary полей;
- repo snapshot и установленная копия ведут себя одинаково;
- task-артефакты фиксируют симптом, инварианты и реальные проверки.

## Итоговый список ручных проверок

- После публикации skill-а проверить `migrate-cleanup-plan` на другом совместимом проекте, если понадобится дополнительная field validation.

## Итог

Локализован drift между repo snapshot и установленной копией skill-а: код formatter-а в repo уже был tolerant к optional upgrade-summary полям, а `~/.agents` copy оставалась на старом snapshot и падала с `KeyError`. Установленная копия синхронизирована, оба запуска `migrate-cleanup-plan` на совместимом проекте теперь завершаются успешно и печатают валидный no-op cleanup с `TARGET_COUNT=0` и `COUNT=0`.
