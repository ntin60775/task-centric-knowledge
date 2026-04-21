# Реестр audit-gates по задаче TASK-2026-0008

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0008` |
| Артефакт | `audit-gates` |
| Версия | `10` |
| Дата обновления | `2026-04-12` |
| Статус | `завершено` |

## Правило фиксации

Этот файл является каноническим местом для фиксации результатов audit-gates из `sdd.md` и `plan.md`.
Назвать gate недостаточно: после фактического прохождения для него обязателен явный статус, дата и краткое evidence.

Допустимые статусы:

- `planned` — gate ещё не проходился;
- `pass` — gate пройден;
- `fail` — gate не пройден;
- `manual-residual` — автопроверки пройдены, но остался зафиксированный ручной остаток.

## Подготовка к старту Этапа 1

Для `SDD_AUDIT` до фактического прогона должны быть подготовлены:

- отдельный `artifacts/stage-1-audit.md`, где изолированно видны локальные симптомы и lessons learned;
- канонический набор внешних ориентиров только по официальным источникам;
- список открытых вопросов, которые передаются в Этап 2 без преждевременного выбора траектории;
- трассировка Этапа 1 к `INV-02` и `INV-04` в `artifacts/verification-matrix.md`.

Строка `SDD_AUDIT` не переводится из `planned`, если в `Evidence / вывод` нельзя коротко сослаться на все четыре элемента внутри изолированного `artifacts/stage-1-audit.md`: локальные симптомы, lessons learned, официальный source-set и открытые вопросы для Этапа 2.

## Подготовка к старту Этапа 3

Для `ARCHITECTURE_AUDIT` до фактического прогона должны быть подготовлены:

- `sdd.md` с DDD-картой контекстов, границами владения агрегатом и минимальным `vNext-core contract`;
- `artifacts/strategy-roadmap.md` с явной границей `что входит в ядро / что остаётся расширяемым слоем / что ещё не выбирается на Этапе 3`;
- `artifacts/cli-ux-draft.md` с публичной поверхностью `status`, `current-task`, `task show`, `doctor deps`, `migrate cleanup plan/confirm`, включая обязательный заголовок задачи, поведение на неоднозначности и cleanup-governance;
- `artifacts/verification-matrix.md`, где `VERIFY-0008-03`, `VERIFY-0008-07`, `VERIFY-0008-08`, `VERIFY-0008-09`, `VERIFY-0008-10`, `VERIFY-0008-12`, `VERIFY-0008-13` уже трассируются к инвариантам Этапа 3;
- явное правило, что все доказательные артефакты хранятся внутри каталога задачи или имеют явную ссылку из него.

Строка `ARCHITECTURE_AUDIT` не переводится из `planned`, если нельзя коротко сослаться на четыре блока evidence: целевая форма `vNext`, DDD-границы, операторский CLI-контракт и правило локального хранения evidence.

## Подготовка к старту Этапа 4

Для `INTEGRATION_AUDIT` до фактического прогона должны быть подготовлены:

- `artifacts/strategy-roadmap.md` с фазами `0..4`, переходными воротами, stop-критериями антиразрастания и очередью следующей волны candidate delivery-tracks;
- `skills-global/task-centric-knowledge/references/roadmap.md` как сокращённый snapshot тех же фаз, ворот и stop-ворот без конкурирующего источника истины;
- `artifacts/verification-matrix.md`, где `VERIFY-0008-05`, `VERIFY-0008-06` и `VERIFY-0008-14` явно трассируются к фазовой roadmap, anti-bloat и иерархии источников истины;
- `task.md`, в котором Этап 4 зафиксирован как закрытый стратегический пакет, а следующим активным этапом объявлен Этап 5.

Строка `INTEGRATION_AUDIT` не переводится из `planned`, если нельзя коротко сослаться на четыре блока evidence: фазовую карту `0..4`, переходные gate-ы, anti-bloat stop-критерии и синхронную очередь следующей волны candidate delivery-tracks.

## Подготовка к старту Этапа 5

Для `REVIEW_CLOSURE_AUDIT` до фактического прогона должны быть подготовлены:

- `artifacts/review-findings-closure.md` с явной картой: что уже закрыто Этапами 2-4, что снято исторической синхронизацией ветки, а что составляет активный пакет `FIND-09`, `FIND-11`, `FIND-12`, `FIND-13`;
- `artifacts/verification-matrix.md`, где `VERIFY-0008-11`, `VERIFY-0008-14`, `VERIFY-0008-15`, `VERIFY-0008-OPENAI` однозначно трассируются к `INV-11`, `INV-14`, `INV-15` и не оставляют `planned`-состояний в финальном контуре;
- `task.md` и `knowledge/tasks/registry.md`, синхронные по статусу задачи и канонической summary;
- `skills-global/task-centric-knowledge/agents/openai.yaml`, `task_workflow.py` и `test_task_workflow.py`, которые подтверждают scope skill-а и helper-level sync без новой runtime-функциональности.

Строка `REVIEW_CLOSURE_AUDIT` не переводится из `planned`, если нельзя коротко сослаться на четыре блока evidence: карту closure по findings, helper/registry sync, корректный scope `agents/openai.yaml` и финальное решение по имени skill-а.

## Реестр gate-ов

| Gate | Этап | Что подтверждает | Основание закрытия | Статус | Дата | Evidence / вывод |
|------|------|------------------|--------------------|--------|------|------------------|
| `SDD_AUDIT` | `Этап 1` | Полноту инвариантов, связь стратегии с локальным состоянием skill-а и корректный scope задачи | `VERIFY-0008-02`, `VERIFY-0008-04` | `pass` | `2026-04-12` | `artifacts/stage-1-audit.md` изолированно фиксирует локальные симптомы, lessons learned, официальный source-set и открытые вопросы для Этапа 2; усиленные `VERIFY-0008-02` и `VERIFY-0008-04` пройдены без опоры на агрегированные результаты следующих этапов |
| `DECISION_AUDIT` | `Этап 2` | Явное стратегическое решение `continue own path / borrow ideas / do not fork / do not rewrite now` | `VERIFY-0008-01`, `VERIFY-0008-14` | `pass` | `2026-04-12` | В `artifacts/strategy-roadmap.md` закрыты все открытые вопросы Этапа 2, зафиксирован единый пакет стратегического решения и классификация `обязательно сейчас / отложить`; `artifacts/review-findings-closure.md` и `skills-global/task-centric-knowledge/references/roadmap.md` синхронизированы с тем же source-set и правилом приоритета; `VERIFY-0008-01` и `VERIFY-0008-14` пройдены |
| `ARCHITECTURE_AUDIT` | `Этап 3` | Целевую архитектуру `vNext`, CLI-контракт, DDD-границы и правило локального хранения evidence | `VERIFY-0008-03`, `VERIFY-0008-07`, `VERIFY-0008-08`, `VERIFY-0008-09`, `VERIFY-0008-10`, `VERIFY-0008-12`, `VERIFY-0008-13` | `pass` | `2026-04-12` | `sdd.md`, `artifacts/strategy-roadmap.md` и `artifacts/cli-ux-draft.md` синхронно фиксируют `vNext-core`, ограниченные контексты, публичную CLI-поверхность и cleanup-сценарий с фиксированным scope; все семь verify-команд Этапа 3 пройдены, локальное хранение evidence поднято в инвариант ядра |
| `INTEGRATION_AUDIT` | `Этап 4` | Фазовую roadmap, ворота перехода, stop-критерии и синхронизацию task-local / skill-level roadmap | `VERIFY-0008-05`, `VERIFY-0008-06`, `VERIFY-0008-14` | `pass` | `2026-04-12` | `artifacts/strategy-roadmap.md` и `skills-global/task-centric-knowledge/references/roadmap.md` синхронно фиксируют фазы `0..4`, gate-ы перехода, anti-bloat stop-ворота и очередь пяти candidate delivery-tracks; `task.md` переводит активный шаг на Этап 5, а verify-команды Этапа 4 проходят без захода в runtime-реализацию |
| `REVIEW_CLOSURE_AUDIT` | `Этап 5` | Закрытие замечаний ревью, sync `registry.md`, корректность имени skill-а и scope `agents/openai.yaml` | `VERIFY-0008-11`, `VERIFY-0008-14`, `VERIFY-0008-15`, `VERIFY-0008-OPENAI` | `pass` | `2026-04-12` | `artifacts/review-findings-closure.md` отделяет findings, уже закрытые Этапами 2-4, от активного stage-5 пакета `FIND-09`, `FIND-11`, `FIND-12`, `FIND-13`; `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_workflow.py`, `VERIFY-0008-11`, `VERIFY-0008-14`, `VERIFY-0008-15` и `VERIFY-0008-OPENAI` пройдены; `task.md`, `knowledge/tasks/registry.md` и `agents/openai.yaml` синхронно подтверждают финальный closure без дополнительного Этапа 6 |
