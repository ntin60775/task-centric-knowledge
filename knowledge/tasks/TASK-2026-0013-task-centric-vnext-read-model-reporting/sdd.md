# SDD по задаче TASK-2026-0013

## Паспорт SDD

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0013` |
| Статус | `завершено` |
| Версия | `5` |
| Дата обновления | `2026-04-13` |

## 1. Проблема и цель

### Проблема

В `TASK-2026-0008` операторский CLI contract уже был определён,
но в runtime отсутствовал отдельный read-only слой для `status`, `current-task` и `task show`.
Из-за этого операторский UX оставался привязанным к mutate-helper и task-local документам.

### Цель

Сделать read-model слой, который:

- даёт команды `status`, `current-task`, `task show`;
- использует канонические данные `Task Core`;
- показывает warnings при неоднозначности, drift и legacy-fallback;
- не переопределяет смысл задачи и её summary;
- не смешивается с mutate- и governance-entrypoint.

## 2. Архитектура и границы

### Целевой runtime-разрез

Read-model живёт внутри `skills-global/task-centric-knowledge/scripts/task_workflow_runtime/`.

- `read_model.py`
  - discovery задач по `knowledge/tasks/**/task.md`;
  - projection `TaskSnapshot`, `CurrentTaskResolution`, `StatusSnapshot`;
  - policy `branch -> task-scoped dirty fallback -> warning`;
  - drift/warning detection для `registry.md`, delivery units и managed-block state.
- `query_cli.py`
- отдельный transport-слой только для чтения;
  - subcommands `status`, `current-task`, `task show`;
  - formatter `text/json`.
- `scripts/task_query.py`
  - тонкий facade-entrypoint без доменной логики и без мутаций.

### Источник истины

- `task.md` остаётся владельцем `TASK-ID`, `Краткого имени`, `Человекочитаемого описания`, `Статуса`, `Ветки` и delivery units;
- `registry.md` используется только как navigation cache и источник drift-сигналов;
- read-model не пишет в `task.md`, `registry.md` и git.

### Транспорт и селекторы

- transport-layer закреплён отдельным `scripts/task_query.py`;
- `task show` v1 поддерживает только `current` и точный `TASK-ID`;
- `task_workflow.py` и `install_skill.py` не расширяются до operator-query surface.

## 3. Полный invariant set

- `INV-0013-01`: task-oriented output всегда включает `TASK-ID`, `Краткое имя`, `Человекочитаемое описание`;
- `INV-0013-02`: read-model не переопределяет `task.md` и `registry.md`, а использует их только как source-of-truth и cache;
- `INV-0013-03`: `current-task` корректно различает `resolved|ambiguous|unresolved`, а в resolved-сценарии показывает текущий этап, следующий шаг и блокеры или ручной остаток;
- `INV-0013-04`: `status` показывает активную ветку, состояние knowledge-контура и предупреждения о неоднозначности или drift;
- `INV-0013-05`: `task show` раскрывает карточку задачи без скрытого обращения к новым источникам истины.
- `INV-0013-06`: malformed delivery rows и missing `TASK-ID` selector не роняют reporting surface, а поднимаются как warning/error payload;
- `INV-0013-07`: health- и legacy-warning ветки (`knowledge_missing`, `registry_missing`, `managed_block_invalid`, `summary_fallback_goal`, `next_step_missing`) имеют regression coverage.
- `INV-0013-08`: publish-контур поднимает warnings для финальной задачи с незакрытыми delivery units, включая `planned`, и для неканоничных `host` / `publication_type` / `cleanup`.
- `INV-0013-09`: duplicate `TASK-ID` и publish-строки с неверным числом колонок не теряются молча: exact selector становится `ambiguous`, а malformed row поднимает warning.

## 4. Новые интерфейсы и данные

### CLI-контракт

```bash
python3 scripts/task_query.py --project-root /abs/project status --format json
python3 scripts/task_query.py --project-root /abs/project current-task --format json
python3 scripts/task_query.py --project-root /abs/project task show current --format json
python3 scripts/task_query.py --project-root /abs/project task show TASK-2026-0013
```

### Payload и policy

- `status` отдаёт `project_root`, `active_branch`, `knowledge_health`, `current_task`, `task_counters`, `high_priority_open`, `review_tasks`, `open_delivery_units`, `warnings`;
- `current-task` отдаёт `resolution` со статусом `resolved|ambiguous|unresolved` и не выбирает задачу молча;
- `task show` отдаёт task snapshot с goal/current stage/files/verify/subtasks/delivery units;
- если `Человекочитаемое описание` отсутствует, v1 допускает fallback из `## Цель` с warning `summary_fallback_goal`;
- tie parent/subtask на одной ветке разрешается только через ownership самого глубокого dirty path.
- malformed delivery row пропускается из snapshot, но фиксируется warning `delivery_unit_parse_error`;
- delivery row с неверным числом колонок тоже фиксируется warning `delivery_unit_parse_error`, а в финальной задаче дополнительно поднимает `final_task_with_open_delivery_units`;
- финальная задача поднимает `final_task_with_open_delivery_units`, если есть любой delivery unit вне `merged|closed`, включая `planned`.
- exact `task show <TASK-ID>` возвращает `ambiguous`, если в knowledge-контуре обнаружены несколько карточек с одинаковым `ID задачи`.

## 5. Этапы реализации и проверки

### Этап 1. Output contract

- зафиксировать subcommands и payload `status/current-task/task show`;
- отделить transport-layer в `scripts/task_query.py`;
- Verify:
  `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules task show TASK-2026-0013`

### Этап 2. Projection runtime

- реализовать task discovery, current-task resolver, drift warnings и formatter;
- не допустить импорта governance runtime или mutate-helper policy;
- Verify:
  `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_query.py`
  `python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_query_architecture.py`

### Этап 3. Acceptance

- прогнать полный discover-набор тестов skill-а;
- синхронизировать task-local и skill-level документы;
- Verify:
  `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'`
  `git diff --check`
  `scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0013-task-centric-vnext-read-model-reporting/task.md knowledge/tasks/TASK-2026-0013-task-centric-vnext-read-model-reporting/plan.md knowledge/tasks/TASK-2026-0013-task-centric-vnext-read-model-reporting/sdd.md knowledge/tasks/TASK-2026-0013-task-centric-vnext-read-model-reporting/artifacts/verification-matrix.md skills-global/task-centric-knowledge/SKILL.md skills-global/task-centric-knowledge/references/task-workflow.md`

## 6. Критерии приёмки

1. `status`, `current-task`, `task show` работают как read-only operator surface.
2. Task summary contract соблюдается во всех task-oriented ответах.
3. Ambiguity handling, health warnings и malformed-delivery scenarios покрыты тестами.
4. Read-model не вводит новый источник истины.
5. Новый facade остаётся тонким entrypoint без доменной логики.

## 7. Стоп-критерии

1. Operator-команды требуют мутировать данные для получения ответа.
2. Projection начинает расходиться с `task.md`.
3. Для реализации приходится расширять scope задачи в governance или memory-layer.
4. Dirty fallback начинает молча выбирать родительскую задачу вместо более точной подзадачи.
