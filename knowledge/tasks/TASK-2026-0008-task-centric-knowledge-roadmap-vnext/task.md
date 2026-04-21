# Карточка задачи TASK-2026-0008

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0008` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0008` |
| Технический ключ для новых именуемых сущностей | `vnext-core` |
| Краткое имя | `task-centric-knowledge-roadmap-vnext` |
| Человекочитаемое описание | Стратегический пакет vNext для развития `task-centric-knowledge` как операционной системы задач внутри репозитория |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `task/task-2026-0008-task-centric-knowledge-roadmap-vnext` |
| Требуется SDD | `да` |
| Статус SDD | `завершено` |
| Ссылка на SDD | `sdd.md` |
| Дата создания | `2026-04-10` |
| Дата обновления | `2026-04-12` |

## Цель

Сформировать для `task-centric-knowledge` чёткую стратегию следующего этапа развития: определить конечную целевую форму системы, принять решение между эволюцией, redesign и форком от внешнего решения, выбрать курс `redesign ядра без full rewrite`, зафиксировать операторский CLI-контракт и разложить путь на проверяемые промежуточные результаты.

## Границы

### Входит

- Стратегический аудит текущего состояния `task-centric-knowledge`.
- Явное решение по траектории: `эволюция / redesign / fork / borrow ideas`.
- Сравнение с актуальными внешними системами и подходами.
- Архитектурная цель `vNext` и границы ядра.
- Черновик операторского CLI UI/UX для query/reporting, diagnostics и migration cleanup.
- Пошаговая дорожная карта с контрольными воротами.
- Синхронизация task-local roadmap с дистрибутивной roadmap skill-а и interface metadata `agents/openai.yaml`.
- Исправление sync-логики `task_workflow.py` для канонического поля `Человекочитаемое описание` и устранение drift в `registry.md`.

### Не входит

- Немедленная реализация всей `vNext`-архитектуры.
- Массовый рефакторинг `task_workflow.py` в рамках этой задачи.
- Выбор одного конкретного forge/provider для production-интеграции.

## Контекст

