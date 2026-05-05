---
name: task-centric-knowledge
description: "Развертывание и обновление операционной системы задач внутри репозитория с корнем `knowledge/`: локальный источник истины задачи, правила в `AGENTS.md`, git-жизненный цикл, маршрутизация между текущей задачей, подзадачей и новой задачей, publish-flow, доказательные артефакты внутри каталога задачи, безопасное обновление и шаблоны `task.md` / `plan.md` / `sdd.md`. Используй, когда нужно стандартизировать проектную память и git-процесс ведения задач в существующем или новом репозитории."
---

# Развертывание knowledge-системы задач

Этот навык оформляет knowledge-систему как дистрибутив для повторного развёртывания в других проектах.
Смысловая целевая форма skill-а — операционная система задач внутри репозитория, но имя `task-centric-knowledge` остаётся корректным: ядро по-прежнему строится вокруг локального знания задачи и её жизненного цикла.
Установщик по-прежнему разворачивает только две зоны:

- `knowledge/` в целевом проекте;
- маркированным managed-блоком в `AGENTS.md`, если файл существует.

Поверх установки навык задаёт git-жизненный цикл задачи через:

- правила в managed-блоке и шаблонах `knowledge/tasks/`;
- нормативный `Task Core` contract, который исторически принят в task-local contract-артефакте и поставляется в дистрибутиве как `references/core-model.md`;
- правила publish-контура: delivery unit в `task.md`, `du/...`-ветки и PR/MR-центричный жизненный цикл;
- правила автоматической маршрутизации контекста между текущей задачей, подзадачей и новой задачей;
- правила тестового контура: максимум автоматических проверок и единый итоговый список ручных сценариев на уровне общей задачи;
- правила локального хранения доказательных артефактов задачи: скриншоты, логи, образцы, отчёты и материалы миграционной проверки живут внутри каталога задачи или явно ссылаются из него;
- правила безопасного upgrade-перехода между версиями skill-а;
- repo-level upgrade-state и controlled compatibility-backfill legacy-задач;
- install/upgrade governance с `doctor-deps` и `migrate-cleanup-plan/confirm`;
-  unified CLI `task-knowledge workflow` для синхронизации стартовой task-ветки, `task.md`, `registry.md` и publish-блока delivery units.
- read-only operator CLI `task-knowledge task` для `status`, `current-task` и `task show`;
- read-only query layer `task-knowledge module find/show` и `file show` для `Module Core`,
  где `module.md` является shared/public truth,
  `verification.md` — владельцем readiness/evidence,
  `file-local-policy.md` — owner локального hot-spot contract scope,
  а `knowledge/modules/registry.md` остаётся навигационным cache.

## Когда использовать

Использовать, когда нужно:

- развернуть в проекте единый корень `knowledge/`;
- включить task-centric процесс с `knowledge/tasks/` и `knowledge/operations/`;
- зафиксировать стандартный git-жизненный цикл задачи и подзадач;
- встроить PR/MR-центричный publish-flow без отдельной сущности поверх `task.md`;
- заставить систему автоматически определять, когда продолжать текущую задачу, когда создавать подзадачу и когда открывать новую задачу;
- безопасно обновлять старую версию навыка на новую без потери уже созданных task-данных;
- проводить governed compatibility-backfill для `active`, `closed historical` и `reference` без реткона закрытых задач;
- перейти от разрозненных планов и заметок к схеме `одна задача = один plan.md`;
- добавить для сложных задач отдельный контракт реализации в `sdd.md`;
- перевести сложные задачи в specification-driven verification: полный invariant set, `artifacts/verification-matrix.md` и доказательство покрытия тестами до ревью;
- сделать для code-related задач явным контроль зависимостей, модульных границ, критического функционала и symptom-driven проверок;
- сделать проверку задачи предсказуемой: использовать для backend, frontend и остальных затронутых контуров только тот максимум автопроверок, который реально исполним в текущем проекте и допускается его правилами;
- собирать все оставшиеся ручные проверки в единый итоговый список на уровне общей задачи;
- получить read-only операторскую отчётность по задачам через `status`, `current-task` и `task show`;
- находить governed modules и file-local verification anchors через `module find/show` и `file show`;
- читать `file show --contracts --blocks` как реальный text surface для `MODULE_CONTRACT`, `MODULE_MAP`, `CHANGE_SUMMARY` и `BLOCK_*`;
- обновить уже развернутую knowledge-систему из этого же skill.

