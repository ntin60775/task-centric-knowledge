from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from task_workflow_testlib import ROOT, TempRepoCase, git
from task_workflow_runtime.task_markdown import parse_delivery_units


QUERY_SCRIPT = ROOT / "scripts" / "task_query.py"
DELIVERY_HEADER = (
    "| Unit ID | Назначение | Head | Base | Host | Тип публикации | "
    "Статус | URL | Merge commit | Cleanup |"
)
DELIVERY_SEPARATOR = "|---------|------------|------|------|------|----------------|--------|-----|--------------|---------|"


class TaskQueryTests(TempRepoCase):
    def write_registry_row(
        self,
        project_root: Path,
        task_dir: Path,
        *,
        task_id: str,
        summary: str,
        status: str = "в работе",
        priority: str = "средний",
        branch: str = "не создана",
        parent_id: str = "—",
    ) -> None:
        registry_path = project_root / "knowledge/tasks/registry.md"
        registry_path.write_text(
            registry_path.read_text(encoding="utf-8")
            + (
                f"| `{task_id}` | `{parent_id}` | `{status}` | `{priority}` | `{branch}` | "
                f"`{task_dir.relative_to(project_root).as_posix().rstrip('/')}/` | {summary} |\n"
            ),
            encoding="utf-8",
        )

    def write_plan(self, task_dir: Path, *, unchecked_steps: list[str] | None = None) -> None:
        unchecked_steps = unchecked_steps or []
        plan_lines = [
            f"# План задачи {(task_dir / 'task.md').read_text(encoding='utf-8').splitlines()[0].split()[-1]}",
            "",
            "## Шаги",
            "",
        ]
        plan_lines.extend(f"- [ ] {step}" for step in unchecked_steps)
        (task_dir / "plan.md").write_text("\n".join(plan_lines) + "\n", encoding="utf-8")

    def rewrite_task_field(self, task_dir: Path, field: str, value: str) -> None:
        task_file = task_dir / "task.md"
        lines = task_file.read_text(encoding="utf-8").splitlines()
        replacement = f"| {field} | `{value}` |"
        for index, line in enumerate(lines):
            if line.startswith(f"| {field} |"):
                lines[index] = replacement
                break
        task_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def enrich_task(
        self,
        task_dir: Path,
        *,
        current_stage: str,
        automated_checks: list[str],
        manual_checks: list[str],
        delivery_rows: list[str] | None = None,
    ) -> None:
        task_file = task_dir / "task.md"
        text = task_file.read_text(encoding="utf-8")
        text = text.replace("## Текущий этап\n\nЧерновик.\n", f"## Текущий этап\n\n{current_stage}\n")
        additions: list[str] = []
        if delivery_rows is not None:
            additions.extend(
                [
                    "",
                    "## Контур публикации",
                    "",
                    DELIVERY_HEADER,
                    DELIVERY_SEPARATOR,
                    *delivery_rows,
                ]
            )
        additions.extend(
            [
                "",
                "## Стратегия проверки",
                "",
                "### Покрывается кодом или тестами",
                "",
                *[f"- {item}" for item in automated_checks],
                "",
                "### Остаётся на ручную проверку",
                "",
                *[f"- {item}" for item in manual_checks],
            ]
        )
        task_file.write_text(text.rstrip() + "\n" + "\n".join(additions).rstrip() + "\n", encoding="utf-8")

    def run_query(self, project_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(QUERY_SCRIPT), "--project-root", str(project_root), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def run_json_query(self, project_root: Path, *args: str) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        result = self.run_query(project_root, *args)
        return result, json.loads(result.stdout)

    def test_status_reports_current_task_review_tasks_and_open_delivery_units(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.write_registry(project_root)

            active_branch = "task/task-2026-1001-alpha"
            active_task_dir = project_root / "knowledge/tasks/TASK-2026-1001-alpha"
            self.write_task(
                active_task_dir,
                task_id="TASK-2026-1001",
                slug="alpha",
                branch=active_branch,
                priority="высокий",
                human_description="Альфа-задача для operator status.",
            )
            self.enrich_task(
                active_task_dir,
                current_stage="Реализация read-model слоя.",
                automated_checks=["python3 -m unittest"],
                manual_checks=["не требуется"],
                delivery_rows=[
                    "| `DU-01` | Draft поставка | `du/task-2026-1001-u01-alpha` | `main` | `github` | `pr` | `draft` | `https://example.test/pr/1` | `—` | `ожидается` |"
                ],
            )
            self.write_plan(active_task_dir, unchecked_steps=["Закрыть status/current-task/task show."])
            self.write_registry_row(
                project_root,
                active_task_dir,
                task_id="TASK-2026-1001",
                summary="Альфа-задача для operator status.",
                priority="высокий",
                branch=active_branch,
            )

            review_task_dir = project_root / "knowledge/tasks/TASK-2026-1002-beta"
            self.write_task(
                review_task_dir,
                task_id="TASK-2026-1002",
                slug="beta",
                branch="main",
                status="на проверке",
                human_description="Бета-задача на проверке.",
            )
            self.enrich_task(
                review_task_dir,
                current_stage="Ожидание ревью.",
                automated_checks=["python3 -m unittest"],
                manual_checks=["не требуется"],
            )
            self.write_plan(review_task_dir, unchecked_steps=["Дождаться ревью."])
            self.write_registry_row(
                project_root,
                review_task_dir,
                task_id="TASK-2026-1002",
                summary="Бета-задача на проверке.",
                status="на проверке",
                branch="main",
            )

            git(project_root, "checkout", "-b", active_branch)
            git(project_root, "add", ".")
            git(project_root, "commit", "-m", "query fixtures")

            result, payload = self.run_json_query(project_root, "status", "--format", "json")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["current_task"]["state"], "resolved")
            self.assertEqual(payload["current_task"]["task"]["summary"]["task_id"], "TASK-2026-1001")
            self.assertEqual(payload["task_counters"]["в работе"], 1)
            self.assertEqual(payload["task_counters"]["на проверке"], 1)
            self.assertEqual(len(payload["open_delivery_units"]), 1)
            self.assertEqual(payload["open_delivery_units"][0]["unit_id"], "DU-01")
            self.assertEqual(payload["review_tasks"][0]["summary"]["task_id"], "TASK-2026-1002")

    def test_status_reports_upgrade_governance_and_legacy_warnings(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.write_registry(project_root)
            task_dir = project_root / "knowledge/tasks/TASK-2026-1300-upgrade"
            self.write_task(
                task_dir,
                task_id="TASK-2026-1300",
                slug="upgrade",
                branch="main",
                human_description="Legacy upgrade task.",
            )
            self.write_registry_row(
                project_root,
                task_dir,
                task_id="TASK-2026-1300",
                summary="Legacy upgrade task.",
                branch="main",
            )
            upgrade_state = project_root / "knowledge/operations/task-centric-knowledge-upgrade.md"
            upgrade_state.parent.mkdir(parents=True, exist_ok=True)
            upgrade_state.write_text(
                (
                    "# Upgrade-state task-centric-knowledge\n\n"
                    "## Паспорт\n\n"
                    "| Поле | Значение |\n"
                    "|------|----------|\n"
                    "| Система | `task-centric-knowledge` |\n"
                    "| Эпоха совместимости | `module-core-v1` |\n"
                    "| Статус upgrade | `partially-upgraded` |\n"
                    "| Execution rollout | `dual-readiness` |\n"
                    "| Последняя задача перехода | `TASK-2026-0024.7` |\n"
                    "| Дата обновления | `2026-04-20` |\n\n"
                    "## Legacy tasks\n\n"
                    "| TASK-ID | Класс | Статус backfill | Migration note | Решение |\n"
                    "|---------|-------|-----------------|----------------|---------|\n"
                    "| `TASK-2026-1300` | `active` | `pending` | `—` | Требуется controlled compatibility-backfill. |\n"
                    "| `TASK-2026-1301` | `reference` | `manual-reference` | `—` | Manual decision. |\n"
                ),
                encoding="utf-8",
            )

            result, payload = self.run_json_query(project_root, "status", "--format", "json")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["upgrade_governance"]["compatibility_epoch"], "module-core-v1")
            self.assertEqual(payload["upgrade_governance"]["upgrade_status"], "partially-upgraded")
            self.assertEqual(payload["upgrade_governance"]["legacy_pending_count"], 1)
            self.assertEqual(payload["upgrade_governance"]["reference_manual_count"], 1)
            warning_codes = {item["code"] for item in payload["warnings"]}
            self.assertIn("legacy_backfill_pending", warning_codes)
            self.assertIn("reference_backfill_manual", warning_codes)
            self.assertIn("execution_rollout_partial", warning_codes)

    def test_current_task_resolves_parent_when_parent_and_subtask_share_branch(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.write_registry(project_root)

            shared_branch = "task/task-2026-1100-parent"
            parent_dir = project_root / "knowledge/tasks/TASK-2026-1100-parent"
            child_dir = parent_dir / "subtasks/TASK-2026-1100.1-child"
            for task_dir, task_id, slug, parent_id in (
                (parent_dir, "TASK-2026-1100", "parent", "—"),
                (child_dir, "TASK-2026-1100.1", "child", "TASK-2026-1100"),
            ):
                self.write_task(
                    task_dir,
                    task_id=task_id,
                    slug=slug,
                    branch=shared_branch,
                    human_description=f"{task_id} summary",
                )
                self.rewrite_task_field(task_dir, "Parent ID", parent_id)
                self.enrich_task(
                    task_dir,
                    current_stage=f"Stage for {task_id}.",
                    automated_checks=["python3 -m unittest"],
                    manual_checks=["не требуется"],
                )
                self.write_plan(task_dir, unchecked_steps=[f"Сделать {task_id}."])
                self.write_registry_row(
                    project_root,
                    task_dir,
                    task_id=task_id,
                    summary=f"{task_id} summary",
                    branch=shared_branch,
                    parent_id=parent_id,
                )

            git(project_root, "checkout", "-b", shared_branch)
            git(project_root, "add", ".")
            git(project_root, "commit", "-m", "ambiguous fixtures")

            result, payload = self.run_json_query(project_root, "current-task", "--format", "json")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["resolution"]["state"], "resolved")
            self.assertEqual(payload["resolution"]["reason"], "branch_parent")
            self.assertEqual(payload["resolution"]["task"]["summary"]["task_id"], "TASK-2026-1100")

    def test_current_task_keeps_ambiguity_for_unrelated_tasks_on_same_branch(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.write_registry(project_root)

            shared_branch = "main"
            task_dirs = (
                (project_root / "knowledge/tasks/TASK-2026-1150-alpha", "TASK-2026-1150", "alpha"),
                (project_root / "knowledge/tasks/TASK-2026-1151-beta", "TASK-2026-1151", "beta"),
            )
            for task_dir, task_id, slug in task_dirs:
                self.write_task(
                    task_dir,
                    task_id=task_id,
                    slug=slug,
                    branch=shared_branch,
                    human_description=f"{task_id} summary",
                )
                self.enrich_task(
                    task_dir,
                    current_stage=f"Stage for {task_id}.",
                    automated_checks=["python3 -m unittest"],
                    manual_checks=["не требуется"],
                )
                self.write_plan(task_dir, unchecked_steps=[f"Сделать {task_id}."])
                self.write_registry_row(
                    project_root,
                    task_dir,
                    task_id=task_id,
                    summary=f"{task_id} summary",
                    branch=shared_branch,
                )

            git(project_root, "add", ".")
            git(project_root, "commit", "-m", "unrelated branch tie fixtures")

            result, payload = self.run_json_query(project_root, "current-task", "--format", "json")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["resolution"]["state"], "ambiguous")
            self.assertEqual(payload["resolution"]["reason"], "branch_tie")
            self.assertEqual(
                sorted(candidate["summary"]["task_id"] for candidate in payload["resolution"]["candidates"]),
                ["TASK-2026-1150", "TASK-2026-1151"],
            )

    def test_current_task_prefers_non_final_candidates_on_shared_branch(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.write_registry(project_root)

            for task_dir, task_id, slug in (
                (project_root / "knowledge/tasks/TASK-2026-1160-done-alpha", "TASK-2026-1160", "done-alpha"),
                (project_root / "knowledge/tasks/TASK-2026-1161-done-beta", "TASK-2026-1161", "done-beta"),
            ):
                self.write_task(
                    task_dir,
                    task_id=task_id,
                    slug=slug,
                    branch="main",
                    status="завершена",
                    human_description=f"{task_id} historical summary",
                )
                self.enrich_task(
                    task_dir,
                    current_stage=f"{task_id} closed stage.",
                    automated_checks=["python3 -m unittest"],
                    manual_checks=["не требуется"],
                )
                self.write_plan(task_dir, unchecked_steps=[])
                self.write_registry_row(
                    project_root,
                    task_dir,
                    task_id=task_id,
                    summary=f"{task_id} historical summary",
                    status="завершена",
                    branch="main",
                )

            parent_dir = project_root / "knowledge/tasks/TASK-2026-1162-current"
            child_dir = parent_dir / "subtasks/TASK-2026-1162.1-review"
            for task_dir, task_id, slug, parent_id, status in (
                (parent_dir, "TASK-2026-1162", "current", "—", "в работе"),
                (child_dir, "TASK-2026-1162.1", "review", "TASK-2026-1162", "на проверке"),
            ):
                self.write_task(
                    task_dir,
                    task_id=task_id,
                    slug=slug,
                    branch="main",
                    status=status,
                    human_description=f"{task_id} active summary",
                )
                self.rewrite_task_field(task_dir, "Parent ID", parent_id)
                self.enrich_task(
                    task_dir,
                    current_stage=f"Stage for {task_id}.",
                    automated_checks=["python3 -m unittest"],
                    manual_checks=["не требуется"],
                )
                self.write_plan(task_dir, unchecked_steps=[f"Сделать {task_id}."])
                self.write_registry_row(
                    project_root,
                    task_dir,
                    task_id=task_id,
                    summary=f"{task_id} active summary",
                    status=status,
                    branch="main",
                    parent_id=parent_id,
                )

            git(project_root, "add", ".")
            git(project_root, "commit", "-m", "prefer active branch candidates")

            result, payload = self.run_json_query(project_root, "current-task", "--format", "json")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["resolution"]["state"], "resolved")
            self.assertEqual(payload["resolution"]["reason"], "branch_parent")
            self.assertEqual(payload["resolution"]["task"]["summary"]["task_id"], "TASK-2026-1162")
            self.assertNotIn("current_task_ambiguous", {warning["code"] for warning in payload["warnings"]})

    def test_current_task_uses_dirty_fallback_to_resolve_branch_tie(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.write_registry(project_root)

            shared_branch = "task/task-2026-1200-parent"
            parent_dir = project_root / "knowledge/tasks/TASK-2026-1200-parent"
            child_dir = parent_dir / "subtasks/TASK-2026-1200.1-child"
            for task_dir, task_id, slug, parent_id in (
                (parent_dir, "TASK-2026-1200", "parent", "—"),
                (child_dir, "TASK-2026-1200.1", "child", "TASK-2026-1200"),
            ):
                self.write_task(
                    task_dir,
                    task_id=task_id,
                    slug=slug,
                    branch=shared_branch,
                    human_description=f"{task_id} summary",
                )
                self.rewrite_task_field(task_dir, "Parent ID", parent_id)
                self.enrich_task(
                    task_dir,
                    current_stage=f"Stage for {task_id}.",
                    automated_checks=["python3 -m unittest"],
                    manual_checks=["не требуется"],
                )
                self.write_plan(task_dir, unchecked_steps=[f"Сделать {task_id}."])
                self.write_registry_row(
                    project_root,
                    task_dir,
                    task_id=task_id,
                    summary=f"{task_id} summary",
                    branch=shared_branch,
                    parent_id=parent_id,
                )

            git(project_root, "checkout", "-b", shared_branch)
            git(project_root, "add", ".")
            git(project_root, "commit", "-m", "dirty fallback fixtures")

            child_task_file = child_dir / "task.md"
            child_task_file.write_text(child_task_file.read_text(encoding="utf-8") + "\n", encoding="utf-8")

            result, payload = self.run_json_query(project_root, "current-task", "--format", "json")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["resolution"]["state"], "resolved")
            self.assertEqual(payload["resolution"]["reason"], "branch+dirty")
            self.assertEqual(payload["resolution"]["task"]["summary"]["task_id"], "TASK-2026-1200.1")

    def test_status_resolves_parent_for_shared_parent_subtask_branch(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.write_registry(project_root)

            shared_branch = "task/task-2026-1225-parent"
            parent_dir = project_root / "knowledge/tasks/TASK-2026-1225-parent"
            child_dir = parent_dir / "subtasks/TASK-2026-1225.1-child"
            for task_dir, task_id, slug, parent_id in (
                (parent_dir, "TASK-2026-1225", "parent", "—"),
                (child_dir, "TASK-2026-1225.1", "child", "TASK-2026-1225"),
            ):
                self.write_task(
                    task_dir,
                    task_id=task_id,
                    slug=slug,
                    branch=shared_branch,
                    human_description=f"{task_id} summary",
                )
                self.rewrite_task_field(task_dir, "Parent ID", parent_id)
                self.enrich_task(
                    task_dir,
                    current_stage=f"Stage for {task_id}.",
                    automated_checks=["python3 -m unittest"],
                    manual_checks=["не требуется"],
                )
                self.write_plan(task_dir, unchecked_steps=[f"Сделать {task_id}."])
                self.write_registry_row(
                    project_root,
                    task_dir,
                    task_id=task_id,
                    summary=f"{task_id} summary",
                    branch=shared_branch,
                    parent_id=parent_id,
                )

            git(project_root, "checkout", "-b", shared_branch)
            git(project_root, "add", ".")
            git(project_root, "commit", "-m", "status ambiguous fixtures")

            result, payload = self.run_json_query(project_root, "status", "--format", "json")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["current_task"]["state"], "resolved")
            self.assertEqual(payload["current_task"]["reason"], "branch_parent")
            self.assertEqual(payload["current_task"]["task"]["summary"]["task_id"], "TASK-2026-1225")
            self.assertNotIn("current_task_ambiguous", {warning["code"] for warning in payload["warnings"]})

    def test_current_task_keeps_ambiguity_when_parent_and_subtask_are_both_dirty(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.write_registry(project_root)

            shared_branch = "task/task-2026-1230-parent"
            parent_dir = project_root / "knowledge/tasks/TASK-2026-1230-parent"
            child_dir = parent_dir / "subtasks/TASK-2026-1230.1-child"
            for task_dir, task_id, slug, parent_id in (
                (parent_dir, "TASK-2026-1230", "parent", "—"),
                (child_dir, "TASK-2026-1230.1", "child", "TASK-2026-1230"),
            ):
                self.write_task(
                    task_dir,
                    task_id=task_id,
                    slug=slug,
                    branch=shared_branch,
                    human_description=f"{task_id} summary",
                )
                self.rewrite_task_field(task_dir, "Parent ID", parent_id)
                self.enrich_task(
                    task_dir,
                    current_stage=f"Stage for {task_id}.",
                    automated_checks=["python3 -m unittest"],
                    manual_checks=["не требуется"],
                )
                self.write_plan(task_dir, unchecked_steps=[f"Сделать {task_id}."])
                self.write_registry_row(
                    project_root,
                    task_dir,
                    task_id=task_id,
                    summary=f"{task_id} summary",
                    branch=shared_branch,
                    parent_id=parent_id,
                )

            git(project_root, "checkout", "-b", shared_branch)
            git(project_root, "add", ".")
            git(project_root, "commit", "-m", "dirty tie fixtures")

            parent_task_file = parent_dir / "task.md"
            child_task_file = child_dir / "task.md"
            parent_task_file.write_text(parent_task_file.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            child_task_file.write_text(child_task_file.read_text(encoding="utf-8") + "\n", encoding="utf-8")

            result, payload = self.run_json_query(project_root, "current-task", "--format", "json")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["resolution"]["state"], "ambiguous")
            self.assertEqual(payload["resolution"]["reason"], "branch_tie")
            self.assertEqual(
                sorted(candidate["summary"]["task_id"] for candidate in payload["resolution"]["candidates"]),
                ["TASK-2026-1230", "TASK-2026-1230.1"],
            )

    def test_status_keeps_ambiguity_when_parent_and_subtask_are_both_dirty(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.write_registry(project_root)

            shared_branch = "task/task-2026-1235-parent"
            parent_dir = project_root / "knowledge/tasks/TASK-2026-1235-parent"
            child_dir = parent_dir / "subtasks/TASK-2026-1235.1-child"
            for task_dir, task_id, slug, parent_id in (
                (parent_dir, "TASK-2026-1235", "parent", "—"),
                (child_dir, "TASK-2026-1235.1", "child", "TASK-2026-1235"),
            ):
                self.write_task(
                    task_dir,
                    task_id=task_id,
                    slug=slug,
                    branch=shared_branch,
                    human_description=f"{task_id} summary",
                )
                self.rewrite_task_field(task_dir, "Parent ID", parent_id)
                self.enrich_task(
                    task_dir,
                    current_stage=f"Stage for {task_id}.",
                    automated_checks=["python3 -m unittest"],
                    manual_checks=["не требуется"],
                )
                self.write_plan(task_dir, unchecked_steps=[f"Сделать {task_id}."])
                self.write_registry_row(
                    project_root,
                    task_dir,
                    task_id=task_id,
                    summary=f"{task_id} summary",
                    branch=shared_branch,
                    parent_id=parent_id,
                )

            git(project_root, "checkout", "-b", shared_branch)
            git(project_root, "add", ".")
            git(project_root, "commit", "-m", "status dirty tie fixtures")

            parent_task_file = parent_dir / "task.md"
            child_task_file = child_dir / "task.md"
            parent_task_file.write_text(parent_task_file.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            child_task_file.write_text(child_task_file.read_text(encoding="utf-8") + "\n", encoding="utf-8")

            result, payload = self.run_json_query(project_root, "status", "--format", "json")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["current_task"]["state"], "ambiguous")
            self.assertEqual(payload["current_task"]["reason"], "branch_tie")
            self.assertIn("current_task_ambiguous", {warning["code"] for warning in payload["warnings"]})

    def test_current_task_ignores_unrelated_dirty_paths_for_branch_tie_resolution(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.write_registry(project_root)

            shared_branch = "task/task-2026-1250-parent"
            parent_dir = project_root / "knowledge/tasks/TASK-2026-1250-parent"
            child_dir = parent_dir / "subtasks/TASK-2026-1250.1-child"
            for task_dir, task_id, slug, parent_id in (
                (parent_dir, "TASK-2026-1250", "parent", "—"),
                (child_dir, "TASK-2026-1250.1", "child", "TASK-2026-1250"),
            ):
                self.write_task(
                    task_dir,
                    task_id=task_id,
                    slug=slug,
                    branch=shared_branch,
                    human_description=f"{task_id} summary",
                )
                self.rewrite_task_field(task_dir, "Parent ID", parent_id)
                self.enrich_task(
                    task_dir,
                    current_stage=f"Stage for {task_id}.",
                    automated_checks=["python3 -m unittest"],
                    manual_checks=["не требуется"],
                )
                self.write_plan(task_dir, unchecked_steps=[f"Сделать {task_id}."])
                self.write_registry_row(
                    project_root,
                    task_dir,
                    task_id=task_id,
                    summary=f"{task_id} summary",
                    branch=shared_branch,
                    parent_id=parent_id,
                )

            git(project_root, "checkout", "-b", shared_branch)
            git(project_root, "add", ".")
            git(project_root, "commit", "-m", "dirty fallback with unrelated fixtures")

            (child_dir / "task.md").write_text((child_dir / "task.md").read_text(encoding="utf-8") + "\n", encoding="utf-8")
            (project_root / "scratch.txt").write_text("out-of-task dirty path\n", encoding="utf-8")

            result, payload = self.run_json_query(project_root, "current-task", "--format", "json")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["resolution"]["state"], "resolved")
            self.assertEqual(payload["resolution"]["reason"], "branch+dirty")
            self.assertEqual(payload["resolution"]["task"]["summary"]["task_id"], "TASK-2026-1250.1")

    def test_current_task_is_unresolved_without_branch_match_or_dirty_scope(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.write_registry(project_root)

            task_dir = project_root / "knowledge/tasks/TASK-2026-1300-orphan"
            self.write_task(
                task_dir,
                task_id="TASK-2026-1300",
                slug="orphan",
                branch="не создана",
                human_description="Orphan summary",
            )
            self.enrich_task(
                task_dir,
                current_stage="Ожидание старта.",
                automated_checks=["python3 -m unittest"],
                manual_checks=["не требуется"],
            )
            self.write_plan(task_dir, unchecked_steps=["Начать задачу."])
            self.write_registry_row(
                project_root,
                task_dir,
                task_id="TASK-2026-1300",
                summary="Orphan summary",
                branch="не создана",
            )

            git(project_root, "add", ".")
            git(project_root, "commit", "-m", "unresolved fixtures")

            result, payload = self.run_json_query(project_root, "current-task", "--format", "json")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["resolution"]["state"], "unresolved")
            self.assertEqual(payload["warnings"][0]["code"], "current_task_unresolved")

    def test_task_show_supports_current_and_exact_task_id(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.write_registry(project_root)

            active_branch = "task/task-2026-1400-demo"
            task_dir = project_root / "knowledge/tasks/TASK-2026-1400-demo"
            self.write_task(
                task_dir,
                task_id="TASK-2026-1400",
                slug="demo",
                branch=active_branch,
                human_description="Demo task summary",
            )
            self.enrich_task(
                task_dir,
                current_stage="Реализация task show.",
                automated_checks=["python3 -m unittest tests/test_task_query.py"],
                manual_checks=["Проверить читаемость вывода."],
                delivery_rows=[
                    "| `DU-01` | Demo поставка | `du/task-2026-1400-u01-demo` | `main` | `none` | `none` | `local` | `—` | `—` | `не требуется` |"
                ],
            )
            self.write_plan(task_dir, unchecked_steps=["Сделать task show."])
            self.write_registry_row(
                project_root,
                task_dir,
                task_id="TASK-2026-1400",
                summary="Demo task summary",
                branch=active_branch,
            )

            git(project_root, "checkout", "-b", active_branch)
            git(project_root, "add", ".")
            git(project_root, "commit", "-m", "task show fixtures")

            current_result, current_payload = self.run_json_query(project_root, "task", "show", "current", "--format", "json")
            exact_result, exact_payload = self.run_json_query(project_root, "task", "show", "TASK-2026-1400", "--format", "json")
            text_result = self.run_query(project_root, "task", "show", "TASK-2026-1400")

            self.assertEqual(current_result.returncode, 0)
            self.assertEqual(current_payload["task"]["summary"]["task_id"], "TASK-2026-1400")
            self.assertIn("plan.md", current_payload["task"]["files"])
            self.assertEqual(current_payload["task"]["verify"]["manual"], ["Проверить читаемость вывода."])
            self.assertEqual(exact_result.returncode, 0)
            self.assertEqual(exact_payload["task"]["summary"]["short_name"], "demo")
            self.assertIn("TASK-2026-1400 · demo", text_result.stdout)
            self.assertIn("Связанные материалы", text_result.stdout)
            self.assertIn("Контур публикации", text_result.stdout)

    def test_task_show_text_reports_missing_task_without_traceback(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.write_registry(project_root)

            result = self.run_query(project_root, "task", "show", "TASK-9999-404")

            self.assertEqual(result.returncode, 2)
            self.assertIn("task show", result.stdout)
            self.assertIn("task_not_found", result.stdout)
            self.assertNotIn("Traceback", result.stderr)

    def test_task_show_reports_drift_and_open_delivery_warning(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.write_registry(project_root)

            task_dir = project_root / "knowledge/tasks/TASK-2026-1500-drift"
            self.write_task(
                task_dir,
                task_id="TASK-2026-1500",
                slug="drift",
                branch="task/task-2026-1500-drift",
                status="завершена",
                human_description="Каноническая summary drift-задачи.",
            )
            self.enrich_task(
                task_dir,
                current_stage="Формально завершена.",
                automated_checks=["python3 -m unittest"],
                manual_checks=["не требуется"],
                delivery_rows=[
                    "| `DU-01` | Drift поставка | `du/task-2026-1500-u01-drift` | `main` | `github` | `pr` | `review` | `https://example.test/pr/7` | `—` | `ожидается` |"
                ],
            )
            self.write_plan(task_dir, unchecked_steps=[])
            self.write_registry_row(
                project_root,
                task_dir,
                task_id="TASK-2026-1500",
                summary="Устаревший registry cache.",
                status="завершена",
                branch="main",
            )

            git(project_root, "checkout", "-b", "task/task-2026-1500-drift")
            git(project_root, "add", ".")
            git(project_root, "commit", "-m", "drift fixtures")

            result, payload = self.run_json_query(project_root, "task", "show", "TASK-2026-1500", "--format", "json")
            warning_codes = {warning["code"] for warning in payload["warnings"]}

            self.assertEqual(result.returncode, 0)
            self.assertIn("summary_drift", warning_codes)
            self.assertIn("branch_drift", warning_codes)
            self.assertIn("final_task_with_open_delivery_units", warning_codes)

    def test_task_show_warns_on_planned_final_delivery_and_noncanonical_publish_fields(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.write_registry(project_root)

            task_dir = project_root / "knowledge/tasks/TASK-2026-1550-publish"
            self.write_task(
                task_dir,
                task_id="TASK-2026-1550",
                slug="publish",
                branch="task/task-2026-1550-publish",
                status="завершена",
                human_description="Publish warning summary",
            )
            self.enrich_task(
                task_dir,
                current_stage="Формально завершена.",
                automated_checks=["python3 -m unittest"],
                manual_checks=["не требуется"],
                delivery_rows=[
                    "| `DU-01` | Publish поставка | `du/task-2026-1550-u01-publish` | `main` | `custom-host` | `ticket` | `planned` | `—` | `—` | `позже` |"
                ],
            )
            self.write_plan(task_dir, unchecked_steps=[])
            self.write_registry_row(
                project_root,
                task_dir,
                task_id="TASK-2026-1550",
                summary="Publish warning summary",
                status="завершена",
                branch="task/task-2026-1550-publish",
            )

            result, payload = self.run_json_query(project_root, "task", "show", "TASK-2026-1550", "--format", "json")
            warning_codes = {warning["code"] for warning in payload["warnings"]}

            self.assertEqual(result.returncode, 0)
            self.assertIn("final_task_with_open_delivery_units", warning_codes)
            self.assertIn("noncanonical_delivery_host", warning_codes)
            self.assertIn("noncanonical_publication_type", warning_codes)
            self.assertIn("noncanonical_cleanup_value", warning_codes)

    def test_task_show_warns_on_invalid_delivery_row_instead_of_crashing(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.write_registry(project_root)

            task_dir = project_root / "knowledge/tasks/TASK-2026-1560-malformed"
            self.write_task(
                task_dir,
                task_id="TASK-2026-1560",
                slug="malformed",
                branch="task/task-2026-1560-malformed",
                human_description="Malformed delivery summary",
            )
            self.enrich_task(
                task_dir,
                current_stage="Есть битая строка publish-контура.",
                automated_checks=["python3 -m unittest"],
                manual_checks=["не требуется"],
                delivery_rows=[
                    "| `DU-1x` | Broken row | `du/task-2026-1560-u01-malformed` | `main` | `github` | `pr` | `draft` | `https://example.test/pr/11` | `—` | `ожидается` |"
                ],
            )
            self.write_plan(task_dir, unchecked_steps=["Починить publish-контур."])
            self.write_registry_row(
                project_root,
                task_dir,
                task_id="TASK-2026-1560",
                summary="Malformed delivery summary",
                branch="task/task-2026-1560-malformed",
            )

            text_result = self.run_query(project_root, "task", "show", "TASK-2026-1560")
            json_result, payload = self.run_json_query(project_root, "task", "show", "TASK-2026-1560", "--format", "json")

            self.assertEqual(text_result.returncode, 0)
            self.assertIn("delivery_unit_parse_error", text_result.stdout)
            self.assertEqual(json_result.returncode, 0)
            self.assertEqual(payload["task"]["delivery_units"], [])
            self.assertIn("delivery_unit_parse_error", {warning["code"] for warning in payload["warnings"]})

    def test_task_show_warns_on_short_delivery_row_and_keeps_final_task_flagged(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.write_registry(project_root)

            task_dir = project_root / "knowledge/tasks/TASK-2026-1565-short-row"
            self.write_task(
                task_dir,
                task_id="TASK-2026-1565",
                slug="short-row",
                branch="task/task-2026-1565-short-row",
                status="завершена",
                human_description="Short delivery row summary",
            )
            self.enrich_task(
                task_dir,
                current_stage="Есть повреждённая строка publish-контура.",
                automated_checks=["python3 -m unittest"],
                manual_checks=["не требуется"],
                delivery_rows=[
                    "| `DU-01` | Short row | `du/task-2026-1565-u01-short-row` | `main` | `github` | `pr` | `planned` | `https://example.test/pr/12` | `—` |"
                ],
            )
            self.write_plan(task_dir, unchecked_steps=[])
            self.write_registry_row(
                project_root,
                task_dir,
                task_id="TASK-2026-1565",
                summary="Short delivery row summary",
                status="завершена",
                branch="task/task-2026-1565-short-row",
            )

            result, payload = self.run_json_query(project_root, "task", "show", "TASK-2026-1565", "--format", "json")
            warning_codes = {warning["code"] for warning in payload["warnings"]}

            self.assertEqual(result.returncode, 0)
            self.assertIn("delivery_unit_parse_error", warning_codes)
            self.assertIn("final_task_with_open_delivery_units", warning_codes)
            self.assertEqual(payload["task"]["delivery_units"], [])

    def test_waiting_task_raises_stage_into_blockers(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.write_registry(project_root)

            active_branch = "task/task-2026-1600-waiting"
            task_dir = project_root / "knowledge/tasks/TASK-2026-1600-waiting"
            self.write_task(
                task_dir,
                task_id="TASK-2026-1600",
                slug="waiting",
                branch=active_branch,
                status="ждёт пользователя",
                human_description="Waiting task summary",
            )
            self.enrich_task(
                task_dir,
                current_stage="Нужен ответ пользователя по transport-layer.",
                automated_checks=["python3 -m unittest"],
                manual_checks=["Дождаться решения пользователя."],
            )
            self.write_plan(task_dir, unchecked_steps=["Получить ответ пользователя."])
            self.write_registry_row(
                project_root,
                task_dir,
                task_id="TASK-2026-1600",
                summary="Waiting task summary",
                status="ждёт пользователя",
                branch=active_branch,
            )

            git(project_root, "checkout", "-b", active_branch)
            git(project_root, "add", ".")
            git(project_root, "commit", "-m", "waiting fixtures")

            result, payload = self.run_json_query(project_root, "current-task", "--format", "json")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["resolution"]["task"]["blockers"], ["Нужен ответ пользователя по transport-layer."])

    def test_status_reports_health_warnings_for_missing_knowledge_registry_and_invalid_managed_block(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            (project_root / "AGENTS.md").write_text("prefix\n⟦⟦BEGIN_TASK_KNOWLEDGE_SYSTEM#KB01⟧⟧\n", encoding="utf-8")

            result, payload = self.run_json_query(project_root, "status", "--format", "json")
            warning_codes = {warning["code"] for warning in payload["warnings"]}

            self.assertEqual(result.returncode, 0)
            self.assertIn("knowledge_missing", warning_codes)
            self.assertIn("registry_missing", warning_codes)
            self.assertIn("managed_block_invalid", warning_codes)

    def test_task_show_reports_summary_fallback_goal_and_missing_next_step(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.write_registry(project_root)

            task_dir = project_root / "knowledge/tasks/TASK-2026-1700-fallback"
            goal_summary = "Fallback summary from goal."
            self.write_task(
                task_dir,
                task_id="TASK-2026-1700",
                slug="fallback",
                branch="task/task-2026-1700-fallback",
                goal=goal_summary,
                human_description="—",
            )
            self.enrich_task(
                task_dir,
                current_stage="Нужно достроить план.",
                automated_checks=["python3 -m unittest"],
                manual_checks=["не требуется"],
            )
            self.write_registry_row(
                project_root,
                task_dir,
                task_id="TASK-2026-1700",
                summary=goal_summary,
                branch="task/task-2026-1700-fallback",
            )

            result, payload = self.run_json_query(project_root, "task", "show", "TASK-2026-1700", "--format", "json")
            warning_codes = {warning["code"] for warning in payload["warnings"]}

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["task"]["summary"]["human_description"], goal_summary)
            self.assertIn("summary_fallback_goal", warning_codes)
            self.assertIn("next_step_missing", warning_codes)

    def test_task_show_reports_duplicate_task_id_as_ambiguous_selector(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.write_registry(project_root)

            first_dir = project_root / "knowledge/tasks/TASK-2026-1800-alpha"
            second_dir = project_root / "knowledge/tasks/TASK-2026-1800-beta"
            for task_dir, slug, summary in (
                (first_dir, "alpha", "Duplicate task alpha"),
                (second_dir, "beta", "Duplicate task beta"),
            ):
                self.write_task(
                    task_dir,
                    task_id="TASK-2026-1800",
                    slug=slug,
                    branch="task/task-2026-1800-alpha",
                    human_description=summary,
                )
                self.enrich_task(
                    task_dir,
                    current_stage=f"Stage for {slug}.",
                    automated_checks=["python3 -m unittest"],
                    manual_checks=["не требуется"],
                )

            result, payload = self.run_json_query(project_root, "task", "show", "TASK-2026-1800", "--format", "json")

            self.assertEqual(result.returncode, 2)
            self.assertEqual(payload["resolution"]["state"], "ambiguous")
            self.assertEqual(payload["resolution"]["reason"], "duplicate_task_id")
            self.assertEqual(len(payload["resolution"]["candidates"]), 2)
            self.assertEqual(payload["warnings"][0]["code"], "duplicate_task_id")

    def test_parse_delivery_units_leniently_skips_short_rows_for_workflow_helpers(self) -> None:
        lines = [
            "## Контур публикации",
            "",
            DELIVERY_HEADER,
            DELIVERY_SEPARATOR,
            "| `DU-01` | Short row | `du/task-2026-1900-u01-short-row` | `main` | `github` | `pr` | `planned` | `https://example.test/pr/12` | `—` |",
        ]

        units = parse_delivery_units(lines)

        self.assertEqual(units, [])


class TestTaskQuery(TaskQueryTests, unittest.TestCase):
    pass
