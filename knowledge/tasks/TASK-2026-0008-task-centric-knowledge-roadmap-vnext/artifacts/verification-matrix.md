# Матрица проверки по задаче TASK-2026-0008

## Когда использовать

Для этой задачи матрица обязательна, потому что без неё стратегическое решение легко превратить в набор мнений без проверяемых инвариантов.

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0008` |
| Связанный SDD | `../sdd.md` |
| Версия | `15` |
| Дата обновления | `2026-04-12` |

Матрица завершена: Этапы 1-5 доказаны воспроизводимыми командами, а финальный синхронизационный контур Этапа 5 закрыт без дополнительных `planned`-строк.

## 1. Канонические инварианты

| Invariant ID | Описание | Источник истины | Где может сломаться |
|--------------|----------|-----------------|---------------------|
| `INV-01` | Есть явное решение по траектории развития | `sdd.md`, `strategy-roadmap.md` | Стратегия останется на уровне вопросов без ответа |
| `INV-02` | Roadmap опирается на реальное текущее состояние skill-а | `sdd.md`, `stage-1-audit.md`, `strategy-roadmap.md` | Внешние идеи вытеснят локальный контекст |
| `INV-03` | Зафиксирована конечная архитектурная цель `vNext` | `strategy-roadmap.md` | Будет только список улучшений без target state |
| `INV-04` | Внешние аналоги рассмотрены по официальным источникам | `stage-1-audit.md`, `strategy-roadmap.md` | Решение по fork будет основано на смутных ассоциациях |
| `INV-05` | Дорожная карта даёт промежуточные фазы и ворота | `strategy-roadmap.md` | Следующие шаги будут неуправляемыми |
| `INV-06` | Стратегия явно уменьшает риск дальнейшего разрастания skill-а | `sdd.md`, `strategy-roadmap.md` | Новые фичи продолжат наращиваться поверх монолита |
| `INV-07` | Есть явный CLI query/reporting contract | `sdd.md`, `cli-ux-draft.md`, `strategy-roadmap.md` | Останутся только внутренние helper-команды без операторского UX |
| `INV-08` | CLI-вывод по задаче требует `TASK-ID + краткое имя + человекочитаемое описание` | `cli-ux-draft.md` | Пользователь будет видеть голые ID без смысла |
| `INV-09` | `doctor deps` различает обязательные, условно-обязательные, опциональные и `not-applicable` зависимости | `cli-ux-draft.md`, `strategy-roadmap.md` | Отсутствие host-инструментов будет выглядеть как поломка всего skill-а |
| `INV-10` | Migration cleanup идёт только через `plan -> confirm` | `cli-ux-draft.md`, `sdd.md` | После миграции можно будет потерять данные из-за молчаливого cleanup |
| `INV-11` | Сводка задачи имеет один источник истины в `task.md`, а helper синхронизирует её в `registry.md` | `task.md`, `cli-ux-draft.md`, `sdd.md`, `task_workflow.py` | `registry.md` снова станет владельцем описания задачи или drift останется незамеченным |
| `INV-12` | DDD-границы и карта контекстов зафиксированы | `sdd.md`, `strategy-roadmap.md` | Слои останутся списком модулей без владения |
| `INV-13` | Доказательные артефакты проверки хранятся в каталоге задачи | `sdd.md`, `strategy-roadmap.md`, `review-findings-closure.md` | Скриншоты, логи и отчёты начнут расползаться вне задачи |
| `INV-14` | Глобальная дорожная карта не конкурирует с дорожной картой задачи | `strategy-roadmap.md`, `skills-global/task-centric-knowledge/references/roadmap.md` | Будет два разных ответа на порядок развития |
| `INV-15` | Имя `task-centric-knowledge` признано корректным для текущего центра продукта | `review-findings-closure.md`, `SKILL.md`, `strategy-roadmap.md` | Переименование будет обсуждаться без изменения центра продукта |

## 2. Матрица покрытия

| Invariant ID | Сценарий нарушения или переход | Автопроверка / команда | Статус покрытия | Примечание |
|--------------|--------------------------------|------------------------|-----------------|------------|
| `INV-01` | В документе нет явного решения `continue / redesign / fork` | `VERIFY-0008-01` | `covered` | Пакет стратегического решения Этапа 2 зафиксирован в `task.md`, `sdd.md` и `strategy-roadmap.md`; курс однозначно назван как `redesign ядра без full rewrite` |
| `INV-02` | Дорожная карта не ссылается на локальные задачи и файлы | `VERIFY-0008-02` | `covered` | Изолированный `stage-1-audit.md` фиксирует связанные задачи, ключевые скрипты, metadata и локальные симптомы, а `sdd.md` и матрица держат трассировку этапа |
| `INV-03` | Есть только идеи, но нет целевой архитектуры | `VERIFY-0008-03` | `covered` | `sdd.md` и `strategy-roadmap.md` синхронно фиксируют целевую форму `vNext`, минимальный `vNext-core contract` и границу между core и расширяемыми слоями |
| `INV-04` | Внешние системы перечислены без источников или source-set расходится между roadmap | `VERIFY-0008-04` | `covered` | Изолированный `stage-1-audit.md` подтверждает для каждого ориентира официальный источник, границу заимствования и отказ от `full fork`; содержательная оценка влияния источников остаётся частью Этапа 2 |
| `INV-05` | Нет фаз и ворот | `VERIFY-0008-05` | `covered` | Task-local и skill-level roadmap синхронно фиксируют фазы `0..4`, gate-ы перехода и очередь следующей волны candidate delivery-tracks |
| `INV-06` | Нет антиразрастания и стоп-критериев | `VERIFY-0008-06` | `covered` | Roadmap запрещает новый рост helper-монолита до стабилизации ядра и фиксирует stop-ворота для пересмотра стратегии |
| `INV-07` | В дорожной карте нет операторской поверхности запросов и отчётности | `VERIFY-0008-07` | `covered` | `cli-ux-draft.md`, `sdd.md` и `strategy-roadmap.md` фиксируют публичную поверхность `status`, `current-task`, `task show`, `doctor deps`, `migrate cleanup` и роль read-модели |
| `INV-08` | В task-выводе допустимы голые ID без понятного названия | `VERIFY-0008-08` | `covered` | `cli-ux-draft.md` фиксирует обязательный заголовок задачи и единый набор полей task-oriented read-модели |
| `INV-09` | `doctor deps` не различает классы зависимостей и слои блокировки | `VERIFY-0008-09` | `covered` | Контракт `doctor deps` разделяет классы зависимостей, статусы и границу `core/local mode` vs `publish/integration` |
| `INV-10` | Cleanup после миграции можно выполнить без явного confirm-flow | `VERIFY-0008-10` | `covered` | `migrate cleanup plan/confirm` закреплён как flow с зафиксированным scope, `TARGETS`, `TARGET_COUNT`, `COUNT`, абсолютными путями и запретом на расширение удаления |
| `INV-11` | Helper продолжает жить на `--summary` или сохраняет drift в `registry.md` вместо канонического поля | `VERIFY-0008-11` | `covered` | Unit-тесты helper-а и отдельная сверка `TASK-2026-0008` подтверждают приоритет `Человекочитаемое описание -> --summary -> ## Цель -> existing cache` и отсутствие drift в nav-cache |
| `INV-12` | DDD остаётся без ограниченных контекстов и владения агрегатом | `VERIFY-0008-12` | `covered` | `sdd.md` и `strategy-roadmap.md` фиксируют ограниченные контексты, границы владения агрегатом и запрет на обход `Task Core` со стороны производных слоёв |
| `INV-13` | Доказательные артефакты можно хранить где угодно без ссылки из задачи | `VERIFY-0008-13` | `covered` | Контракт локального хранения evidence закреплён в `sdd.md`, `strategy-roadmap.md` и closure-документе, включая допуск внешних артефактов только через явную ссылку |
| `INV-14` | Дорожная карта уровня skill-а и дорожная карта задачи дают разные источники истины или разные внешние ориентиры | `VERIFY-0008-14` | `covered` | Иерархия источников истины, общий source-set и единый стратегический вывод синхронизированы для закрытия `DECISION_AUDIT`; изолированный stage-local source-set Этапа 1 отдельно подтверждается `VERIFY-0008-04` |
| `INV-15` | Имя skill-а требует переименования без изменения центра продукта | `VERIFY-0008-15` | `covered` | `review-findings-closure.md`, `SKILL.md` и `strategy-roadmap.md` согласованно фиксируют, что менять нужно позиционирование, а не имя `task-centric-knowledge` |

