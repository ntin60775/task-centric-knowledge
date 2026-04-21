# Заимствованный слой GRACE

Этот каталог фиксирует local-first borrowed-layer из GRACE для `Module Core`.
Он не превращает `task-centric-knowledge` в GRACE runtime и не требует XML-платформу как обязательную зависимость.

## Манифест источника

Канонический manifest:

```text
borrowings/grace/source.json
```

В manifest закреплены:

- `origin_url`: upstream-репозиторий GRACE;
- `pinned_revision`: проверяемый commit, из которого берутся borrowings;
- `upstream_version`: версия upstream-пакета;
- `local_checkout_override`: локальный checkout через CLI `--checkout` или env `TASK_KNOWLEDGE_GRACE_CHECKOUT`;
- `surfaces`: язык-независимое соответствие `upstream source -> local target`.

Абсолютный локальный путь checkout не хранится в manifest, потому что это настройка оператора, а не distributable contract.

## Поток обновления

Операторский контур:

```text
task-knowledge --json borrowings status --project-root /abs/project --source grace --checkout /abs/grace-checkout
task-knowledge --json borrowings refresh-plan --project-root /abs/project --source grace --checkout /abs/grace-checkout
task-knowledge --json borrowings refresh-apply --project-root /abs/project --source grace --checkout /abs/grace-checkout --plan-fingerprint <sha256> --yes
```

`status` показывает состояние manifest и checkout,
а также заранее сигнализирует,
если mapped upstream paths уже dirty
и `refresh-plan` будет заблокирован.
`refresh-plan` строит preview действий для pinned revision.
`refresh-apply` заново строит preview, сверяет fingerprint и применяет только тот scope, который был подтверждён.

В v1 разрешены только действия `create`, `update` и `noop`.
Удаление и переименование borrowed assets запрещены.
Manifest также требует:

- уникальные `surface_id`;
- уникальные `local_target` по всему manifest;
- точное совпадение summary-полей `upstream_paths` и `local_targets` с фактическими `mappings`.

## Репозиторный словарь пакетов

Borrowed vocabulary адаптирует идеи GRACE к task-centric модели:

- `ExecutionPacket` — контроллер выдаёт writer-subagent точный write-scope, contract excerpt, dependency summaries, verification excerpt, allowed checks и stop conditions.
- `ResultPacket` — writer возвращает changed files, executed checks, residual risks, assumptions и needs-controller-decision.
- `FailureHandoff` — verifier передаёт contract ref, scenario, expected evidence, observed evidence, first divergent anchor и suggested next action.
- `ExecutionReadiness` — будущий verification catalog сообщает `ready`, `blocked` или `partial` перед writer-pass.

Writer-subagent не владеет `task.md`, `plan.md`, `sdd.md`, `registry.md` и shared governance docs.
Если write-scope нужно расширить, writer возвращает blocker контроллеру.

## Язык-независимая граница

Manifest описывает surface через пути, concepts и target assets.
Он не требует Python, TypeScript, AST, package manager или import graph.
Такой mapping пригоден и для file-centric репозиториев, включая `1С/BSL`.
