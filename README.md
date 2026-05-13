# task-centric-knowledge

Операционная система задач внутри репозитория. Локальный источник истины, маршрутизация между текущей задачей, подзадачей и новой задачей, git-жизненный цикл и publish-контур.

## Назначение

`task-centric-knowledge` организует агентную разработку вокруг понятия **задачи**:

- каждая задача живёт в `knowledge/tasks/<TASK-ID>-<slug>/task.md`;
- `plan.md`, `sdd.md`, verification matrix и артефакты хранятся рядом с задачей;
- навигационный cache ведётся в `knowledge/tasks/registry.md`;
- CLI `task-knowledge` предоставляет установку, отчётность и workflow-помощники.

## Ключевые документы

| Документ | Назначение |
|----------|------------|
| [`SKILL.md`](SKILL.md) | Нормативный документ навыка для агентов |
| [`references/core-model.md`](references/core-model.md) | Каноническая модель Task Core: DDD-карта, агрегаты, статусы |
| [`references/roadmap.md`](references/roadmap.md) | Дорожная карта развития |
| [`references/cli-reference.md`](references/cli-reference.md) | Полный CLI reference: установка, подкоманды, JSON-политика |
| [`references/deployment.md`](references/deployment.md) | Развёртывание и production rollout |
| [`references/task-workflow.md`](references/task-workflow.md) | Workflow-контракт: открытие, ведение, завершение задачи |
| [`references/task-routing.md`](references/task-routing.md) | Маршрутизация: текущая задача / подзадача / новая задача |
| [`references/upgrade-transition.md`](references/upgrade-transition.md) | Безопасное обновление knowledge-системы |
| [`references/consumer-runtime-v1.md`](references/consumer-runtime-v1.md) | Контракт для потребителей, встраивающих runtime subset |
| [`references/adoption.md`](references/adoption.md) | Adoption-паттерны для разных профилей |

## Философия

- **Локальный источник истины**. Вся информация о задаче живёт в её каталоге внутри репозитория. Никакой внешней базы.
- **Одна задача — один план**. Не создавать глобальных дорожных карт поверх задач.
- **Доказательный verify-контур**. Для сложных задач обязателен `sdd.md` и `artifacts/verification-matrix.md`.
- **Модульная архитектура**. Ядро (Task Core) стабильно, publish-адаптеры и профили подключаются как расширения.
- **Безопасное обновление**. Managed-файлы обновляются без потери project data, с явным git-следом перехода.

## Быстрый старт

```bash
# Установка CLI
make install-local

# Проверка окружения
task-knowledge doctor --project-root /abs/project

# Установка knowledge-системы в проект
task-knowledge install apply --project-root /abs/project --force
```

Подробный CLI reference: [`references/cli-reference.md`](references/cli-reference.md).

## Владение репозиторием

Этот репозиторий является каноническим домом `task-centric-knowledge`.
Потребители не должны копировать реализацию в свои `skills-global/`;
ожидаемый интерфейс интеграции — CLI `task-knowledge ... --project-root /abs/project`.

Product history хранится в `knowledge/tasks/` и импортирована из исходного `ai-agents-rules` только для задач, которые описывают развитие самого `task-centric-knowledge`.

## Лицензия

См. [`LICENSE`](LICENSE).