- источник постановки: запрос пользователя от `2026-04-10` о дальнейшем развитии навыка, необходимости roadmap и проверке сценариев `переосмыслить с нуля` / `форкнуться от лучшей системы`;
- связанная бизнес-область: knowledge-driven workflow для агентной разработки и сопровождения задач в git-репозиториях;
- ограничения и зависимости: решение должно опираться на текущую реальность skill-а, не игнорировать уже вложенные итерации `TASK-2026-0004`, `TASK-2026-0006`, `TASK-2026-0007` и не подменять стратегию абстрактным wishlist;
- исходный наблюдаемый симптом / лог-маркер: `не требуется`;
- основной контекст сессии: `текущая задача`.

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | Обновляются `skills-global/task-centric-knowledge/scripts/task_workflow.py` и `skills-global/task-centric-knowledge/tests/test_task_workflow.py` для sync канонической сводки задачи в `registry.md` |
| Конфигурация / схема данных / именуемые сущности | Целевая доменная модель `task`, `subtask`, `delivery unit`, `verification matrix`, memory lanes и adapter surfaces |
| Skill metadata | Синхронизация `skills-global/task-centric-knowledge/agents/openai.yaml` с фактическим scope skill-а |
| Интерфейсы / формы / страницы | Операторский CLI UX: `status`, `current-task`, `task show`, `doctor deps`, `migrate cleanup` |
| Интеграции / обмены | GitHub / GitLab / agent-memory подходы рассматриваются как ориентиры и источники идей |
| Документация | `task.md`, `plan.md`, `sdd.md`, `artifacts/stage-1-audit.md`, `artifacts/verification-matrix.md`, `artifacts/strategy-roadmap.md`, `artifacts/cli-ux-draft.md`, `artifacts/audit-gates.md`, `artifacts/review-findings-closure.md`, `skills-global/task-centric-knowledge/references/roadmap.md` |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/`
- файл плана: `plan.md`
- файл SDD: `sdd.md`
- изолированное evidence Этапа 1: `artifacts/stage-1-audit.md`
- файл verification matrix: `artifacts/verification-matrix.md`
- стратегический артефакт: `artifacts/strategy-roadmap.md`
- дистрибутивный снимок roadmap: `skills-global/task-centric-knowledge/references/roadmap.md`
- interface metadata skill-а: `skills-global/task-centric-knowledge/agents/openai.yaml`
- helper sync задачи: `skills-global/task-centric-knowledge/scripts/task_workflow.py`
- тесты helper-а: `skills-global/task-centric-knowledge/tests/test_task_workflow.py`
- навигационный кэш задач: `knowledge/tasks/registry.md`
- черновик CLI UX: `artifacts/cli-ux-draft.md`
- артефакт audit-gates: `artifacts/audit-gates.md`
- закрытие замечаний ревью: `artifacts/review-findings-closure.md`
- пользовательские материалы: сообщения пользователя от `2026-04-10`
- связанные коммиты / PR / ветки: ветку и связанные commit-ы фиксировать по мере появления
- связанные операции в `knowledge/operations/`, если есть: `нет`

## Контур публикации

Delivery unit для этой задачи не требуется: результатом является стратегия и knowledge-артефакты, а не отдельная publish-поставка.

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | — | `—` | `—` | `none` | `none` | `closed` | `—` | `—` | `не требуется` |

## Текущий этап

Этап 1 закрыт: в `artifacts/stage-1-audit.md` изолированно зафиксированы локальные симптомы, lessons learned, канонический официальный source-set и открытые вопросы для Этапа 2, а `SDD_AUDIT` переведён в `pass` без опоры на агрегированные результаты следующих этапов.
Этап 2 закрыт: принято решение `continue own path`, `borrow ideas`, `do not fork`, `do not rewrite now`, выбран курс `redesign ядра без full rewrite`, а task-local `artifacts/strategy-roadmap.md` закреплён как канонический стратегический источник при синхронизированном skill-level snapshot.
Этап 3 закрыт: `sdd.md`, `artifacts/strategy-roadmap.md` и `artifacts/cli-ux-draft.md` согласованы по `vNext-core`, ограниченным контекстам, публичной CLI-поверхности и правилу локального хранения evidence; `ARCHITECTURE_AUDIT` переведён в `pass` после прохождения `VERIFY-0008-03`, `VERIFY-0008-07`, `VERIFY-0008-08`, `VERIFY-0008-09`, `VERIFY-0008-10`, `VERIFY-0008-12`, `VERIFY-0008-13`.
Этап 4 закрыт: task-local `artifacts/strategy-roadmap.md` и skill-level `skills-global/task-centric-knowledge/references/roadmap.md` синхронизированы по фазам `0..4`, воротам перехода, stop-критериям антиразрастания и очереди следующей волны candidate delivery-tracks; `INTEGRATION_AUDIT` переведён в `pass` после прохождения `VERIFY-0008-05`, `VERIFY-0008-06` и повторной сверки `VERIFY-0008-14`.
Этап 5 закрыт: `artifacts/review-findings-closure.md`, `artifacts/verification-matrix.md`, `artifacts/audit-gates.md`, `task.md` и `knowledge/tasks/registry.md` синхронизированы по активному пакету закрытия `FIND-09`, `FIND-11`, `FIND-12`, `FIND-13`; `REVIEW_CLOSURE_AUDIT` переведён в `pass` после прохождения `VERIFY-0008-11`, `VERIFY-0008-14`, `VERIFY-0008-15`, `VERIFY-0008-OPENAI` и unit-тестов helper-а.
Задача завершена: стратегический пакет `vNext`, CLI-контракт, иерархия roadmap, metadata scope и helper-level sync доведены до согласованного итогового состояния без открытия дополнительного Этапа 6.

## Стратегия проверки

### Фактически выполненные автопроверки

- `scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/task.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/plan.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/sdd.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/stage-1-audit.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/verification-matrix.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/strategy-roadmap.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/cli-ux-draft.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/audit-gates.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/review-findings-closure.md skills-global/task-centric-knowledge/references/roadmap.md`
- `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_workflow.py`
- `git diff --check`
- Воспроизводимые команды `VERIFY-0008-01` ... `VERIFY-0008-15` и `VERIFY-0008-OPENAI` из `artifacts/verification-matrix.md`

### Итоговый ручной остаток

- Дополнительных ручных проверок для финального этапа закрытия не требуется: стратегические оценки масштаба, source-set и CLI UX уже закреплены артефактами Этапов 1-4, а Этап 5 закрыт воспроизводимым verify-контуром.

## Критерии готовности

На `2026-04-12` критерии готовности закрыты:

- Есть явное решение, продолжать ли текущую систему, делать ли redesign или искать fork.
- Выбранный redesign-курс назван без двусмысленности: `redesign ядра без full rewrite`.
- Есть внешнее сравнение как минимум с несколькими актуальными системами или подходами.
- Зафиксирована конечная цель `vNext` и границы ядра.
- Зафиксирован минимальный CLI-контракт для `status`, `current-task`, `task show`, `doctor deps` и `migrate cleanup`.
- Закрыты замечания контрольного ревью по источнику истины, иерархии дорожных карт, DDD-границам и хранению доказательных артефактов.
- Дистрибутивная roadmap и `agents/openai.yaml` не противоречат task-local стратегии.
- Helper `task_workflow.py` синхронизирует `Человекочитаемое описание` из `task.md` в `registry.md` без drift на новых и уже существующих строках.
- Строка `TASK-2026-0008` в `knowledge/tasks/registry.md` совпадает с каноническим описанием из `task.md`.
- Есть фазовая roadmap с промежуточными результатами и стоп-критериями.
- Результаты audit-gates зафиксированы в `artifacts/audit-gates.md` со статусом, датой и кратким evidence.
- Стратегические артефакты сохранены в knowledge-системе репозитория.

## Итоговый список ручных проверок

- Дополнительных ручных проверок для финального sync-контура не требуется.
- Следующий цикл должен открываться отдельными delivery-задачами только из очереди candidate delivery-tracks, уже зафиксированной в `artifacts/strategy-roadmap.md`.

## Итог

Задача завершена.

Что фактически подготовлено:

- стратегический пакет `vNext` с явным решением `redesign ядра без full rewrite`;
- DDD-карта контекстов, минимальный CLI query/reporting contract и фазовая roadmap `0..4`;
- синхронизация task-local roadmap, skill-level snapshot и `skills-global/task-centric-knowledge/agents/openai.yaml`;
- helper-level контракт для канонической summary задачи и устранение drift между `task.md` и `knowledge/tasks/registry.md`;
- финальный verify/gate-контур, который позволяет закрывать подобные стратегические задачи без двусмысленного ручного residual.

Что доказано фактически:

- audit-gate-ами `SDD_AUDIT`, `DECISION_AUDIT`, `ARCHITECTURE_AUDIT`, `INTEGRATION_AUDIT`, `REVIEW_CLOSURE_AUDIT`;
- unit-тестами `skills-global/task-centric-knowledge/tests/test_task_workflow.py`;
- воспроизводимыми командами `VERIFY-0008-01` ... `VERIFY-0008-15` и `VERIFY-0008-OPENAI`;
- локализационной проверкой Markdown-артефактов и `git diff --check`.

Следующее ограничение намеренное:

- сама `vNext`-архитектура пока не реализуется в этой задаче; дальнейшее движение допускается только через отдельные delivery-задачи из очереди candidate delivery-tracks.
