# Карточка задачи TASK-2026-0037

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0037` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0037` |
| Технический ключ для новых именуемых сущностей | `global-skill-install-contract` |
| Краткое имя | `global-skill-install-contract` |
| Человекочитаемое описание | Закрепить полную и проверяемую глобальную установку навыка `task-centric-knowledge` в live-copy и CLI layer. |
| Статус | `завершена` |
| Приоритет | `высокий` |
| Ответственный | `Codex` |
| Ветка | `main` |
| Требуется SDD | `да` |
| Статус SDD | `готово` |
| Ссылка на SDD | `sdd.md` |
| Дата создания | `2026-04-28` |
| Дата обновления | `2026-04-28` |

## Цель

Сделать глобальную установку навыка полной, воспроизводимой и проверяемой: live-копия в `~/.agents/skills/task-centric-knowledge` и пользовательский CLI layer должны обновляться одной штатной процедурой и доказываться прямыми проверками.

## Границы

### Входит

- Source-controlled команда или helper для глобальной установки live-копии навыка.
- Явный manifest/sync scope для live-copy subset.
- Verify-gates для live-копии, user-facing CLI и расхождений между ними.
- Документация с разделением поверхностей `source repo`, `live skill copy`, `user-site CLI layer`, `target project knowledge`.
- Regression-тесты на отсутствие `assets/knowledge/**`, stale/mismatch и полноту deploy scope.

### Не входит

- Изменение семантики `task-knowledge install apply` для целевых проектов.
- Сетевой publish, PR/MR или изменение remote-настроек.
- Удаление live-копии или destructive cleanup без отдельного delete-gate.

## Контекст

- источник постановки: пользовательское ожидание, что глобальная установка навыка выполняется полностью и без ошибок.
- связанная бизнес-область: глобальная live-установка Codex skill-а.
- ограничения и зависимости: live-copy находится вне git checkout, но обновляется из standalone source repo.
- исходный наблюдаемый симптом / лог-маркер: live-copy могла быть неполной, а CLI продолжал работать из source repo; конкретный симптом — отсутствие `assets/knowledge/**` в `/home/prog7/.agents/skills/task-centric-knowledge`.
- основной контекст сессии: новая задача.

## Затронутые области

| Область | Что меняется |
|---------|--------------|
| Код / сервисы | Добавляется install/verify helper и Makefile target для глобальной установки навыка. |
| Конфигурация / схема данных / именуемые сущности | Добавляется явный live-copy manifest/scope без новых runtime-зависимостей. |
| Интерфейсы / формы / страницы | Не меняются. |
| Интеграции / обмены | Синхронизация source repo -> `~/.agents/skills/task-centric-knowledge` и user-site CLI wrapper. |
| Документация | README/SKILL/deployment docs уточняют различие install-поверхностей и full global install flow. |

## Связанные материалы

- основной каталог задачи: `knowledge/tasks/TASK-2026-0037-global-skill-install-contract/`
- файл плана: `plan.md`
- файл SDD: `sdd.md`
- файл verification matrix: `artifacts/verification-matrix.md`
- канонический нормативный contract: `README.md`, `SKILL.md`, `references/deployment.md`, новый helper global install.
- пользовательские материалы: ревью процедуры деплоя со спецами в текущей сессии.
- связанные коммиты / PR / ветки: `task/task-2026-0037-global-skill-install-contract`
- связанные операции в `knowledge/operations/`, если есть: `—`

## Контур публикации

| Unit ID | Назначение | Head | Base | Host | Тип публикации | Статус | URL | Merge commit | Cleanup |
|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|
| `—` | — | `—` | `—` | `none` | `none` | `planned` | `—` | `—` | `не требуется` |

## Текущий этап

Локальный finalize выполнен: task-ветка влита в base-ветку, рабочий контекст переведён на base-ветку, `push` остаётся отдельным шагом.
## Стратегия проверки

### Покрывается кодом или тестами

- `python3 -m unittest discover -s tests -v`
- `python3 -m compileall -q scripts tests`
- `bash scripts/check-docs-localization.sh`
- `git diff --check`
- direct-live smoke после установки: `python3 /home/prog7/.agents/skills/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --mode check --format json`
- smoke пользовательского CLI: `task-knowledge --json doctor --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-centric-knowledge --source-root /home/prog7/.agents/skills/task-centric-knowledge`

### Остаётся на ручную проверку

- Проверить в новой Codex-сессии, что skill routing видит обновлённую live-копию после перезапуска host-а, если host кеширует список skills.

## Критерии готовности

- Глобальная установка запускается штатной командой из source repo.
- Команда не требует сети и не пишет за пределы ожидаемых user-local путей.
- Live-copy содержит все обязательные deploy assets, включая `assets/knowledge/**`.
- User-site CLI layer обновлён и проверен.
- Regression-тесты покрывают missing/stale live-copy class.
- Документация явно разделяет все install-поверхности.

## Итоговый список ручных проверок

- Проверить в новой Codex-сессии, что skill routing видит обновлённую live-копию после перезапуска host-а, если host кеширует список skills.

## Итог

Добавлен source-controlled контур `make install-global-dry-run` -> `make install-global` -> `make verify-global-install`.
Live-copy обновлена в `/home/prog7/.agents/skills/task-centric-knowledge`, CLI layer связан с этой live-copy, `assets/knowledge/**` и wrapper/`.pth` проверяются regression-тестами и verify mode.
