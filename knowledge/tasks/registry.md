# Реестр задач

Реестр нужен только для навигации.
Источником истины по каждой задаче остаётся файл `knowledge/tasks/<TASK-ID>-<slug>/task.md`.

## Как вести

- одна строка на одну задачу;
- одна строка на одну значимую подзадачу;
- для подзадачи указывать родительский `ID`;
- статус и краткое описание должны совпадать с `task.md`;
- колонка `Ветка` должна совпадать с полем `Ветка` в `task.md`;
- для подзадачи допустимо наследовать ветку родителя, если отдельная ветка не нужна;
- если задача переименована, ссылка на каталог обновляется;
- если задача разбита на подзадачи, декомпозиция отражается через `Parent ID`.

## Таблица

| ID | Parent ID | Статус | Приоритет | Ветка | Каталог | Краткое описание |
|----|-----------|--------|-----------|-------|---------|------------------|
| `TASK-2026-0004` | `—` | `завершена` | `высокий` | `task/task-2026-0004-task-centric-knowledge-git-flow` | `knowledge/tasks/TASK-2026-0004-task-centric-knowledge-git-flow/` | Доработка `task-centric-knowledge` для автоматического git-жизненного цикла задачи и явной маршрутизации задач/подзадач. |
| `TASK-2026-0004.1` | `TASK-2026-0004` | `завершена` | `высокий` | `task/task-2026-0004-task-centric-knowledge-git-flow` | `knowledge/tasks/TASK-2026-0004-task-centric-knowledge-git-flow/subtasks/TASK-2026-0004.1-skill-upgrade-safety/` | Безопасное обновление старой версии task-centric-knowledge на новую без потери task-данных и с явным переходом в git. |
| `TASK-2026-0006` | `—` | `завершена` | `высокий` | `task/task-2026-0006-task-centric-testing-contract` | `knowledge/tasks/TASK-2026-0006-task-centric-testing-contract/` | Тестовый контракт task-centric-knowledge: максимум автоматических проверок и единый итоговый список ручных тестов. |
| `TASK-2026-0008` | `—` | `завершена` | `высокий` | `task/task-2026-0008-task-centric-knowledge-roadmap-vnext` | `knowledge/tasks/TASK-2026-0008-task-centric-knowledge-roadmap-vnext/` | Стратегический пакет vNext для развития `task-centric-knowledge` как операционной системы задач внутри репозитория |
| `TASK-2026-0010` | `—` | `завершена` | `высокий` | `task/task-2026-0010-task-centric-vnext-core-contract` | `knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/` | Нормативный vNext-core contract и DDD-карта для task-centric-knowledge |
| `TASK-2026-0011` | `—` | `завершена` | `высокий` | `task/task-2026-0011-task-centric-vnext-helper-modularization` | `knowledge/tasks/TASK-2026-0011-task-centric-vnext-helper-modularization/` | Модульная декомпозиция helper-контуров task-centric-knowledge без регрессии git и publish-flow |
| `TASK-2026-0012` | `—` | `завершена` | `высокий` | `task/task-2026-0012-task-centric-vnext-doctor-cleanup-governance` | `knowledge/tasks/TASK-2026-0012-task-centric-vnext-doctor-cleanup-governance/` | Governance-слой `doctor-deps` и `migrate-cleanup-plan/confirm` для vNext task-centric-knowledge |
| `TASK-2026-0013` | `—` | `завершена` | `высокий` | `task/task-2026-0013-task-centric-vnext-read-model-reporting` | `knowledge/tasks/TASK-2026-0013-task-centric-vnext-read-model-reporting/` | Операторский read-model слой status / current-task / task show поверх Task Core |
| `TASK-2026-0014` | `—` | `завершена` | `средний` | `task/task-2026-0014-task-centric-vnext-field-validation` | `knowledge/tasks/TASK-2026-0014-task-centric-vnext-field-validation/` | Полевая валидация и пакет внедрения для vNext task-centric-knowledge на внешних репозиториях |
| `TASK-2026-0015` | `—` | `завершена` | `средний` | `task/task-2026-0015-task-centric-knowledge-managed-refresh` | `knowledge/tasks/TASK-2026-0015-task-centric-knowledge-managed-refresh/` | Локальный refresh managed-файлов task-centric-knowledge в текущем репозитории |
| `TASK-2026-0021` | `—` | `завершена` | `высокий` | `main` | `knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/` | Финишировать первую релизную версию task-centric-knowledge, устранить repo-wide knowledge-drift и принять product decision относительно grace-marketplace |
| `TASK-2026-0021.1` | `TASK-2026-0021` | `завершена` | `высокий` | `main` | `knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/subtasks/TASK-2026-0021.1-standalone-release-hardening/` | Довести `task-centric-knowledge` до release-grade standalone состояния без расширения product scope сверх уже подтверждённого ядра. |
| `TASK-2026-0024` | `—` | `завершена` | `высокий` | `main` | `knowledge/tasks/TASK-2026-0024-grace-borrowed-module-core/` | Открыть post-release трек на точечные module-centric заимствования из GRACE без превращения task-centric-knowledge в полный GRACE framework. |
| `TASK-2026-0024.1` | `TASK-2026-0024` | `завершена` | `высокий` | `main` | `knowledge/tasks/TASK-2026-0024-grace-borrowed-module-core/subtasks/TASK-2026-0024.1-grace-borrowings-source-and-refresh-governance/` | Зафиксировать local-first source manifest и безопасный refresh-governance для borrowed-layer из GRACE без жёсткой привязки к одному checkout path. |
| `TASK-2026-0024.2` | `TASK-2026-0024` | `завершена` | `высокий` | `main` | `knowledge/tasks/TASK-2026-0024-grace-borrowed-module-core/subtasks/TASK-2026-0024.2-module-passports-and-registry/` | Ввести managed-root `knowledge/modules/` с модульными паспортами и registry как companion-layer для постоянной инженерной памяти по governed модулям. |
| `TASK-2026-0024.3` | `TASK-2026-0024` | `завершена` | `средний` | `main` | `knowledge/tasks/TASK-2026-0024-grace-borrowed-module-core/subtasks/TASK-2026-0024.3-lightweight-module-dependency-map/` | Добавить лёгкую dependency-модель между governed modules без перехода к full knowledge-graph.xml и полной graph-платформе уровня GRACE. |
| `TASK-2026-0024.4` | `TASK-2026-0024` | `завершена` | `средний` | `main` | `knowledge/tasks/TASK-2026-0024-grace-borrowed-module-core/subtasks/TASK-2026-0024.4-file-local-contracts-for-hotspots/` | Принять ограниченную локальную разметку файлов для governed hot spots: `MODULE_CONTRACT`, `MODULE_MAP`, `CHANGE_SUMMARY` и точечные якоря блоков без repo-wide обязательной разметки. |
| `TASK-2026-0024.5` | `TASK-2026-0024` | `завершена` | `средний` | `main` | `knowledge/tasks/TASK-2026-0024-grace-borrowed-module-core/subtasks/TASK-2026-0024.5-module-verification-catalog/` | Добавить каталог модульной верификации, который переиспользуется task-local verification matrix и фиксирует канонические проверки governed modules. |
| `TASK-2026-0024.6` | `TASK-2026-0024` | `завершена` | `высокий` | `main` | `knowledge/tasks/TASK-2026-0024-grace-borrowed-module-core/subtasks/TASK-2026-0024.6-module-query-read-model/` | Добавить read-only команды `task-knowledge module find/show` и `file show` для навигации по `Module Core` и локальному слою file-local contracts. |
| `TASK-2026-0024.7` | `TASK-2026-0024` | `завершена` | `высокий` | `main` | `knowledge/tasks/TASK-2026-0024-grace-borrowed-module-core/subtasks/TASK-2026-0024.7-legacy-upgrade-and-task-backfill-governance/` | Определить versioned upgrade старых версий task-centric-knowledge и policy compatibility-backfill старых задач без реткона закрытых исторических артефактов. |
| `TASK-2026-0024.7.1` | `TASK-2026-0024.7` | `завершена` | `высокий` | `task/task-2026-0024-grace-borrowed-module-core` | `knowledge/tasks/TASK-2026-0024-grace-borrowed-module-core/subtasks/TASK-2026-0024.7-legacy-upgrade-and-task-backfill-governance/subtasks/TASK-2026-0024.7.1-historical-task-sync-guard/` | Запретить helper-синхронизации переписывать branch и исторические метаданные закрытой задачи при запуске из чужой активной ветки и ограничить sync только безопасным compatibility-обновлением. |
| `TASK-2026-0025` | `—` | `завершена` | `высокий` | `task/task-2026-0025-task-centric-knowledge-local-upgrade` | `knowledge/tasks/TASK-2026-0025-task-centric-knowledge-local-upgrade/` | Обновить managed knowledge-систему этого репозитория до текущей версии skill-а task-centric-knowledge без потери project data. |
| `TASK-2026-0026` | `—` | `завершена` | `высокий` | `main` | `knowledge/tasks/TASK-2026-0026-task-centric-knowledge-standalone-bootstrap/` | Зафиксировать bootstrap нового standalone-репозитория `task-centric-knowledge` после выноса из `ai-agents-rules`. |
| `TASK-2026-0027` | `—` | `на проверке` | `высокий` | `task/task-2026-0027-local-auto-finalize` | `knowledge/tasks/TASK-2026-0027-local-auto-finalize/` | Добавить local auto-finalize helper: безопасный локальный `commit -> merge -> checkout main` или явный stop-report с причинами блокировки. |