## 2.1. Подготовка к Этапу 1

| Что должно быть подготовлено | Где фиксируется | Чем подтверждается при закрытии |
|------------------------------|-----------------|----------------------------------|
| Локальный инвентаризационный минимум: ключевые скрипты, metadata и связанные задачи | `stage-1-audit.md`, `sdd.md` | `VERIFY-0008-02` |
| Lessons learned из `TASK-2026-0004`, `TASK-2026-0006`, `TASK-2026-0007` как ограничения следующего цикла | `stage-1-audit.md`, `sdd.md` | `VERIFY-0008-02`, запись `SDD_AUDIT` |
| Канонический внешний source-set только по официальным источникам | `stage-1-audit.md` | `VERIFY-0008-04` |
| Открытые вопросы, которые передаются в Этап 2 без преждевременного решения | `stage-1-audit.md`, `audit-gates.md` | запись `SDD_AUDIT` |
| Явное место фиксации evidence по Этапу 1 | `audit-gates.md` | строка `SDD_AUDIT` с датой и кратким выводом |

## 2.2. Воспроизводимые команды

### `VERIFY-0008-01`

```bash
rg -n "redesign ядра без full rewrite|Переписывать с нуля не нужно|Не форкаться целиком|own core \\+ modular evolution" knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/strategy-roadmap.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/task.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/sdd.md
```

