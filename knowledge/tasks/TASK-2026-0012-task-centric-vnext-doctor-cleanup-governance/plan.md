# План задачи TASK-2026-0012

## Паспорт плана

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0012` |
| Parent ID | `—` |
| Версия плана | `2` |
| Связь с SDD | `sdd.md`, `artifacts/verification-matrix.md` |
| Дата обновления | `2026-04-13` |

## Цель

Построить governance-контур `doctor-deps` и `migrate-cleanup-plan/confirm` как отдельный safety-oriented слой `vNext`
без регрессии существующего `check/install` поведения.

## Границы

### Входит

- runtime-разрез install/governance helper-а;
- dependency catalog и blocking layers;
- cleanup allowlist, disclosure и scope-lock;
- CLI-режимы `doctor-deps`, `migrate-cleanup-plan`, `migrate-cleanup-confirm`;
- тесты и документация по install/upgrade governance.

### Не входит

- unified transport-layer для `status/current-task/task show`;
- расширение auto-delete beyond installer-generated artifacts;
- publish-host parity и memory-layer.

## Планируемые изменения

### Код

- создать пакет `scripts/install_skill_runtime/` с модулями `models.py`, `environment.py`, `doctor.py`, `cleanup.py`, `cli.py`, `__init__.py`;
- сократить `scripts/install_skill.py` до bootstrap, re-export и `main(script_path=...)`;
- перенести существующие `check/install` операции в `environment.py`;
- реализовать `doctor-deps` с dependency classes, status model и blocking layers;
- реализовать `migrate-cleanup-plan/confirm` с allowlist v1, абсолютными путями, `TARGETS`, `TARGET_COUNT`, `COUNT`, `plan_fingerprint` и confirm-flow.

### Тесты

- сохранить regression `test_install_skill.py`;
- добавить `test_install_skill_governance.py` для `doctor-deps` и cleanup-flow;
- добавить `test_install_skill_architecture.py` для import-graph и тонкого facade;
- прогнать полный discover-набор skill-а.

### Документация

- синхронизировать `SKILL.md`, `references/deployment.md`, `references/upgrade-transition.md`;
- перевести task-local артефакты в финальное состояние.

## Риски и зависимости

- без явного allowlist cleanup легко превратить в скрытое удаление project data;
- fingerprint-confirm flow нельзя строить на недетерминированном scope;
- install facade нельзя снова разрастить до монолита после `TASK-2026-0011`.

## Проверки

### Что можно проверить кодом или тестами

- `python3 -m unittest skills-global/task-centric-knowledge/tests/test_install_skill.py`;
- `python3 -m unittest skills-global/task-centric-knowledge/tests/test_install_skill_governance.py`;
- `python3 -m unittest skills-global/task-centric-knowledge/tests/test_install_skill_architecture.py`;
- `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'`;
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules --mode doctor-deps --format json`;
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules --mode migrate-cleanup-plan --format json`;
- `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --help`;
- `git diff --check`.

### Что остаётся на ручную проверку

- `не требуется`

## Шаги

- [x] Синхронизировать task-контекст и отдельную task-ветку.
- [x] Вынести install/governance runtime в отдельный пакет.
- [x] Добавить `doctor-deps`.
- [x] Добавить `migrate-cleanup-plan`.
- [x] Добавить `migrate-cleanup-confirm`.
- [x] Закрепить allowlist v1 и scope-lock через fingerprint.
- [x] Добавить governance и architecture тесты.
- [x] Синхронизировать skill docs и task-local артефакты.
- [x] Прогнать verify-команды и локализационный guard.

## Критерии завершения

- install/governance helper декомпозирован на осмысленные runtime-модули;
- `check/install` сохраняют поведение;
- `doctor-deps` и `migrate-cleanup-plan/confirm` реализованы и проверяемы;
- cleanup-governance не допускает silent deletion и ограничен allowlist v1;
- весь invariant set `TASK-2026-0012` переведён в `covered`.