## Предпочтительный CLI

Предпочтительный операторский вход для этого навыка теперь — единый CLI `task-knowledge`.
Он собирает в одну команду install/governance, read-only query и workflow/publish helper.

Полная глобальная установка навыка из source repo: `make install-global-dry-run`,
затем `make install-global` и `make verify-global-install`.
Этот контур обновляет live-copy в `~/.agents/skills/task-centric-knowledge`,
ставит user-site CLI layer из live-copy и проверяет оба слоя прямыми smoke-checks.

`make install-local` обновляет только user-site CLI layer из текущего каталога.
Зелёный `task-knowledge --help` не считается проверкой live-copy.

Операторские примеры запуска, порядок команд и JSON-контракт вынесены в `README.md`
этого skill-а, чтобы основной `SKILL.md` оставался нормативным, а не справочным.

Единственный операторский entrypoint — `task-knowledge`.
Governed legacy-backfill также должен идти через explicit CLI-режим,
а не через неявное переиспользование ordinary `workflow sync`.

## Базовый порядок

1. Для понимания границ ядра, source-of-truth, managed-файлов, git-жизненного цикла, validated adoption-порядка и правил маршрутизации при необходимости прочитай `references/core-model.md`, `references/deployment.md`, `references/adoption.md`, `references/upgrade-transition.md`, `references/task-workflow.md` и `references/task-routing.md`.
2. Сначала запусти проверку:

```bash
task-knowledge install check --project-root /abs/project
task-knowledge install check --project-root /abs/project --profile 1c
```

Для обновления самого глобально установленного навыка не используй команды выше:
они управляют target project knowledge. Используй global install контур:

Порядок команд: `make install-global-dry-run`, затем `make install-global`, затем `make verify-global-install`.

3. Если результат проверки устраивает, выполни установку:

```bash
task-knowledge install apply --project-root /abs/project
task-knowledge install apply --project-root /abs/project --profile 1c
task-knowledge install apply --project-root /abs/project --existing-system-mode migrate
task-knowledge install apply --project-root /abs/project --force  # полное обновление managed-шаблонов
```

4. Если в проекте уже есть managed-файлы knowledge-системы и их нужно обновить шаблонами этого дистрибутива, используй `--force`.
   При этом `knowledge/tasks/registry.md` и `knowledge/modules/registry.md` считаются project data:
   installer создаёт их при первой установке, но не перезаписывает даже с `--force`.
   `install` всегда выполняет post-install verification перед успешным результатом.
   Сам переход версии разносить в локальном git отдельным commit-ом по правилам из `references/upgrade-transition.md`.
5. Для отдельного read-only аудита уже установленной проектной части используй:

```
task-knowledge install verify-project --project-root /abs/project  # read-only аудит установленного проекта
task-knowledge install verify-project --project-root /abs/project --force  # проверка полного обновления
```

`verify-project --force` требует актуальность force-updatable managed-шаблонов относительно дистрибутива,
но не перезаписывает project data и не выполняет cleanup.
6. Для диагностики install/upgrade-контура используй:

```bash
task-knowledge install doctor-deps --project-root /abs/project
```

`check`, `install`, `verify-project` и `doctor-deps` дополнительно возвращают поля
совместимости `compatibility_epoch`, `upgrade_status`, `execution_rollout`,
а также счётчики `legacy_pending_count` и `reference_manual_count`.

7. Если после миграции появились installer-generated артефакты для безопасной чистки, сначала покажи план:

```bash
task-knowledge install cleanup-plan --project-root /abs/project
```

`migrate-cleanup-plan` раскрывает только auto-delete allowlist v1:

- `knowledge/MIGRATION-SUGGESTION.md`, если текущая классификация уже `clean` или `compatible`;
- `AGENTS.task-centric-knowledge.<profile>.md`, если managed-блок уже materialized в `AGENTS.md`.

