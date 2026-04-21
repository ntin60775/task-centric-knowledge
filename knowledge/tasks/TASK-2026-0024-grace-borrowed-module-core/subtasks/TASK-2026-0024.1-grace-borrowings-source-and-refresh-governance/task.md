# Карточка задачи TASK-2026-0024.1

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0024.1` |
| Parent ID | `TASK-2026-0024` |
| Уровень вложенности | `1` |
| Ключ в путях | `TASK-2026-0024.1` |
| Технический ключ для новых именуемых сущностей | `borrowings-refresh` |
| Краткое имя | `grace-borrowings-source-and-refresh-governance` |
| Человекочитаемое описание | `Зафиксировать local-first source manifest и безопасный refresh-governance для borrowed-layer из GRACE без жёсткой привязки к одному checkout path.` |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `main` |
| Требуется SDD | `нет` |
| Статус SDD | `не требуется` |
| Ссылка на SDD | `—` |
| Дата создания | `2026-04-20` |
| Дата обновления | `2026-04-20` |

## Цель

Сделать borrowed-layer из GRACE обновляемым и воспроизводимым:
вместо неустойчивого абсолютного пути
ввести machine-readable source manifest,
локальный override checkout path
и явный refresh flow `status -> refresh-plan -> refresh-apply`,
не завязанный на один язык или один тип исходных артефактов.
В этом же foundation-слое нужно зафиксировать borrowed vocabulary для controlled execution:
`ExecutionPacket`, `ResultPacket`, `FailureHandoff` и `ExecutionReadiness`
как repo-native заимствования из GRACE без переноса full XML-платформы.

## Границы

### Входит

- выбрать и закрепить canonical path для source manifest borrowed-layer;
- описать поля `origin_url`, `pinned_revision`, `local_checkout_override`, состав borrowed surface и mapping upstream -> local target;
- определить read-only статус borrowed-layer и план/применение refresh;
- определить защиту от расширения scope между `refresh-plan` и `refresh-apply`;
- определить mapping `GRACE operational packets -> repo-native execution packet vocabulary`;
- определить, что `refresh-apply` и обновление borrowed assets остаются controller-only действием;
- определить, как borrowed manifest описывает language-agnostic surface и не предполагает Python/TypeScript-only структуру источника;
- определить, как local checkout обнаруживается и как fallback ведёт себя без сети.

### Не входит

- реализация module passports, dependency map и file-local contracts;
- массовый импорт файлов из GRACE в текущем ходе;
- network fetch как обязательный сценарий первой поставки.

## Контекст

- источник постановки: решение пользователя ожидать обновляемый borrowed-layer, а не одноразовое ручное копирование идей;
- связанная область: governance borrowings между `task-centric-knowledge` и GRACE;
- ограничения и зависимости: старый путь `/home/prog7/MyWorkspace/30-Knowledge/AI/grace-marketplace/` уже не существует; runtime не должен фиксировать новый абсолютный checkout path в distributable contract и обязан получать локальный checkout через `--checkout` или `TASK_KNOWLEDGE_GRACE_CHECKOUT`;
- дополнительное ожидание: source manifest должен быть пригоден для borrowings, применимых к разным языкам, включая `1С/BSL`;
- исходный наблюдаемый симптом / лог-маркер: артефакты предыдущих задач ссылаются на устаревший checkout path и не дают устойчивого refresh-механизма;
- основной контекст сессии: `первая рабочая подзадача TASK-2026-0024`

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | будущий CLI/runtime слой `task-knowledge borrowings status|refresh-plan|refresh-apply` и helper-слой borrowed packet vocabulary |
| Конфигурация / схема данных / именуемые сущности | source manifest borrowed-layer, локальный override-контракт, отпечаток refresh-плана, repo-native packet vocabulary |
| Интерфейсы / формы / страницы | read-only статус и preview/apply интерфейс borrowed refresh |
| Интеграции / обмены | локальная интеграция с checkout `grace-marketplace` как внешним upstream source |
| Документация | task-local описание refresh-governance и будущий borrowed README |

## Связанные материалы

- родительская задача: `knowledge/tasks/TASK-2026-0024-grace-borrowed-module-core/`
- граница продукта: `knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/artifacts/v1-product-thesis.md`
- операторский локальный GRACE checkout: задаётся через `--checkout` или `TASK_KNOWLEDGE_GRACE_CHECKOUT`
- upstream README: `README.md` внутри указанного оператором checkout

## Текущий этап

Подзадача завершена.
Манифест источника,
отпечаток refresh-плана,
поверхность CLI
и repo-native packet vocabulary реализованы и усилены после цикличного ревью.
Полный test/localization контур пройден,
а operator contract больше не опирается на несуществующий локальный checkout path.

## Стратегия проверки

### Покрывается кодом или тестами

- unit/regression для parser и fingerprint borrowed manifest;
- CLI-проверки `task-knowledge borrowings status|refresh-plan|refresh-apply --json`;
- `git diff --check`

### Остаётся на ручную проверку

- `не требуется`

## Критерии готовности

- source manifest определён и не зависит от одного абсолютного пути;
- refresh flow описан как `plan -> apply` с защитой от drift scope;
- borrowed packet vocabulary описывает `ExecutionPacket`, `ResultPacket`, `FailureHandoff`, `ExecutionReadiness` без переноса GRACE XML как обязательного runtime;
- local-first сценарий работает без обязательной сети;
- manifest не кодирует язык-специфичную модель исходников и допускает borrowings для `1С/BSL`;
- borrowed-layer можно обновлять повторно и предсказуемо.

## Итоговый список ручных проверок

- `не требуется`

## Итог

Реализован local-first borrowed-layer для GRACE:
добавлены `source.json`,
описание governance в `README.md`,
runtime helper для `status -> refresh-plan -> refresh-apply`
и namespace `task-knowledge borrowings`.
Refresh-план получает fingerprint по manifest,
`pinned_revision`,
`checkout_revision`,
source hashes и target-before hashes.
`refresh-apply` заново строит preview,
требует `--yes`,
сверяет fingerprint
и применяет только `create/update/noop` scope внутри skill root.

Borrowed packet vocabulary зафиксирован без переноса GRACE XML runtime:
`ExecutionPacket`,
`ResultPacket`,
`FailureHandoff`
и `ExecutionReadiness`
остаются repo-native contract для controlled single-writer execution.

Фактические проверки пройдены:
`python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'`,
`git diff --check`,
`python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules task show TASK-2026-0024.1 --format json`,
`python3 skills-global/task-centric-knowledge/scripts/task_knowledge_cli.py --json borrowings refresh-plan --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules --source grace --checkout /abs/grace-checkout`
и `bash scripts/check-docs-localization.sh ...`.
