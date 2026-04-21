# `task-centric-knowledge v1`: продуктовая формула и граница с GRACE

## 1. Зачем вообще нужен этот продукт

`task-centric-knowledge` оправдан как отдельный продукт только в одной роли:

это не universal AI engineering framework,
а лёгкая task-centric operating system для репозитория,
которая делает три вещи одновременно:

- хранит канонический контекст задачи прямо внутри проекта;
- заставляет агента и человека работать через одни и те же task-local артефакты;
- связывает knowledge-контур задачи с минимально достаточным git/publish lifecycle.

Если продукт пытается стать "всем хорошим сразу" —
roadmap, spec-kit, verification framework, semantic markup platform, multiagent runtime и knowledge graph —
он проигрывает более зрелому GRACE и теряет право на отдельное существование.

## 2. Что такое первая полнофункциональная релизная версия

`task-centric-knowledge v1` считается выпущенным не тогда, когда закрыты все идеи roadmap,
а тогда, когда пользователь может установить систему в реальный репозиторий и получить рабочий цикл без догадок.

Release-grade сценарий `v1`:

1. выполнить `install/check/doctor` и получить предсказуемое состояние knowledge-системы;
2. открыть новую задачу и синхронизировать её с веткой и `registry.md`;
3. вести задачу, подзадачу и доказательные артефакты в одном task-local каталоге;
4. получать operator-ответы через `status/current-task/task show`;
5. использовать локальный git/publish lifecycle как штатный, а не как деградированный fallback;
6. безопасно обновлять managed-часть системы без потери project data;
7. не сталкиваться с необъяснимым drift между `task.md`, `registry.md` и read-model.

## 3. Что должно входить в `v1`, а что нет

### Обязательный scope `v1`

- канонический `knowledge/`-контур с `task.md`, `plan.md`, `sdd.md`, `artifacts/`;
- install/check/doctor/upgrade контур и его governance-правила;
- task routing `текущая задача / подзадача / новая задача`;
- task branch sync и минимально достаточный publish-flow;
- операторский read-only CLI `status`, `current-task`, `task show`;
- validated adoption playbook для `clean`, `mixed_system`, `compatible/1c`;
- warning-first read-model вместо молчаливых догадок;
- доказательная модель через task-local artifacts и `verification-matrix`.

### Сознательно не входит в `v1`

- полная XML-экосистема contract-first уровня отдельного engineering framework;
- semantic block markup по всему коду проекта;
- rich module graph и module-level query language;
- универсальная execution platform для любых инженерных процессов;
- попытка конкурировать с GRACE по всей методологической поверхности.

## 4. Почему это не просто "возьмём GRACE"

`grace-marketplace` уже решает другую задачу и решает её заметно глубже:

- это contract-first engineering framework;
- у него есть зрелая skill-линейка `init/plan/verification/execute/fix/review/status/cli`;
- у него есть собственный CLI, artifact query и semantic markup model;
- он ориентирован на shared XML artifacts, module graph и verification-driven engineering.

Это сильный аргумент не расширять `task-centric-knowledge` туда же.

Но из этого не следует, что `task-centric-knowledge` надо автоматически выбросить.
Если продуктовая цель уже другая, отдельное существование остаётся рациональным.

## 5. Жёсткая граница между продуктами

### `task-centric-knowledge`

- владеет task lifecycle внутри репозитория;
- владеет task-local source of truth;
- владеет branch/status/publish synchronization на уровне задачи;
- владеет install/upgrade governance knowledge-системы;
- даёт минимальный operator UX для работы с задачами.

### `GRACE`

- владеет contract-first инженерным процессом;
- владеет проектными XML-артефактами, graph и semantic markup;
- владеет module-level planning, verification planning и artifact query;
- даёт более широкий engineering framework и companion CLI.

## 6. Матрица решений: `standalone / adapter / pivot`

### Вариант `standalone`

Продолжаем `task-centric-knowledge` отдельно,
если хотим именно task-centric operating system для произвольных репозиториев,
включая проекты, где тяжёлый GRACE-процесс избыточен.

Это оправдано только если:

- `v1` остаётся компактным по формуле;
- система реально работает как repo-embedded task OS;
- дальнейшее развитие идёт в сторону polish, adoption и adapter surfaces,
  а не в сторону бесконечного наращивания методологии.

### Вариант `adapter`

Строим адаптерный мост,
если хотим сохранить сильную task-local lifecycle модель `task-centric-knowledge`,
но признать GRACE основным spec/contract framework.

Тогда `task-centric-knowledge` становится верхним task/governance слоем,
а GRACE подключается как companion для contract-first и module-level engineering.

### Вариант `pivot`

Останавливаем самостоятельное развитие,
если desired `v1` по факту требует:

- полноценного spec-kit;
- graph-driven навигации;
- semantic markup контракта в коде;
- execution/review/fix framework уровня GRACE.

В этом случае честнее брать GRACE как основной продукт,
а из `task-centric-knowledge` сохранить только полезные идеи миграции или task-local governance.

## 7. Решение задачи

Финальное решение задачи, подтверждённое пользователем `2026-04-14`:

- базовая траектория: `standalone`, но только в узкой формуле task-centric OS;
- резервная траектория: `adapter`, если пользователю позже понадобится единый стек `task lifecycle + contract-first engineering`;
- запрещённая траектория: пытаться превратить `task-centric-knowledge` в "свой собственный GRACE".

Иными словами:
отдельное развитие оправдано не потому, что продукт "тоже умеет workflow",
а потому, что у него другая минимальная единица ценности —
не модульный engineering graph, а управляемая задача внутри репозитория.

## 8. Release-gates для `v1`

`task-centric-knowledge v1` нельзя считать выпущенным, пока не выполняются все пункты:

1. knowledge-контур устанавливается и обновляется без потери project data;
2. новая задача открывается и синхронизируется без ручной магии вне задокументированного validated bootstrap;
3. `status/current-task/task show` дают предсказуемый operator UX;
4. task-local source of truth не расходится с `registry.md` и read-model по устранимым причинам;
5. локальный git/publish lifecycle работает как штатный сценарий;
6. пользователь может коротко объяснить, зачем брать этот продукт вместо GRACE.

## 9. Когда дальнейшее развитие нужно остановить

- если новый scope снова требует full framework-поверхность уровня GRACE;
- если без GRACE-подобных артефактов продукт не может доказать свою полезность;
- если пользовательская ценность не формулируется короче, чем "это ещё одна методология для агентов";
- если основная мотивация развития сводится к тому, что работа уже проделана и жалко её бросать.

## 10. Практический следующий шаг после этой задачи

После закрытия `TASK-2026-0021` следующий delivery backlog должен идти только из одного из двух направлений:

- `standalone-v1 finish`: добить release-gates и сделать `task-centric-knowledge v1` реально поставляемым как task OS;
- `adapter-to-grace`: описать явный мост `task-centric knowledge lifecycle -> GRACE contract workflow`.

Третьего направления быть не должно:
"ещё немного поразвивать и потом решить" — это и есть текущее зависание, которое задача обязана закрыть.
