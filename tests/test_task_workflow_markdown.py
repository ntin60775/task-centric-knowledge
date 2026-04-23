from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from task_workflow_runtime.models import DeliveryUnit
from task_workflow_runtime.task_markdown import (
    parse_delivery_units,
    task_summary_from_fields,
    update_task_file_with_delivery_units,
)


def make_task_file(root: Path) -> Path:
    task_file = root / "task.md"
    task_file.write_text(
        """# Карточка задачи TASK-2026-0001

## Паспорт

| Поле | Значение |
|------|----------|
| ID задачи | `TASK-2026-0001` |
| Parent ID | `—` |
| Уровень вложенности | `0` |
| Ключ в путях | `TASK-2026-0001` |
| Технический ключ для новых именуемых сущностей | `—` |
| Краткое имя | `demo` |
| Человекочитаемое описание | `Демо summary` |
| Статус | `в работе` |
| Приоритет | `средний` |
| Ответственный | `Codex` |
| Ветка | `не создана` |
| Требуется SDD | `нет` |
| Статус SDD | `не требуется` |
| Ссылка на SDD | `—` |
| Дата создания | `2026-04-09` |
| Дата обновления | `2026-04-09` |

## Текущий этап

Черновик.
""",
        encoding="utf-8",
    )
    return task_file


class TaskWorkflowMarkdownTests:
    def test_update_task_file_with_delivery_units_inserts_publish_block_before_current_stage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            task_file = make_task_file(Path(tmp_dir))
            fields = update_task_file_with_delivery_units(
                task_file,
                "du/task-2026-0001-u01-demo",
                [
                    DeliveryUnit(
                        unit_id="DU-01",
                        purpose="Первая поставка",
                        head="du/task-2026-0001-u01-demo",
                        base="main",
                        host="none",
                        publication_type="none",
                        status="local",
                        url="—",
                        merge_commit="—",
                        cleanup="не требуется",
                    )
                ],
                today="2026-04-13",
                summary="Обновлённая summary",
            )

            text = task_file.read_text(encoding="utf-8")
            assert "## Контур публикации" in text
            assert text.index("## Контур публикации") < text.index("## Текущий этап")
            assert "| Ветка | `du/task-2026-0001-u01-demo` |" in text
            assert "| Дата обновления | `2026-04-13` |" in text
            assert fields["Ветка"] == "du/task-2026-0001-u01-demo"
            assert len(parse_delivery_units(text.splitlines())) == 1

    def test_task_summary_from_fields_ignores_placeholder(self) -> None:
        assert task_summary_from_fields({"Человекочитаемое описание": "—"}) is None
        assert task_summary_from_fields({"Человекочитаемое описание": "Валидная summary"}) == "Валидная summary"


class TestTaskWorkflowMarkdown(TaskWorkflowMarkdownTests, unittest.TestCase):
    pass
