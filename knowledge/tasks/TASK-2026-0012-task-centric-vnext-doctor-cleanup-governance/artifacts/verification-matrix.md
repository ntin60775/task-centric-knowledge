# Матрица проверки по задаче TASK-2026-0012

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0012` |
| Связанный SDD | `../sdd.md` |
| Версия | `2` |
| Дата обновления | `2026-04-13` |

## Канонические инварианты

| Invariant ID | Описание | План проверки | Статус |
|--------------|----------|---------------|--------|
| `INV-0012-01` | Dependency classes разделены корректно | `python3 -m unittest skills-global/task-centric-knowledge/tests/test_install_skill_governance.py` | `covered` |
| `INV-0012-02` | `doctor-deps` различает blocking layers | `python3 -m unittest skills-global/task-centric-knowledge/tests/test_install_skill_governance.py`, `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules --mode doctor-deps --format json` | `covered` |
| `INV-0012-03` | Cleanup невозможен без `migrate-cleanup-plan` | `python3 -m unittest skills-global/task-centric-knowledge/tests/test_install_skill_governance.py` | `covered` |
| `INV-0012-04` | `migrate-cleanup-plan` раскрывает абсолютные пути и счётчики scope | `python3 -m unittest skills-global/task-centric-knowledge/tests/test_install_skill_governance.py`, `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules --mode migrate-cleanup-plan --format json` | `covered` |
| `INV-0012-05` | `migrate-cleanup-confirm` не расширяет scope | `python3 -m unittest skills-global/task-centric-knowledge/tests/test_install_skill_governance.py` | `covered` |
| `INV-0012-06` | Governance не удаляет project data молча | `python3 -m unittest discover -s skills-global/task-centric-knowledge/tests -p 'test_*.py'`, `python3 skills-global/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/work/AI/ai-agents-rules --mode migrate-cleanup-plan --format json` | `covered` |

## Правило завершения

- Задача не считается завершённой, пока все инварианты не переведены в `covered` или явно не маркированы как ручной остаток.
- Review не заменяет эту матрицу.
