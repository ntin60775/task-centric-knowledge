# Контракт потребительского runtime v1

Этот документ фиксирует минимальный контракт для проектов-потребителей, которые используют `task-centric-knowledge` как updateable runtime dependency, но сами владеют своим product runtime storage.

## Целевая модель

`task-centric-knowledge` остаётся standalone task OS и предоставляет стабильный CLI/JSON contract. Consumer repo сам выбирает способ обновления встроенного subset-а и сам хранит product runtime state в своём явном subroot.

Контракт не добавляет upstream-команду, которая меняет consumer repo. Если потребителю нужен embedded subset, обновление остаётся на стороне consumer-owned script-а или package workflow.

## Граница корней

- `project_root` — корень consumer repo, где живут `knowledge/`, task data и product runtime subroot.
- `runtime_root` — каталог, из которого реально исполняется runtime subset или установленная команда.
- `source_root` — standalone-дистрибутив `task-centric-knowledge` с `SKILL.md`, `assets/`, `references/` и `scripts/`.

`project_root` не является fallback-ом для `source_root`. Если команда требует install assets, а доступен только embedded runtime subset, она должна вернуть один blocker `source_root_unavailable`, а не искать `SKILL.md` и `assets/...` внутри consumer repo.
Собственные каталоги consumer-а вроде `assets/` и `references/` не превращают `project_root` в standalone `source_root`.

## Стабильная CLI/JSON-поверхность

Публичным API для consumers считается CLI/JSON, а не Python imports:

- `task-knowledge --json task status --project-root /abs/project`
- `task-knowledge --json task current --project-root /abs/project`
- `task-knowledge --json task show --project-root /abs/project current|TASK-ID`
- `task-knowledge --json workflow sync --project-root /abs/project --task-dir ...`
- `task-knowledge --json doctor --project-root /abs/project`
- `task-knowledge --json install check --project-root /abs/project`
- `task-knowledge --json install doctor-deps --project-root /abs/project`

Mutating workflow-команды остаются отдельным lifecycle surface и не являются embedded update protocol.

## Встраиваемый manifest

Consumer-owned manifest может использовать следующий minimum shape:

```json
{
  "integration_contract": "consumer-runtime-v1",
  "pinned_commit": "<upstream commit>",
  "included_paths": ["scripts/task_query.py"],
  "consumer_runtime_root": "knowledge/runtime/<consumer-id>",
  "consumer_entrypoint": "task-knowledge task status --project-root /abs/project"
}
```

Допустимые расширения: `checksums`, `compatible_cli_range`, `schema_version`, `updated_at`.

Обязательные правила:

- `included_paths` описывает только embedded runtime files, а не project data.
- `consumer_runtime_root` обязан быть явным subroot-ом, а не всем `knowledge/`.
- `knowledge/tasks/*`, `knowledge/tasks/registry.md` и task artifacts остаются project data.
- Root `.sisyphus` считается foreign storage contour; вложенные fixture/test paths не должны сами по себе становиться root-level migration blocker.

## Версионирование

Версия package/CLI и версия consumer contract связаны, но не подменяют друг друга:

- package/CLI version показывает версию поставки `task-knowledge`;
- `consumer-runtime-v1` показывает совместимость embedded consumer contract;
- breaking change в CLI/JSON или manifest shape требует нового consumer contract.

## Владение обновлением

Потребитель сам выполняет pull/update embedded subset-а из canonical upstream. `task-centric-knowledge` в этом контракте только гарантирует стабильность описанного surface и диагностику, которая не смешивает `project_root`, `runtime_root` и `source_root`.