### `VERIFY-0008-02`

```bash
python3 -c 'from pathlib import Path; files={"audit":Path("knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/stage-1-audit.md"),"workflow":Path("skills-global/task-centric-knowledge/scripts/task_workflow.py"),"install":Path("skills-global/task-centric-knowledge/scripts/install_skill.py"),"metadata":Path("skills-global/task-centric-knowledge/agents/openai.yaml"),"sdd":Path("knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/sdd.md"),"matrix":Path("knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/verification-matrix.md")}; texts={k:p.read_text(encoding="utf-8") for k,p in files.items()}; checks={"audit":["## Инвентаризация локального состояния","## Локальные симптомы","## Lessons learned как ограничения","TASK-2026-0004","TASK-2026-0006","TASK-2026-0007","task_workflow.py","install_skill.py","agents/openai.yaml"],"workflow":["Человекочитаемое описание","knowledge/tasks/registry.md","delivery units"],"install":["AGENTS.md","knowledge/tasks/registry.md","references/upgrade-transition.md"],"metadata":["publish-flow","verification matrix","upgrade-transition","managed-блоком AGENTS.md"],"sdd":["artifacts/stage-1-audit.md","VERIFY-0008-02","VERIFY-0008-04"],"matrix":["stage-1-audit.md","INV-02","INV-04"]}; bad={name:[token for token in tokens if token not in texts[name]] for name,tokens in checks.items()}; bad={k:v for k,v in bad.items() if v}; assert not bad, bad; print("stage1_local_inputs_ok")'
```

### `VERIFY-0008-03`

```bash
rg -n 'Конечная цель `vNext`|операционная система задач|контракт ядра|memory lanes|adapter surfaces|read model / reporting UX|redesign ядра' knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/strategy-roadmap.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/sdd.md
```

### `VERIFY-0008-04`

```bash
python3 -c 'from pathlib import Path; text=Path("knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/stage-1-audit.md").read_text(encoding="utf-8"); rows={line.split("`")[1]: line for line in text.splitlines() if line.startswith("| `")}; expected={"GitHub Spec Kit":["github.com/github/spec-kit","github.github.com/spec-kit","specification layer","feature-spec workflow"],"Claude Code":["docs.anthropic.com/en/docs/claude-code/memory","docs.anthropic.com/en/docs/claude-code/sub-agents","scoped memory","agent runtime"],"Cursor":["docs.cursor.com/en/context/rules","docs.cursor.com/en/context/memories","project rules","IDE/context layer"],"memories.sh":["memories.sh","memories.sh/docs","session","система памяти"],"Память GitHub Copilot / VS Code":["code.visualstudio.com/docs/copilot/agents/memory","docs.github.com/en/copilot/how-tos/use-copilot-agents/copilot-memory","области памяти","вендорская память"],"Devin":["docs.devin.ai/product-guides/knowledge","onboarding","knowledge overlay"],"OpenHands":["docs.openhands.dev/sdk/guides/task-tool-set","docs.all-hands.dev/usage/prompting/microagents-overview","machine-executable subtask flow","orchestration/tooling layer"],"LangChain Deep Agents":["docs.langchain.com/oss/python/deepagents/index","docs.langchain.com/oss/python/deepagents/long-term-memory","backend/policy separation","agent harness"],"Агентные workflows GitHub":["github.github.com/gh-aw","github.github.com/gh-aw/reference/memory","package-слой","execution framework"]}; bad={name:["row_missing"] if name not in rows else [token for token in tokens if token not in rows[name]] for name,tokens in expected.items()}; bad={k:v for k,v in bad.items() if v}; assert "## Открытые вопросы для Этапа 2" in text, "missing_stage2_questions"; assert not bad, bad; print("stage1_source_set_ok")'
```

### `VERIFY-0008-14`

