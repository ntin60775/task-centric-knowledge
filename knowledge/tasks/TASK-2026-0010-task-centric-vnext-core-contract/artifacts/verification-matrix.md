# Матрица проверки по задаче TASK-2026-0010

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0010` |
| Связанный SDD | `../sdd.md` |
| Версия | `2` |
| Дата обновления | `2026-04-13` |

## 1. Канонические инварианты

| Invariant ID | Описание | Источник истины | Где может сломаться |
|--------------|----------|-----------------|---------------------|
| `INV-0010-01` | У `Task Core` есть один канонический нормативный документ `artifacts/vnext-core-contract.md`. | `artifacts/vnext-core-contract.md`, `task.md`, `sdd.md` | Нормативный слой останется размазан между roadmap, SDD и snapshot-документами. |
| `INV-0010-02` | Полный агрегат перечисляет `Task`, `Subtask`, `Delivery Unit`, `Verification Matrix`, `Task Artifact`, `Decision`, `Worklog Entry`, `Handoff`. | `artifacts/vnext-core-contract.md` | Downstream-задачи закрепят неполную модель и потеряют task-local сущности. |
| `INV-0010-03` | `task.md` остаётся source-of-truth по summary, status, branch и delivery units, а `registry.md` остаётся cache. | `artifacts/vnext-core-contract.md`, `SKILL.md`, `README.md` | Read-model или реестр начнут переопределять смысл задачи. |
| `INV-0010-04` | Summary задачи канонически строится из `TASK-ID`, `Краткого имени` и `Человекочитаемого описания`. | `artifacts/vnext-core-contract.md`, `SKILL.md`, `README.md` | CLI/reporting слой будет собирать summary из fallback-полей и создавать drift. |
| `INV-0010-05` | Производные контексты перечислены явно и не обходят `Task Core`. | `artifacts/vnext-core-contract.md`, `references/roadmap.md` | Read-model, publish-layer, memory или governance получат неявное право менять ядро. |
| `INV-0010-06` | Статусная модель задач и delivery units закреплена как набор допустимых состояний и переходов. | `artifacts/vnext-core-contract.md` | Следующие tracks начнут вводить несовместимые state-machine semantics. |
| `INV-0010-07` | Evidence хранится внутри task-local `artifacts/` или явно ссылается из него. | `artifacts/vnext-core-contract.md`, `SKILL.md`, `README.md` | Доказательные материалы останутся вне задачи без task-local привязки. |
| `INV-0010-08` | Cleanup-governance наследует `plan -> confirm` и не удаляет `project data` молча. | `artifacts/vnext-core-contract.md`, `SKILL.md`, `references/roadmap.md` | Governance-слой сможет выполнять cleanup без раскрытого scope и подтверждения. |
| `INV-0010-09` | Skill-level snapshot и managed templates синхронизированы с task-local contract. | `SKILL.md`, `references/roadmap.md`, assets `knowledge/tasks/**` | После refresh installer развернёт шаблоны, противоречащие core contract. |

## 2. Матрица покрытия

| Invariant ID | Сценарий нарушения или переход | Автопроверка / команда | Статус покрытия | Примечание |
|--------------|--------------------------------|------------------------|-----------------|------------|
| `INV-0010-01` | В репозитории нет одного явного primary source для `Task Core`. | `rg -n "канонический нормативный источник|artifacts/vnext-core-contract.md|первичный нормативный" knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/task.md knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/sdd.md knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md skills-global/task-centric-knowledge/references/roadmap.md` | `covered` | Core contract создан и все производные документы ссылаются именно на него. |
| `INV-0010-02` | В contract отсутствуют `Decision`, `Worklog Entry` или `Handoff`. | `rg -n "Task Artifact|Decision|Worklog Entry|Handoff|Verification Matrix|Delivery Unit" knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md` | `covered` | Полный агрегат перечислен в contract явным списком и таблицами. |
| `INV-0010-03` | `registry.md` или другой слой объявлен source-of-truth вместо `task.md`. | `rg -n "task.md|registry.md|источник истины|cache|delivery units" knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md skills-global/task-centric-knowledge/SKILL.md skills-global/task-centric-knowledge/assets/knowledge/tasks/README.md` | `covered` | Contract, skill и managed `README.md` согласованы по ownership. |
| `INV-0010-04` | Summary собирается не из канонической тройки. | `rg -n "TASK-ID|Краткое имя|Человекочитаемое описание" knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md skills-global/task-centric-knowledge/SKILL.md skills-global/task-centric-knowledge/assets/knowledge/tasks/README.md` | `covered` | Каноническая summary-тройка присутствует в task-local и skill-level документах. |
| `INV-0010-05` | Производные контексты не описаны или могут менять ядро. | `rg -n "Task Core|Read Model / Reporting|Publish Integration|Memory|Packaging / Governance|Profiles|не меняет|не конкурирует|не удаляет" knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md skills-global/task-centric-knowledge/references/roadmap.md` | `covered` | DDD-карта и ограничения слоёв синхронизированы. |
| `INV-0010-06` | В репозитории нет явной state-machine для задач и delivery units. | `rg -n "черновик|готова к работе|в работе|на проверке|ждёт пользователя|заблокирована|завершена|отменена|planned|local|draft|review|merged|closed" knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md` | `covered` | Contract фиксирует оба набора статусов и допустимые переходы. |
| `INV-0010-07` | Evidence разрешено хранить вне задачи без ссылки из `artifacts/`. | `rg -n "artifacts/|внешний объект|ссылка|доказательные артефакты" knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md skills-global/task-centric-knowledge/SKILL.md skills-global/task-centric-knowledge/assets/knowledge/tasks/README.md` | `covered` | Правило локального хранения evidence повторено в contract, skill и managed `README.md`. |
| `INV-0010-08` | Cleanup допускает silent deletion или обход `plan -> confirm`. | `rg -n "plan -> confirm|cleanup|project data" knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md skills-global/task-centric-knowledge/SKILL.md skills-global/task-centric-knowledge/references/roadmap.md` | `covered` | Contract и skill-level snapshot повторяют базовый governance-инвариант. |
| `INV-0010-09` | Assets и installer разворачивают шаблоны, не совпадающие с contract. | `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'` | `covered` | Unit-тесты installer/templates прошли после обновления asset-файлов и text-regression проверок. |

## 3. Остаточный риск и ручной остаток

- `нет`

## 4. Правило завершения

- Задача не считается завершённой, пока все обязательные инварианты не переведены в `covered`.
- Review не заменяет эту матрицу и не считается первым местом обнаружения core-инвариантных ошибок.
