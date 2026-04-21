# SDD по задаче TASK-2026-0021.1

## Паспорт SDD

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0021.1` |
| Статус | `завершено` |
| Версия | `1` |
| Дата обновления | `2026-04-14` |

## 0. Инварианты и verification matrix

### Полный invariant set

- `INV-0021.1-01`: у дистрибутива `task-centric-knowledge` есть один короткий и явный release-grade core-contract внутри `references/`, трассируемый к task-local `vnext-core-contract`.
- `INV-0021.1-02`: `SKILL.md` и reference-документы не описывают как будущие те release-critical capability, которые уже реализованы и подтверждены tracks `TASK-2026-0010 ... TASK-2026-0014`.
- `INV-0021.1-03`: release-critical контур `install/check/doctor/query/workflow` остаётся воспроизводимым и подтверждается тестами и локальными CLI-проверками.
- `INV-0021.1-04`: hardening не расширяет product scope и не открывает новый конкурирующий нормативный слой поверх уже существующей модели ядра.

### Связанные артефакты проверки

- `artifacts/verification-matrix.md`

## 1. Проблема и цель

### Проблема

`task-centric-knowledge` фактически уже имеет сильный release-ready контур:
core contract, модульный runtime, `doctor-deps`, `migrate-cleanup-plan/confirm`, `status/current-task/task show`,
field validation и adoption package уже существуют.
Но дистрибутивный слой не везде подаёт это как завершённую стабильную форму:
часть reference-файлов описывает capability как будущие tracks,
а core-contract остаётся канонически закреплённым только в task-local артефакте `TASK-2026-0010`.

### Цель

Сделать текущую standalone линию skill-а короткой, объяснимой и надёжной:
вынести release-grade snapshot ядра в дистрибутивный reference-слой,
синхронизировать `SKILL.md` и references с фактическим состоянием,
и подтвердить runtime-контур проверками без расширения product scope.

## 2. Архитектура и границы

- task-local `knowledge/tasks/TASK-2026-0010-.../artifacts/vnext-core-contract.md` остаётся историческим первичным источником решения;
- новый `skills-global/task-centric-knowledge/references/core-model.md` становится дистрибутивным snapshot этого контракта;
- `SKILL.md`, `references/roadmap.md`, `references/deployment.md`, `references/task-workflow.md` должны ссылаться на `references/core-model.md` как на операторский первичный источник по модели ядра;
- runtime/tests усиливаются только там, где это нужно для подтверждения release-контуров;
- host-specific, memory-layer и новая product surface не входят в задачу.

### Допустимые и недопустимые связи

- допустимо: `references/core-model.md` <- snapshot/адаптация от task-local `vnext-core-contract`;
- допустимо: reference-документы ссылаются на `core-model.md` как на канонический дистрибутивный contract;
- допустимо: тесты проверяют трассировку и отсутствие release-drift;
- недопустимо: roadmap снова делает `status/current-task/task show` или `doctor/cleanup` чисто будущими track-ами без пометки, что они уже реализованы;
- недопустимо: новый reference-документ начинает конкурировать с task-local contract по смыслу или истории решения.

### Новые зависимости и их обоснование

- `нет`

### Наблюдаемые сигналы и диагностические маркеры

- отсутствие `references/core-model.md`;
- формулировки roadmap/references, трактующие уже существующие capability как чисто будущие;
- падение `unittest` или локальных CLI-проверок `status/current-task/task show`, `check`, `doctor-deps`.

## 3. Изменения данных / схемы / metadata

- добавляется новый дистрибутивный документ `skills-global/task-centric-knowledge/references/core-model.md`;
- обновляются task-local metadata подзадачи и родителя;
- возможны точечные изменения тестовых файлов skill-а.

## 4. Новые сущности и интерфейсы

| Сущность | Тип | Назначение |
|----------|-----|------------|
| `references/core-model.md` | Markdown-документ | Канонический дистрибутивный snapshot модели ядра `task-centric-knowledge` |

Новых CLI-команд, пакетов и runtime-сущностей по умолчанию не добавляется.

## 5. Изменения в существующих компонентах

| Компонент | Что меняется | Ожидаемый результат |
|-----------|--------------|---------------------|
| `skills-global/task-centric-knowledge/SKILL.md` | Явная ссылка на `references/core-model.md` и release-grade форму skill-а | Оператору проще понять опорный contract и текущую границу продукта |
| `skills-global/task-centric-knowledge/references/roadmap.md` | Удаление drift между “уже реализовано” и “следующая волна” | Дорожная карта перестаёт спорить с фактическим состоянием release-контуров |
| `skills-global/task-centric-knowledge/references/deployment.md` | Привязка install/check/doctor/cleanup к core-model | Deployment UX описывает тот же продукт, что реально существует |
| `skills-global/task-centric-knowledge/references/task-workflow.md` | Привязка workflow/query к core-model | Operator CLI не выглядит отдельным незафиксированным слоем |
| `skills-global/task-centric-knowledge/tests/*` | Дополнительный hardening там, где надо закрепить release-contract | Release-risk снижается не только документами, но и автопроверками |

## 6. Этапы реализации и проверки

### Этап 1: Contract Freeze

- Сформировать release-hardening invariant set.
- Выпустить `references/core-model.md` как дистрибутивный snapshot `Task Core`.
- Зафиксировать трассировку от `SKILL.md` и references к новому contract.
- Verify: `rg -n "core-model.md|Task Core|источник истины|delivery units|plan -> confirm" skills-global/task-centric-knowledge/SKILL.md skills-global/task-centric-knowledge/references/core-model.md skills-global/task-centric-knowledge/references/roadmap.md skills-global/task-centric-knowledge/references/deployment.md skills-global/task-centric-knowledge/references/task-workflow.md`
- Audit: `IMPLEMENTATION_AUDIT`

### Этап 2: Release Drift Closure

- Синхронизировать roadmap и reference-слой с уже реализованными tracks `TASK-2026-0010 ... TASK-2026-0014`.
- Не допустить конкуренции между task-local contract и дистрибутивным snapshot.
- Verify: `rg -n "TASK-2026-0010|TASK-2026-0011|TASK-2026-0012|TASK-2026-0013|TASK-2026-0014|already|реализ|completed|заверш" skills-global/task-centric-knowledge/references/roadmap.md`
- Audit: `IMPLEMENTATION_AUDIT`

### Этап 3: Runtime Confidence

- Усилить тесты или точечно поправить runtime там, где это нужно для release-grade гарантий.
- Не менять product surface и не вводить новые capability.
- Verify: `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'`
- Audit: `IMPLEMENTATION_AUDIT`

### Финальный этап: Интеграция

- Прогнать локальные query/install проверки по текущему репозиторию и по `Druzhina`.
- Прогнать localization guard для всех изменённых Markdown-файлов.
- Синхронизировать task-local выводы подзадачи и родителя.
- Verify: `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main status --format json`
- Verify: `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main current-task --format json`
- Verify: `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main task show TASK-2026-0021.1 --format json`
- Verify: `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/druzhina --mode check`
- Verify: `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/druzhina --mode doctor-deps`
- Verify: `git diff --check`
- Verify: `scripts/check-docs-localization.sh <изменённые-md-файлы>`
- Audit: `INTEGRATION_AUDIT`

## 7. Критерии приёмки

1. В дистрибутиве skill-а есть один явный `references/core-model.md`, на который ссылаются `SKILL.md` и reference-документы.
2. Reference-слой не оставляет впечатление, что core contract, `doctor/cleanup` и `status/current-task/task show` ещё только предстоит реализовать.
3. Полный тестовый прогон skill-а проходит без регрессии.
4. Локальные CLI-проверки по текущему репозиторию и `Druzhina` подтверждают рабочий release-контур.
5. Hardening не добавляет новые capability вне согласованного release-scope.

## 8. Стоп-критерии

1. Выясняется, что для release-контуров нужен новый крупный runtime-layer, а не точечный hardening.
2. Дистрибутивный `core-model.md` начинает спорить с task-local `vnext-core-contract` по смыслу или ownership.
3. Runtime после правок требует массового переписывания helper-контуров, а не точечного hardening.