Legacy-контуры вроде `.sisyphus`, `doc/tasks`, `docs/tasks`, `docs/roadmap`, `docs/plans` и другие `FOREIGN_SYSTEM_INDICATORS` не удаляются автоматически и уходят только в `manual_review`.
Даже allowlist v1 удаляется автоматически только для обычных файлов; symlink, каталог или любой другой неожиданный тип объекта переводится в `manual_review`.
`project data` (`AGENTS.md`, `knowledge/tasks/registry.md`, `knowledge/modules/registry.md`, каталоги задач и managed knowledge-файлы) остаются в `keep`.
8. Применение cleanup допустимо только через fingerprint из показанного плана:

```bash
task-knowledge install cleanup-confirm --project-root /abs/project --confirm-fingerprint <sha256> --yes
```

`confirm` пересчитывает scope заново и останавливается при любом расхождении `TARGETS`, `TARGET_COUNT`, `COUNT` или confirm-команды.
9. Если `AGENTS.md` отсутствует, установщик не создает его молча, а генерирует отдельный snippet для ручного включения.
10. Если установщик обнаруживает другую систему хранения, он классифицирует её и по умолчанию останавливает установку с явным предложением миграции.
11. Если в `AGENTS.md` найдены неконсистентные managed-маркеры, установщик останавливается с ошибкой и не дописывает новый блок поверх поврежденного состояния.
12. После установки для каждой новой задачи синхронизируй git-контекст через вспомогательный скрипт.
    Если это самый первый task bootstrap после clean install и `install` уже сделал рабочее дерево грязным,
    сначала явно создай `task/...` ветку вручную, а затем вызывай helper в режиме `--register-if-missing`
    по правилам из `references/adoption.md` и `references/task-workflow.md`:

```bash
task-knowledge workflow sync --project-root /abs/project --task-dir knowledge/tasks/TASK-2026-0001-zadacha --create-branch --register-if-missing --summary "Краткое описание задачи"
task-knowledge workflow sync --project-root /abs/project --task-dir knowledge/tasks/TASK-2026-0001-zadacha/subtasks/TASK-2026-0001.1-podzadacha --create-branch --inherit-branch-from-parent --register-if-missing --summary "Краткое описание подзадачи"
```

13. Если repo уже переведён в epoch `module-core-v1`, legacy-задачи обновляй только через explicit backfill:
    через facade-скрипт `task-knowledge workflow backfill --project-root /abs/project --task-dir knowledge/tasks/TASK-2026-0001-zadacha --scope compatibility` или через unified CLI `task-knowledge workflow backfill --project-root /abs/project --task-dir knowledge/tasks/TASK-2026-0001-zadacha --scope compatibility`

Для `closed historical` ordinary sync сохраняет historical safe-sync policy,
а controlled backfill ограничивается migration note и repo upgrade-state.

14. Для read-only operator query используй отдельный CLI:

```bash
task-knowledge --json task status --project-root /abs/project
task-knowledge --json task current --project-root /abs/project
task-knowledge task show --project-root /abs/project current
task-knowledge task show --project-root /abs/project TASK-2026-0001-zadacha
```

`task-knowledge task` не мутирует git или knowledge-контур.
Для `current-task` unified CLI использует policy `branch -> task-scoped dirty fallback -> warning` и не выбирает задачу молча при неоднозначности.

## Профили

- `generic` — общий профиль для обычных программных проектов.
- `1c` — профиль с формулировками под код, metadata, формы и прикладные модули 1С.

## Инварианты

