# SDD по задаче TASK-2026-0012

## Паспорт SDD

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0012` |
| Статус | `завершено` |
| Версия | `2` |
| Дата обновления | `2026-04-13` |

## 1. Проблема и цель

### Проблема

После `TASK-2026-0011` install helper перестал быть монолитом,
но governance-контур install/upgrade всё ещё не имел отдельной runtime-модели
для `doctor-deps` и безопасного `migrate-cleanup-plan/confirm`.

Без этого install/upgrade UX оставался неполным:

- зависимости не различались по классам и blocking layers;
- publish tooling мог выглядеть как поломка всего skill-а;
- cleanup после миграции не имел runtime-allowlist и scope-lock;
- `install_skill.py` рисковал снова разрастись до монолита.

### Цель

Сделать governance-контур, который:

- живёт в отдельном runtime-пакете поверх существующего facade;
- различает классы зависимостей и слои блокировки;
- раскрывает cleanup scope до мутации;
- требует fingerprint-confirm перед удалением;
- не удаляет `project data` и foreign-system контуры автоматически.

## 2. Архитектура и границы

### Целевой runtime-разрез

Новый runtime живёт в пакете `skills-global/task-centric-knowledge/scripts/install_skill_runtime/`.

- `models.py`
  - константы режимов и dependency statuses;
  - `StepResult`, `ExistingSystemReport`, `DependencyCheck`, `CleanupCandidate`, `CleanupPlan`;
  - расчёт `cleanup_scope_fingerprint`.
- `environment.py`
  - `validate_source`, `validate_target`, `detect_managed_block_state`, `detect_existing_system`;
  - `copy_knowledge_files`, `install_agents_block`, `write_migration_suggestion`;
  - существующие `check/install`.
- `doctor.py`
  - каталог зависимостей;
  - определение `git`-контура, remote и host;
  - `doctor_deps`.
- `cleanup.py`
  - discovery cleanup-кандидатов;
  - allowlist v1;
  - раскрытие absolute `TARGETS` и recursive `COUNT`;
  - `migrate_cleanup_plan`, `migrate_cleanup_confirm`.
- `cli.py`
  - разбор аргументов, dispatch и вывод `text/json`.
- `__init__.py`
  - публичный runtime surface и re-export существующих функций/констант.

`scripts/install_skill.py` оставлен тонким facade-entrypoint с bootstrap `sys.path`,
compatibility re-export и вызовом `main(script_path=...)`.

### Публичный transport

Track 3 закреплён внутри `install_skill.py` через `--mode`:

- `check`
- `install`
- `doctor-deps`
- `migrate-cleanup-plan`
- `migrate-cleanup-confirm`

Transport-layer для unified operator CLI сознательно не выбирается в этой задаче.

### Список auto-delete v1

Auto-delete разрешён только для installer-generated артефактов:

- `knowledge/MIGRATION-SUGGESTION.md`, если текущая классификация уже `clean` или `compatible`;
- `AGENTS.task-centric-knowledge.<profile>.md`, если managed-блок knowledge-системы уже materialized в `AGENTS.md`.

В `keep` обязательно остаются:

- `AGENTS.md`;
- `knowledge/tasks/registry.md`;
- существующие managed knowledge-файлы;
- каталоги задач `knowledge/tasks/TASK-*`;
- migration note, если классификация всё ещё требует её сохранения.

В `manual_review` попадают только внешние и legacy-контуры из `FOREIGN_SYSTEM_INDICATORS`.
Туда же уходит любой allowlist-путь, если вместо обычного файла найден symlink, каталог или другой неожиданный тип объекта.

## 3. Полный invariant set

- `INV-0012-01`: зависимости разделяются на `required`, `conditional`, `optional`, `not-applicable`;
- `INV-0012-02`: `doctor-deps` различает блокеры `core/local mode` и `publish/integration`;
- `INV-0012-03`: cleanup невозможен без шага `migrate-cleanup-plan`;
- `INV-0012-04`: `migrate-cleanup-plan` раскрывает абсолютные пути, `TARGETS`, `TARGET_COUNT`, `COUNT`, `plan_fingerprint` и confirm-команду;
- `INV-0012-05`: `migrate-cleanup-confirm` не может расширить scope относительно ранее показанного плана и требует `--confirm-fingerprint` и `--yes`;
- `INV-0012-06`: governance не удаляет `project data` молча и не включает foreign-system cleanup в auto-delete allowlist.

## 4. Новые интерфейсы и данные

### CLI-контракт

| Режим | Назначение | Ключевые поля |
|-------|------------|---------------|
| `doctor-deps` | Диагностика install/upgrade зависимостей | `dependencies[]`, `dependency_class`, `status`, `blocking_layer`, `hint` |
| `migrate-cleanup-plan` | Dry-run cleanup после миграции | `safe_delete`, `keep`, `manual_review`, `targets`, `target_count`, `count`, `plan_fingerprint`, `confirm_command` |
| `migrate-cleanup-confirm` | Подтверждённое применение cleanup-plan | те же scope-поля + повторная валидация fingerprint |

### Ограничения payload

- `check/install` сохраняют прежний shape payload и дополняются только полем `mode`;
- `doctor-deps` не зависит от network-запросов;
- fingerprint считается от `TARGETS`, полного раскрытого delete-scope, `TARGET_COUNT`, `COUNT` и confirm-template.

## 5. Этапы реализации и проверки

### Этап 1. Runtime split

- вынести install/governance logic в `install_skill_runtime/`;
- оставить `install_skill.py` тонким facade;
- Verify:
  `python3 -m unittest skills-global/task-centric-knowledge/tests/test_install_skill_architecture.py`

### Этап 2. Diagnostics contract

- зафиксировать dependency classes и status model;
- различить `core/local mode` и `publish/integration`;
- Verify:
  `python3 -m unittest skills-global/task-centric-knowledge/tests/test_install_skill_governance.py`
  `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules --mode doctor-deps --format json`

### Этап 3. Cleanup planning and confirm

- реализовать allowlist v1;
- реализовать disclosure `TARGETS`, `TARGET_COUNT`, `COUNT`;
- реализовать `plan_fingerprint` и confirm-flow;
- Verify:
  `python3 -m unittest skills-global/task-centric-knowledge/tests/test_install_skill_governance.py`
  `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules --mode migrate-cleanup-plan --format json`

### Этап 4. Regression and docs

- подтвердить, что `check/install` не регрессировали;
- синхронизировать `SKILL.md`, deployment и upgrade docs;
- Verify:
  `python3 -m unittest skills-global/task-centric-knowledge/tests/test_install_skill.py`
  `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'`
  `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --help`
  `git diff --check`

## 6. Критерии приёмки

1. Install/governance runtime живёт в отдельном пакете `scripts/install_skill_runtime/`.
2. `install_skill.py` остаётся тонким compatibility facade.
3. `doctor-deps` не путает publish-tooling проблемы с core/local blockерами.
4. `migrate-cleanup-plan` раскрывает детерминированный cleanup scope.
5. `migrate-cleanup-confirm` останавливается при любом scope drift.
6. `project data` и foreign-system контуры не попадают в auto-delete.
7. Полный invariant set покрыт тестами и smoke-проверками.

## 7. Стоп-критерии

1. Cleanup требует скрытого удаления или недетерминированного подсчёта.
2. Publish/integration tooling переводит `doctor-deps` в красный `core/local mode`.
3. Facade `install_skill.py` снова втягивает business logic.
4. Allowlist v1 начинает захватывать `registry.md`, task-каталоги или foreign-system контуры.
