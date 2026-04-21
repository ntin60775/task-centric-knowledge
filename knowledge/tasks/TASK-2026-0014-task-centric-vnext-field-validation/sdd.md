# SDD по задаче TASK-2026-0014

## Паспорт SDD

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0014` |
| Статус | `завершено` |
| Версия | `2` |
| Дата обновления | `2026-04-13` |

## 1. Проблема и цель

### Проблема

Даже полностью собранный `vNext` останется локальной конструкцией,
если не проверить его на внешних репозиториях и не зафиксировать friction installation, migration и operator UX
на разных классах knowledge-сред.

### Цель

Провести field validation, которая:

- проверяет `vNext` вне текущего репозитория на трёх классах сред;
- фиксирует reproducible adoption package;
- собирает журнал friction и expected behavior;
- возвращает в roadmap только подтверждённые улучшения.

## 2. Архитектура и границы

Field validation не меняет `Task Core`.
Она проверяет продуктовую форму уже реализованных tracks на изолированных reference environments.

Минимальные компоненты:

- набор reference environments;
- quickstart и adoption package;
- notes по миграции;
- friction log;
- acceptance summary по каждой среде.

### Матрица сред валидации

| Класс среды | Носитель | Baseline | Профиль | Назначение |
|-------------|----------|----------|---------|------------|
| `clean` | `ui-ux-pro-max-skill` | `main@b7e3af8` | `generic` | Чистая установка, snippet-flow при отсутствии `AGENTS.md`, bootstrap первой задачи |
| `mixed_system` | `druzhina` | `main@7ff5c62` | `generic` | Миграционная установка, `MIGRATION-SUGGESTION.md`, `manual_review` и zero-target cleanup-plan |
| `compatible` | `ERP` | `main@65d4934cc` | `1c` | Upgrade `--force`, сохранение `registry.md` как project data, allowlist cleanup-plan |

### Ограничения execution-среды

- validation проводится только на изолированных копиях, не на живых рабочих деревьях;
- для bulky `1c`-репозитория governance/adoption validation допускает sparse-checkout `AGENTS.md + knowledge/**`,
  потому что полный продуктовый payload не нужен для install/upgrade/read-model сценариев;
- cleanup ограничивается `migrate-cleanup-plan`; delete-команды в рамках этой задачи не выполняются.

## 3. Начальный invariant set

- `INV-0014-01`: validation покрывает `clean`, `mixed_system` и `compatible` классы сред;
- `INV-0014-02`: adoption package воспроизводим без неявных локальных предпосылок;
- `INV-0014-03`: friction log отделяет expected behavior, documentation fixes и кандидаты в roadmap;
- `INV-0014-04`: roadmap пополняется только по подтверждённым сигналам field validation;
- `INV-0014-05`: field validation не расширяет product scope спекулятивно и не выполняет destructive cleanup.

## 4. Этапы реализации и проверки

### Этап 1. Select environments

- выбран validation-root `/home/prog7/.codex/memories/task-2026-0014-validation-v2/`;
- подтверждены baseline-носители и классы сред;
- оформлен `artifacts/reference-environments.md`.

### Этап 2. Adoption package

- подготовлены `artifacts/adoption-package.md` и публичный `references/adoption.md`;
- clean-install quickstart проверен на `ui-ux-pro-max-skill`;
- прямой bootstrap `task_workflow --create-branch` на dirty tree зафиксирован как friction,
  валидированный обход описан публично.

### Этап 3. Feedback loop

- собран `artifacts/friction-log.md`;
- заполнен `artifacts/acceptance-summary.md`;
- в roadmap возвращены только сигналы clean-bootstrap, bulky-`1c` validation pattern и expected ambiguity semantics на shared `main`.

## 5. Критерии приёмки

1. Есть репрезентативный набор validation environments по трём классам сред.
2. Adoption package воспроизводим и синхронизирован в публичных docs.
3. Friction log структурирован и пригоден для product decisions.
4. Roadmap обновлена только подтверждённой field feedback.

## 6. Стоп-критерии

1. Validation проводится только на одном искусственно упрощённом репозитории и не покрывает разные классы сред.
2. Adoption package требует неявных шагов, которые проявились в полевых прогонах, но не попали в docs.
3. В roadmap возвращаются неподтверждённые идеи вместо фактических сигналов.
4. Field validation начинает выполнять destructive cleanup или runtime-расширения вне её границ.