- Источник истины по задаче после установки: `knowledge/tasks/<TASK-ID>-<slug>/task.md`
- Канонический нормативный источник модели `Task Core` должен оформляться отдельным task-local contract-артефактом и затем синхронизироваться в skill-level snapshot и managed-шаблоны
- Корень агрегата `Task Core`: `Task`; канонические task-local сущности: `Subtask`, `Delivery Unit`, `Verification Matrix`, `Task Artifact`, `Decision`, `Worklog Entry`, `Handoff`
- Поля `TASK-ID`, `Краткое имя` и `Человекочитаемое описание` в `task.md` являются каноническим источником сводки задачи
- `registry.md` является навигационным cache и не должен подменять сводку задачи из `task.md`
- `Read Model / Reporting`, `Publish Integration`, `Memory`, `Packaging / Governance` и `Profiles` остаются производными слоями и не могут переопределять `Task Core`
- Для верхнеуровневой задачи по умолчанию используется стартовая ветка `task/<task-id>-<slug>`
- Поле `Ветка` трактуется как текущая активная ветка рабочего контекста; во время поставки это может быть `du/...`
- Для подзадачи по умолчанию используется ветка родителя, пока из локального контекста не доказана необходимость отдельной ветки
- Delivery units хранятся в `## Контур публикации` внутри `task.md` и не попадают в `registry.md`
- Задача может быть закрыта только после того, как все её delivery units переведены в `merged` или `closed`
- Решение между продолжением текущей задачи, созданием подзадачи и открытием новой задачи агент должен принимать автоматически по локальному контексту и зафиксированным правилам
- Если после локального анализа нельзя однозначно выбрать между текущей задачей, подзадачей и новой задачей, агент обязан остановиться и задать пользователю явный вопрос с вариантами
- Стратегия проверки по умолчанию требует использовать максимально полный набор автоматических проверок, который реально исполним в текущем проекте и допустим его правилами, ограничениями и доступной средой
- То, что теоретически можно автоматизировать, но что запрещено или не допускается правилами проекта, не должно попадать в обязательные автопроверки задачи
- Все оставшиеся ручные проверки должны собираться в единый итоговый список на уровне общей задачи, а не размазываться по нескольким артефактам
- На задачу всегда один `plan.md`
- Для сложной задачи `sdd.md` обязателен как отдельный контракт на реализацию
- Для задачи с `sdd.md` по умолчанию обязателен и артефакт `artifacts/verification-matrix.md`
- Все доказательные артефакты задачи хранятся внутри `artifacts/` каталога задачи; внешний объект допустим только при явной ссылке из локального артефакта задачи
- Любой cleanup-governance наследует `plan -> confirm` и не удаляет `project data` молча
- `doctor-deps` различает `required`, `conditional`, `optional`, `not-applicable` зависимости и показывает границу `core/local mode` vs `publish/integration`
- `migrate-cleanup-plan` раскрывает абсолютные пути, `TARGETS`, `TARGET_COUNT`, `COUNT`, `plan_fingerprint` и точную confirm-команду
- `migrate-cleanup-confirm` требует `--confirm-fingerprint` и `--yes`, заново пересчитывает scope и не допускает его расширения
- Подзадачи живут внутри `subtasks/`
- Глубина подзадач ограничена тремя уровнями
- `knowledge/operations/` используется только для действий, которые не считаются задачами продукта
- Обычные локальные git-действия в активной ветке контекста не требуют отдельного подтверждения пользователя, если контекст ясен и рабочее дерево не содержит чужих или несвязанных изменений
- Local finalize допустим как отдельный local-only helper path: при безопасном task-контексте он делает task-scoped commit, fast-forward merge в base-ветку и checkout base-ветки; при блокере возвращает явный stop-report без мутаций
- Локальные publish-helper действия не должны обещать сетевые публикации без валидного remote, поддерживаемого host adapter и доступной auth
- Local finalize не подменяет publish-layer: `push`, PR/MR, host auth и cleanup веток остаются отдельными действиями
- При upgrade старой версии на новую project data и уже созданные task-каталоги должны оставаться нетронутыми, если они не входят в явный scope перехода
- Разговор про `push` допустим только после локальной фиксации перехода и только если реально обнаружен связанный remote

## Доказательный verify-контур

Для сложных задач этот навык требует не только `sdd.md`, но и доказуемый verify-контур.
Это делает агент, а не пользователь или внешний ревьюер.

Обязательный порядок:

1. До существенных изменений выписать полный invariant set задачи, а не только список замечаний или symptom-based fixes.
2. Завести `artifacts/verification-matrix.md` и связать каждый инвариант как минимум с одним сценарием нарушения и одной проверкой.
3. До запроса ревью прогнать команды, тесты и audit-gates, которые доказывают покрытие матрицы.
4. Если часть инвариантов нельзя закрыть автоматикой, явно зафиксировать этот остаток и поднять его в единый ручной checklist общей задачи.

