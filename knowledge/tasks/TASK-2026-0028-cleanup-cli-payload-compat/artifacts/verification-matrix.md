# Verification matrix по задаче TASK-2026-0028

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0028` |
| Версия | `1` |
| Дата обновления | `2026-04-21` |

## Матрица

| Инвариант | Сценарий нарушения | Проверка / команда | Статус |
|-----------|--------------------|--------------------|--------|
| `INV-01` | `print_text_report()` безусловно читает отсутствующие поля cleanup-payload и падает с `KeyError` | `python3 /home/prog7/.agents/skills/task-centric-knowledge/scripts/install_skill.py --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-knowledge-agent-runtime --mode migrate-cleanup-plan` | `passed` |
| `INV-02` | no-op cleanup считается ошибкой вместо валидного результата | `python3 scripts/install_skill.py --project-root /home/prog7/РабочееПространство/projects/PetProjects/task-knowledge-agent-runtime --mode migrate-cleanup-plan` | `passed` |
| `INV-03` | repo snapshot и installed copy расходятся по formatter-логике | `git diff --no-index -- scripts/install_skill_runtime/cli.py /home/prog7/.agents/skills/task-centric-knowledge/scripts/install_skill_runtime/cli.py` | `passed` |
