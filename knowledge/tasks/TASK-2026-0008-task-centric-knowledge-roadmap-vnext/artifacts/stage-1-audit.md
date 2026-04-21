# Изолированное evidence Этапа 1 по задаче TASK-2026-0008

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0008` |
| Артефакт | `stage-1-audit` |
| Версия | `1` |
| Дата обновления | `2026-04-12` |
| Статус | `изолированное evidence для SDD_AUDIT` |

## Назначение

Этот файл фиксирует только доказательную базу Этапа 1: локальный аудит и внешний landscape.
Он не принимает финальную стратегию `redesign / fork / rewrite`, не закрывает Этапы 2-4 и не заменяет сводный `artifacts/strategy-roadmap.md`.

Для `SDD_AUDIT` источником evidence считается именно этот артефакт.
`artifacts/strategy-roadmap.md` агрегирует результаты следующих этапов и поэтому не должен использоваться как единственное основание закрытия Этапа 1.

## Что именно должен доказывать Этап 1

- локальные архитектурные симптомы привязаны к реальным файлам и уже выполненным задачам;
- lessons learned из `TASK-2026-0004`, `TASK-2026-0006`, `TASK-2026-0007` подняты как ограничения следующего цикла;
- внешний landscape собран только по официальным первичным источникам;
- для Этапа 2 подготовлены открытые вопросы без преждевременного финального выбора траектории.

## Инвентаризация локального состояния

- `TASK-2026-0004` уже добавила git-aware жизненный цикл, маршрутизацию задач и безопасный upgrade-переход.
- `TASK-2026-0006` уже добавила testing contract и `verification-matrix`.
- `TASK-2026-0007` уже добавила delivery units, publish-flow и закрыла GitHub smoke-gate.
- Основные технические носители текущей сложности:
  - `skills-global/task-centric-knowledge/scripts/task_workflow.py`
  - `skills-global/task-centric-knowledge/scripts/install_skill.py`
  - `skills-global/task-centric-knowledge/agents/openai.yaml`

## Локальные симптомы

- Монолитность orchestration-слоя:
  ключевой носитель логики сосредоточен в `skills-global/task-centric-knowledge/scripts/task_workflow.py`.
- Drift между каноническим `task.md` и навигационным `registry.md`:
  симптом поднят в `TASK-2026-0008` и должен закрываться только через helper sync.
- Нормативное дублирование:
  одно правило часто приходится синхронно менять в `SKILL.md`, `references/*.md`, managed-блоках, `knowledge/tasks/README.md`, шаблонах и тестах.
- Drift metadata относительно фактического scope:
  `skills-global/task-centric-knowledge/agents/openai.yaml` должен успевать за capability, добавленными задачами `TASK-2026-0006` и `TASK-2026-0007`.

## Lessons learned как ограничения

- `TASK-2026-0004` запрещает терять git-aware жизненный цикл, безопасный upgrade-переход и явную маршрутизацию задач.
- `TASK-2026-0006` требует, чтобы стратегия оставалась проверяемой через `verification-matrix`, а не превращалась в набор мнений без трассировки.
- `TASK-2026-0007` уже вынес publish-flow в отдельный контур и закрыл внешний smoke; следующий цикл не должен тащить host-specific publish-логику обратно в ядро.

## Канонический внешний landscape Этапа 1

| Ориентир | Официальные источники | Что заимствовать | Почему не база для `full fork` |
|----------|------------------------|------------------|---------------------------------|
| `GitHub Spec Kit` | `github.com/github/spec-kit`; `github.github.com/spec-kit` | `specification layer` и фазность `spec -> plan -> tasks -> implement` | это feature-spec workflow, а не repo-local task operating model |
| `Claude Code` | `docs.anthropic.com/en/docs/claude-code/memory`; `docs.anthropic.com/en/docs/claude-code/sub-agents` | scoped memory и контракт субагентов | это agent runtime, а не дистрибутив knowledge-системы задач |
| `Cursor` | `docs.cursor.com/en/context/rules`; `docs.cursor.com/en/context/memories` | совместимость с project rules и предупреждения о drift между слоями инструкций | это IDE/context layer без task registry, delivery units и install/upgrade governance |
| `memories.sh` | `memories.sh`; `memories.sh/docs` | дорожки памяти `session`, `semantic`, `episodic`, `procedural` | это система памяти, а не система ведения задач с `task.md / plan.md / sdd.md / registry.md` |
| `Память GitHub Copilot / VS Code` | `code.visualstudio.com/docs/copilot/agents/memory`; `docs.github.com/en/copilot/how-tos/use-copilot-agents/copilot-memory` | явные области памяти и memory с подтверждёнными источниками | вендорская память не заменяет git-tracked task workflow |
| `Devin` | `docs.devin.ai/product-guides/knowledge` | onboarding на уровне репозитория и триггеры извлечения знаний | это knowledge overlay, а не операционная модель задачи внутри репозитория |
| `OpenHands` | `docs.openhands.dev/sdk/guides/task-tool-set`; `docs.all-hands.dev/usage/prompting/microagents-overview`; `docs.all-hands.dev/openhands/usage/microagents/microagents-repo` | machine-executable subtask flow и packaging микроправил | это orchestration/tooling layer, а не task-centric knowledge-дистрибутив |
| `LangChain Deep Agents` | `docs.langchain.com/oss/python/deepagents/index`; `docs.langchain.com/oss/python/deepagents/long-term-memory`; `docs.langchain.com/oss/python/deepagents/human-in-the-loop` | backend/policy separation и дисциплина writable/read-only memory | это agent harness, а не готовый repo-local task workflow-дистрибутив |
| `Агентные workflows GitHub` | `github.github.com/gh-aw`; `github.github.com/gh-aw/reference/memory`; `github.github.com/gh-aw/introduction/how-they-work/` | package-слой, lock/governance и воспроизводимость | это GitHub Actions-oriented execution framework, а не repo-local task operating model |

## Открытые вопросы для Этапа 2

- Какие заимствования из внешнего landscape являются обязательной частью ближайшего `vNext-core`, а какие остаются deferred-слоем.
- Где проходит минимальная граница между `core contract` и первой волной модульной декомпозиции без скатывания в `full rewrite`.
- Какие локальные симптомы считаются блокерами следующего цикла, а какие остаются управляемым техническим долгом.
- Какой набор формулировок должен перейти из task-local стратегии в дистрибутивный snapshot без потери иерархии источников истины.

## Итого по Этапу 1

- evidence Этапа 1 изолировано от решений следующих этапов;
- локальные симптомы и lessons learned связаны с конкретными файлами и предыдущими задачами;
- официальный source-set собран в одном месте и для каждого ориентира зафиксированы границы заимствования;
- открытые вопросы переданы в Этап 2 без преждевременного выбора траектории.