```bash
python3 -c 'from pathlib import Path; files={"closure":Path("knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/review-findings-closure.md"),"task_roadmap":Path("knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/strategy-roadmap.md"),"skill_roadmap":Path("skills-global/task-centric-knowledge/references/roadmap.md")}; texts={k:p.read_text(encoding="utf-8") for k,p in files.items()}; orientirs=["GitHub Spec Kit","Claude Code","Cursor","memories.sh","Память GitHub Copilot / VS Code","Devin","OpenHands","LangChain Deep Agents","Агентные workflows GitHub"]; checks={"closure":["task-local `strategy-roadmap.md` объявляется каноническим стратегическим источником","становится дистрибутивным снимком той же стратегии","приоритет у локальной дорожной карты задачи"],"task_roadmap":["каноническим набором внешних ориентиров","Выбранный путь: redesign ядра без full rewrite",*orientirs],"skill_roadmap":["Этот файл является дистрибутивным снимком той же стратегии","локальный источник истины репозитория","redesign ядра без full rewrite",*orientirs]}; bad={name:[token for token in tokens if token not in texts[name]] for name,tokens in checks.items()}; bad={k:v for k,v in bad.items() if v}; assert not bad, bad; print("roadmap_hierarchy_and_source_set_ok")'
```

### `VERIFY-0008-05`

```bash
rg -n "Фаза 0|Фаза 1|Фаза 2|Фаза 3|Фаза 4|Ворота перехода" knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/strategy-roadmap.md skills-global/task-centric-knowledge/references/roadmap.md
```

### `VERIFY-0008-06`

```bash
rg -n "Не добавлять новые большие capability прямо в текущий helper-монолит|Стоп-критерии|change amplification|не расширять модель дальше вширь" knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/strategy-roadmap.md skills-global/task-centric-knowledge/references/roadmap.md
```

### `VERIFY-0008-07`

```bash
rg -n "status|current-task|task show|doctor deps|migrate cleanup" knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/cli-ux-draft.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/strategy-roadmap.md skills-global/task-centric-knowledge/references/roadmap.md
```

### `VERIFY-0008-08`

```bash
rg -n 'TASK-ID \+ краткое имя \+ человекочитаемое описание|TASK-ID \. краткое имя \. человекочитаемое описание' knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/cli-ux-draft.md
```

### `VERIFY-0008-09`

```bash
rg -n 'обязательные|условно-обязательные|опциональные|not-applicable|core/local mode|publish/integration' knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/cli-ux-draft.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/strategy-roadmap.md
```

### `VERIFY-0008-10`

```bash
rg -n 'plan -> confirm|migrate cleanup plan|migrate cleanup confirm|абсолютные пути|TARGET_COUNT|COUNT' knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/cli-ux-draft.md
```

### `VERIFY-0008-12`

```bash
rg -n 'DDD-карта контекстов|ограниченный контекст|Корень агрегата|Task Core|Read Model / Reporting|Publish Integration|Packaging / Governance' knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/sdd.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/strategy-roadmap.md
```

### `VERIFY-0008-13`

```bash
rg -n 'локальное хранение доказательных артефактов|artifacts/screenshots|artifacts/logs|artifacts/reports|artifacts/migration|доказательные материалы задачи должны жить внутри каталога' knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/sdd.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/strategy-roadmap.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/review-findings-closure.md
```

### `VERIFY-0008-11`

```bash
python3 -m unittest skills-global/task-centric-knowledge/tests/test_task_workflow.py
python3 -c 'from pathlib import Path; import re; task=Path("knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/task.md").read_text(encoding="utf-8"); registry=Path("knowledge/tasks/registry.md").read_text(encoding="utf-8"); summary=re.search(r"\| Человекочитаемое описание \| (.+?) \|", task).group(1).strip(); row=next(line for line in registry.splitlines() if line.startswith("| `TASK-2026-0008` |")); assert f"| {summary} |" in row, (summary, row); print("registry_summary_synced_ok")'
```

### `VERIFY-0008-15`

```bash
rg -n 'Переименование skill-а не требуется|task-centric-knowledge остаётся корректным именем|операционная система задач внутри репозитория' knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/review-findings-closure.md skills-global/task-centric-knowledge/SKILL.md knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/artifacts/strategy-roadmap.md
```

### `VERIFY-0008-OPENAI`

```bash
rg -n "delivery units|publish-flow|verification matrix|доказательных артефактов|upgrade-transition|managed-блоком AGENTS.md" skills-global/task-centric-knowledge/agents/openai.yaml
```

## 3. Остаточный риск и ручной остаток

- Дополнительный ручной остаток для финального sync-этапа отсутствует: содержательные оценки стратегической амбиции, фазовой roadmap и CLI UX закрыты предыдущими audit-gate-ами, а Этап 5 подтверждает только доказательный и синхронизационный контур.

## 4. Правило завершения

- Задача не считается завершённой, пока `strategy-roadmap.md` не содержит явного стратегического решения, целевой архитектуры и фазовой дорожной карты.
- Задача не считается завершённой, пока `cli-ux-draft.md` не фиксирует минимальный операторский контракт для запросов, отчётности и cleanup после миграции.
- Review не заменяет эту матрицу.
- Результаты audit-gates фиксируются отдельно в `artifacts/audit-gates.md`; сама матрица не подменяет запись `pass/fail/manual-residual` по gate-ам.