Ревью остаётся дополнительным слоем контроля, но не должно быть первым местом, где система впервые обнаруживает базовые инвариантные ошибки.

## Контроль Code-Related Задач

Этот контур нужен для задач, где меняется код, поведение системы, import/module-связи, пакеты или зависимости.

Правило адаптировано под два режима:

- для простой code-related задачи в `plan.md` допустима короткая форма: явно записать, что новых runtime/package зависимостей нет или перечислить их, указать изменения import/module-связей, критический функционал, основной сценарий и проверки;
- для архитектурно нетривиальной задачи, задачи с новыми зависимостями, изменением направления зависимостей, несколькими модулями или incident/log-driven симптомом это должно быть явно раскрыто в `sdd.md` и привязано к `artifacts/verification-matrix.md`.

Для сложного режима агент обязан:

1. Зафиксировать допустимые и недопустимые связи между модулями, слоями или пакетами.
2. Явно обосновать новые зависимости или зафиксировать проверяемое ожидание, что новых зависимостей быть не должно.
3. Разделить критический функционал и основной сценарий, чтобы тесты доказывали оба уровня поведения.
4. Если задача поднята по логам, инциденту или деградации, сохранить исходный наблюдаемый симптом как проверяемый маркер, сообщение, условие воспроизведения или диагностический признак.
5. До завершения либо прогнать проверки, подтверждающие отсутствие протекания зависимостей и корректность критического и основного функционала, либо явно зафиксировать, почему такие проверки неприменимы.

## Классификация существующей системы хранения

Установщик различает следующие состояния:

- `clean` — признаков другой системы не найдено;
- `compatible` — уже есть совместимая knowledge-система;
- `partial_knowledge` — knowledge-структура есть, но неполная;
- `foreign_system` — найдена другая система хранения без совместимой knowledge-структуры;
- `mixed_system` — одновременно найдены и частичная knowledge-модель, и сторонние контуры хранения.

Если обнаружены `foreign_system` или `mixed_system`, установщик по умолчанию не продолжает установку и предлагает явный режим миграции.

## Управляемые ресурсы

- `assets/knowledge/**` — шаблон корня `knowledge/`
- `assets/agents-managed-block-generic.md` — managed-блок для `AGENTS.md`
- `assets/agents-managed-block-1c.md` — managed-блок для `AGENTS.md` под 1С
- `task-knowledge` — единый CLI entrypoint для install/governance, read-only query и workflow/publish helper
- `scripts/install_skill_runtime/**` — runtime-модули install/upgrade governance
- `task-knowledge workflow` — синхронизация стартовой task-ветки, `task.md`, `registry.md` и publish-блока delivery units
- `task-knowledge task` — read-only operator query для `status/current-task/task show`
- `scripts/module_core_runtime/read_model.py` — projection runtime для partial rollout `Module Core`
- `scripts/module_core_runtime/query_cli.py` — transport-layer и formatter для `module find/show` и `file show`
- `scripts/task_workflow_runtime/read_model.py` — projection runtime поверх `Task Core`
- `scripts/task_workflow_runtime/query_cli.py` — transport-layer и formatter operator CLI
- `references/upgrade-transition.md` — безопасный порядок обновления старой версии навыка на новую и фиксации перехода в git
- `references/core-model.md` — канонический дистрибутивный snapshot модели ядра `Task Core`
- `references/adoption.md` — validated quickstart, field-validated bootstrap первой задачи и patterns по классам сред
- `references/task-routing.md` — правила автоматического выбора между текущей задачей, подзадачей и новой задачей
- `references/task-workflow.md` — справка по git-жизненному циклу задачи
- `references/roadmap.md` — стратегическая дорожная карта дальнейшего развития skill-а и критерии `continue / rethink / borrow`
- `knowledge/tasks/registry.md` — seed-файл реестра, который после первой установки считается project data и не должен перезаписываться `--force`

## Примечания

- Этот skill не пытается угадать проектные naming conventions за пределами общей task-centric модели.
- Установщик сам по себе не делает commit и не трогает удалённый Git-процесс; эти действия относятся к исполнению конкретной задачи после установки.
- После установки при необходимости вручную добавь проект-специфичные конвенции поверх managed-блока в `AGENTS.md`.
