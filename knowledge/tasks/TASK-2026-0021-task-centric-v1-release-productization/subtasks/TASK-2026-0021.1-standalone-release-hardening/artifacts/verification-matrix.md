# Матрица проверки — TASK-2026-0021.1

## Контекст

- Задача: `TASK-2026-0021.1`
- Родитель: `TASK-2026-0021`
- SDD: `../sdd.md`

## Матрица

| Invariant ID | Описание | Источник истины | Где может сломаться |
|--------------|----------|-----------------|---------------------|
| `INV-0021.1-01` | У skill-а есть один короткий и явный дистрибутивный core-contract. | `sdd.md`, `skills-global/task-centric-knowledge/references/core-model.md`, `knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md` | В дистрибутиве останется только task-local ссылка или появится несколько конкурирующих нормативных файлов. |
| `INV-0021.1-02` | Reference-слой не трактует уже реализованные release-контуры как чисто будущие. | `sdd.md`, `skills-global/task-centric-knowledge/references/roadmap.md`, `SKILL.md` | Roadmap и docs будут спорить с фактическим состоянием runtime и закрытых задач `TASK-2026-0010 ... TASK-2026-0014`. |
| `INV-0021.1-03` | Контур `install/check/doctor/query/workflow` остаётся подтверждённым тестами и локальными CLI-проверками. | `sdd.md`, `skills-global/task-centric-knowledge/tests`, `scripts/*.py` | Документы будут обещать стабильность без автопроверочного подтверждения. |
| `INV-0021.1-04` | Hardening не открывает новый product layer и не ломает границы ядра. | `sdd.md`, `SKILL.md`, `references/core-model.md`, `references/roadmap.md` | Новый snapshot начнёт конкурировать с ядром или расширять scope в memory/publish/operator UX. |

## Покрытие

| Invariant ID | Сценарий нарушения | Проверка | Статус |
|--------------|--------------------|----------|--------|
| `INV-0021.1-01` | В дистрибутиве нет `core-model.md` или он не трассируется к каноническому core contract. | `rg -n "core-model.md|vnext-core-contract|источник истины|Task Core" skills-global/task-centric-knowledge/SKILL.md skills-global/task-centric-knowledge/references/core-model.md skills-global/task-centric-knowledge/references/roadmap.md skills-global/task-centric-knowledge/references/deployment.md skills-global/task-centric-knowledge/references/task-workflow.md knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md` | `covered` |
| `INV-0021.1-02` | Roadmap продолжает описывать как pending уже реализованные tracks `0010 ... 0014` без разведения “сделано” и “следующая волна”. | `rg -n "TASK-2026-0010|TASK-2026-0011|TASK-2026-0012|TASK-2026-0013|TASK-2026-0014|реализ|заверш|completed|next wave" skills-global/task-centric-knowledge/references/roadmap.md skills-global/task-centric-knowledge/SKILL.md` | `covered` |
| `INV-0021.1-03` | Release-контур описан, но тесты или CLI-проверки его не подтверждают. | `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'` | `covered` |
| `INV-0021.1-03` | `status/current-task/task show`, `check` или `doctor-deps` перестали работать на фактических репозиториях. | `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main status --format json` | `covered` |
| `INV-0021.1-03` | `status/current-task/task show`, `check` или `doctor-deps` перестали работать на фактических репозиториях. | `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main current-task --format json` | `covered` |
| `INV-0021.1-03` | `status/current-task/task show`, `check` или `doctor-deps` перестали работать на фактических репозиториях. | `python3 skills-global/task-centric-knowledge/scripts/task_query.py --project-root /home/prog7/MyWorkspace/30-Knowledge/AI/ai-agents-rules-main task show TASK-2026-0021.1 --format json` | `covered` |
| `INV-0021.1-03` | `check` или `doctor-deps` не подтверждают пригодность skill-а для `Druzhina`. | `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/druzhina --mode check` | `covered` |
| `INV-0021.1-03` | `check` или `doctor-deps` не подтверждают пригодность skill-а для `Druzhina`. | `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/MyWorkspace/20-Personal/PetProjects/Active/druzhina --mode doctor-deps` | `covered` |
| `INV-0021.1-04` | Правки создают новый конкурирующий нормативный слой или размывают границы ядра. | `rg -n "Task Core|Read Model / Reporting|Publish Integration|Memory|Packaging / Governance|Profiles|не меняет|не конкурирует|не расширяет scope" skills-global/task-centric-knowledge/references/core-model.md skills-global/task-centric-knowledge/references/roadmap.md` | `covered` |
| `INV-0021.1-01` | Изменённые Markdown-файлы нарушают локализационный guard. | `scripts/check-docs-localization.sh knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/task.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/subtasks/TASK-2026-0021.1-standalone-release-hardening/task.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/subtasks/TASK-2026-0021.1-standalone-release-hardening/plan.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/subtasks/TASK-2026-0021.1-standalone-release-hardening/sdd.md knowledge/tasks/TASK-2026-0021-task-centric-v1-release-productization/subtasks/TASK-2026-0021.1-standalone-release-hardening/artifacts/verification-matrix.md skills-global/task-centric-knowledge/SKILL.md skills-global/task-centric-knowledge/references/core-model.md skills-global/task-centric-knowledge/references/roadmap.md skills-global/task-centric-knowledge/references/deployment.md skills-global/task-centric-knowledge/references/task-workflow.md knowledge/tasks/registry.md` | `covered` |
