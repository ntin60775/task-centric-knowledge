# План задачи TASK-2026-0024.4

## Правило

Для задачи существует только один файл плана: `plan.md`.

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0024.4` |
| Parent ID | `TASK-2026-0024` |
| Версия плана | `2` |
| Связь с SDD | `не требуется` |
| Дата обновления | `2026-04-21` |

## Цель

Определить узкий borrowed file-local contract layer,
который даст private/local truth для governed hot spots
и останется управляемым по стоимости сопровождения.
File-local layer должен помогать controlled execution:
writer получает точные anchors,
а verifier и failure handoff могут указывать first divergent anchor.
Layer должен использовать syntax-neutral markers,
применимые в том числе к `1С/BSL`.

## Границы

### Входит

- перечень разрешённых markers;
- criteria для hot spots;
- якоря блоков;
- использование anchors в `file show`, execution packet и failure handoff;
- правила размещения markers в языках с разными comment styles;
- связь с `file show`.

### Не входит

- массовая разметка;
- mandatory markup для всего репозитория;
- полный lint-режим GRACE.

## Планируемые изменения

### Код

- новый parser/runtime `scripts/module_core_runtime/file_local_contracts.py`;
- расширение `scripts/module_core_runtime/read_model.py` и `query_cli.py`;
- включение `file-local-policy.md` в installer assets и unified CLI text surface.

### Конфигурация / схема данных / именуемые сущности

- правила `MODULE_CONTRACT`, `MODULE_MAP`, `CHANGE_SUMMARY` и якорей блоков.

### Документация

- управляемый шаблон `knowledge/modules/_templates/file-local-policy.md`;
- обновления `README.md`, `SKILL.md` и `knowledge/modules/README.md`;
- синхронизация task-local карточки и плана под фактическую реализацию.

## Зависимости и границы

### Новые runtime/package зависимости

- `нет`

### Изменения import/module-связей и зависимостей между модулями

- file-local truth должна дополнять module passports, а не дублировать все их поля;
- markers не должны полагаться на один конкретный синтаксис комментариев или docstring-модель.

### Границы, которые должны остаться изолированными

- разметка только для целевых сложных файлов;
- никакой repo-wide обязанности по умолчанию.

### Критический функционал

- локальная инженерная навигация по сложному файлу;
- точные anchors для чтения и ревью;
- переносимый contract для `1С/BSL` и других языков.

### Основной сценарий

- инженер или агент открывает governed file;
- видит file-local contracts и якоря блоков;
- использует `file show` для ориентации.

### Исходный наблюдаемый симптом

- одного только module passport недостаточно для private/local implementation context.

## Риски и зависимости

- слишком широкая политика приведёт к бюрократии;
- слишком узкая политика не даст практической пользы;
- если marker contract окажется завязан на syntax assumptions одного языка, file-local layer не станет универсальным.

## Связь с SDD

- `не требуется`

## Проверки

### Что можно проверить кодом или тестами

- профильный пакет unit/CLI/install-тестов для parser layer,
  слоя read-model,
  единого CLI
  и управляемого installer-контура;
- `git diff --check`
- wrapper локализационной проверки `bash scripts/check-docs-localization.sh`

### Что остаётся на ручную проверку

- `не требуется`

## Шаги

- [x] Определить минимальный набор markers.
- [x] Определить criteria для governed hot spots.
- [x] Описать якоря блоков и связь с `file show`.
- [x] Описать anchor usage для packet guidance и failure handoff.
- [x] Зафиксировать explicit запрет на repo-wide mandatory rollout.
- [x] Зафиксировать syntax-neutral marker policy, пригодную для `1С/BSL`.

## Критерии завершения

- file-local policy реализована warning-first поверх существующего query-layer;
- installer, runtime, CLI и документация используют единый storage contract;
- text/json surface `file show` больше не содержит placeholder-поведение для governed hot spots.
