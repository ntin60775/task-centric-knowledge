# Карточка задачи TASK-2026-0024.4

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0024.4` |
| Parent ID | `TASK-2026-0024` |
| Уровень вложенности | `1` |
| Ключ в путях | `TASK-2026-0024.4` |
| Технический ключ для новых именуемых сущностей | `file-contracts` |
| Краткое имя | `file-local-contracts-for-hotspots` |
| Человекочитаемое описание | `Принять ограниченную локальную разметку файлов для governed hot spots: `MODULE_CONTRACT`, `MODULE_MAP`, `CHANGE_SUMMARY` и точечные якоря блоков без repo-wide обязательной разметки.` |
| Статус | `завершена` |
| Приоритет | `средний` |
| Ответственный | `Codex` |
| Ветка | `main` |
| Требуется SDD | `нет` |
| Статус SDD | `не требуется` |
| Ссылка на SDD | `—` |
| Дата создания | `2026-04-20` |
| Дата обновления | `2026-04-21` |

## Цель

Добавить ограниченный borrowed file-local contract layer
для сложных управляемых файлов,
чтобы агент и ревью имели private/local truth,
но без обязательной разметки всего репозитория.
Этот слой должен давать writer-subagent точные локальные anchors,
а verifier — first divergent anchor для `FailureHandoff`.
Разметка и policy должны быть переносимы между языками,
включая файлы `1С/BSL`.

## Границы

### Входит

- определить разрешённые file-local markers;
- определить, в каких файлах и по каким критериям markup допустим или обязателен;
- определить минимальные правила для якорей блоков;
- определить, как anchors используются в `file show`, execution packet и failure handoff;
- определить syntax-neutral contract для маркеров, пригодный для разных comment styles и для `1С/BSL`;
- связать локальную разметку файла с module passports и будущим `file show`.

### Не входит

- массовая разметка существующего кода;
- обязательную repo-wide semantic markup;
- полный GRACE lint/markup regime.

## Контекст

- источник постановки: заимствование из GRACE private/file-local truth для governed hot spots;
- связанная область: инженерная навигация и review в сложных implementation files;
- ограничения и зависимости: markup должен остаться optional-by-scope и не стать новой обязательной бюрократией;
- дополнительное ожидание: policy не может зависеть от одного вида комментариев или от языка с многострочными doc-блоками по умолчанию;
- исходный наблюдаемый симптом / лог-маркер: без file-local layer module passports дадут только общую публичную истину и не закроют локальный implementation context;
- основной контекст сессии: `capability-подзадача Module Core`

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | будущие parser/query helper для file-local contracts |
| Конфигурация / схема данных / именуемые сущности | набор разрешённых markers и правила hot-spot governance |
| Интерфейсы / формы / страницы | будущая команда `task-knowledge file show` |
| Интеграции / обмены | связь с module passports и borrowed source manifest |
| Документация | task-local правила локальной разметки файлов и границ scope |

## Связанные материалы

- родительская задача: `knowledge/tasks/TASK-2026-0024-grace-borrowed-module-core/`
- GRACE README и explainers по semantic/file-local truth: `/home/prog7/РабочееПространство/work/AI/git-update-only/grace-marketplace/README.md`

## Текущий этап

Подзадача реализована поверх уже внедрённого query-layer `TASK-2026-0024.6`.
Добавлен отдельный parser/runtime слой `module_core_runtime/file_local_contracts.py`,
который читает канонический `knowledge/modules/<MODULE-ID>-<slug>/file-local-policy.md`
и разбирает paired markers / `BLOCK_*`
через syntax-neutral comment prefixes `//`, `#`, `--`, `;`, `*`.

`task-knowledge file show` теперь:

- заполняет JSON-поля `contract_markers` и `blocks`;
- поддерживает text surface `--contracts` и `--blocks`;
- оставляет rollout warning-only без hard lint gate;
- различает отдельные warning-коды для отсутствующей policy,
  файла вне hot-spot scope
  и multi-owner неоднозначности.

Следующий шаг родительской цепочки — `TASK-2026-0024.7`.

## Стратегия проверки

### Покрывается кодом или тестами

- профильный пакет unit/CLI/install-тестов для parser layer,
  слоя read-model,
  единого CLI
  и управляемого installer-контура;
- `git diff --check`
- wrapper локализационной проверки `bash scripts/check-docs-localization.sh`

### Остаётся на ручную проверку

- `не требуется`

## Критерии готовности

- file-local markers и их scope определены;
- правила hot-spot governance однозначны;
- anchors пригодны для packet guidance, `file show` и `FailureHandoff`;
- маркеры и anchors применимы к `1С/BSL` и другим языкам без отдельного special-case режима;
- слой не конфликтует с standalone-границей продукта.

## Итоговый список ручных проверок

- `не требуется`

## Итог

Реализован v1 file-local layer поверх существующих `module show` / `file show`.
Новый managed template `knowledge/modules/_templates/file-local-policy.md`
включён в installer additive assets
и задокументирован в `README.md`, `SKILL.md` и `knowledge/modules/README.md`.

`module.md` теперь требует каноническую относительную ссылку
на `knowledge/modules/<MODULE-ID>-<slug>/file-local-policy.md`.
`file show` при наличии policy-файла читает только явные governed hot spots,
не выводит hard errors на missing markup
и оставляет verification-derived anchors первичным execution signal.

Принятые ограничения v1 зафиксированы в коде и документации:

- hot-spot scope определяется только явной таблицей `## Hot spots`;
- поддерживаются только `MODULE_CONTRACT`, `MODULE_MAP`, `CHANGE_SUMMARY` и named `BLOCK_*`;
- глобальный repo-wide mandatory markup,
  синтаксический граф импортов
  и full GRACE semantic regime остаются вне scope.
