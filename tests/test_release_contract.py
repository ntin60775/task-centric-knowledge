from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT
CORE_MODEL_PATH = SKILL_ROOT / "references" / "core-model.md"
TASK_LOCAL_CONTRACT_PATH = (
    REPO_ROOT
    / "knowledge/tasks/TASK-2026-0010-task-centric-vnext-core-contract/artifacts/vnext-core-contract.md"
)


def _section_body(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != heading:
            continue
        level = len(heading.split(" ", 1)[0])
        body: list[str] = []
        for candidate in lines[index + 1 :]:
            stripped = candidate.strip()
            if stripped.startswith("#"):
                prefix = stripped.split(" ", 1)[0]
                if set(prefix) == {"#"} and len(prefix) <= level:
                    break
            body.append(candidate)
        return body
    raise AssertionError(f"Не найден раздел {heading!r}.")


def _table_first_column_values(text: str, heading: str) -> list[str]:
    values: list[str] = []
    for line in _section_body(text, heading):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells:
            continue
        first_cell = cells[0].strip("`")
        if not first_cell or first_cell in {"Контекст", "Сущность", "Носитель"} or set(first_cell) == {"-"}:
            continue
        values.append(first_cell)
    return values


def _bullet_values(text: str, heading: str) -> list[str]:
    values: list[str] = []
    for line in _section_body(text, heading):
        stripped = line.strip()
        if stripped.startswith("- "):
            values.append(stripped[2:].strip("`"))
    return values


class ReleaseContractDocsTests(unittest.TestCase):
    def test_core_model_exists_and_covers_release_critical_sections(self) -> None:
        text = CORE_MODEL_PATH.read_text(encoding="utf-8")

        self.assertIn("дистрибутивный snapshot модели ядра", text)
        self.assertIn("TASK-2026-0010", text)
        self.assertIn("## DDD-карта контекстов", text)
        self.assertIn("## Источник истины и ownership по файлам", text)
        self.assertIn("## Модель состояний", text)
        self.assertIn("## Evidence и cleanup governance", text)
        self.assertIn("current-task", text)
        self.assertIn("doctor-deps", text)
        self.assertIn("ambiguous/branch_tie", text)

    def test_primary_skill_docs_trace_to_core_model(self) -> None:
        docs = [
            SKILL_ROOT / "SKILL.md",
            SKILL_ROOT / "references" / "deployment.md",
            SKILL_ROOT / "references" / "task-workflow.md",
            SKILL_ROOT / "references" / "adoption.md",
            SKILL_ROOT / "references" / "roadmap.md",
        ]

        for path in docs:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("references/core-model.md", text)

    def test_roadmap_marks_vnext_tracks_as_completed_history(self) -> None:
        text = (SKILL_ROOT / "references" / "roadmap.md").read_text(encoding="utf-8")

        self.assertIn("Фазы 1-4 уже закрыты задачами `TASK-2026-0010 ... TASK-2026-0014`", text)
        self.assertIn("Track 1. `vNext-core contract` (закрыт в `TASK-2026-0010`)", text)
        self.assertIn("Track 2. Модульная декомпозиция helper-а (закрыт в `TASK-2026-0011`)", text)
        self.assertIn("Track 3. `doctor / cleanup governance` (закрыт в `TASK-2026-0012`)", text)
        self.assertIn("Track 4. `Read model / reporting` (закрыт в `TASK-2026-0013`)", text)
        self.assertIn("Track 5. Полевая валидация (закрыт в `TASK-2026-0014`)", text)

    def test_distributive_core_model_stays_aligned_with_task_local_contract(self) -> None:
        self.assertTrue(
            TASK_LOCAL_CONTRACT_PATH.exists(),
            "Для release-contract traceability в этом репозитории обязан существовать task-local contract `TASK-2026-0010`.",
        )

        task_local_contract = TASK_LOCAL_CONTRACT_PATH.read_text(encoding="utf-8")
        core_model = CORE_MODEL_PATH.read_text(encoding="utf-8")

        for heading in (
            "## DDD-карта контекстов",
            "### Канонические task-local сущности",
        ):
            with self.subTest(section=heading):
                self.assertEqual(
                    set(_table_first_column_values(core_model, heading)),
                    set(_table_first_column_values(task_local_contract, heading)),
                )

        for heading in (
            "### Статусы `Task` и `Subtask`",
            "### Статусы `Delivery Unit`",
        ):
            with self.subTest(section=heading):
                self.assertEqual(_bullet_values(core_model, heading), _bullet_values(task_local_contract, heading))

        for marker in (
            "delivery unit живёт только внутри `task.md`",
            "`registry.md` не получает отдельных строк для delivery units",
            "plan -> confirm",
            "`project data`",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, task_local_contract)
                self.assertIn(marker, core_model)


if __name__ == "__main__":
    unittest.main()
