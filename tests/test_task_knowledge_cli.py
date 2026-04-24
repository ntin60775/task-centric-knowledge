from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from task_workflow_testlib import ROOT, SUBPROCESS_TIMEOUT_SECONDS, TempRepoCase, git


CLI_SCRIPT = ROOT / "scripts" / "task_knowledge_cli.py"


class TaskKnowledgeCliTests(TempRepoCase):
    def run_cli(self, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI_SCRIPT), *args],
            capture_output=True,
            text=True,
            check=False,
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
            env=env,
        )

    def run_cli_json(
        self,
        *args: str,
        env: dict[str, str] | None = None,
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        result = self.run_cli("--json", *args, env=env)
        return result, json.loads(result.stdout)

    def test_doctor_reports_project_and_runtime(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.write_registry(project_root)

            result, payload = self.run_cli_json("doctor", "--project-root", str(project_root))

            self.assertEqual(result.returncode, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "doctor")
            self.assertEqual(payload["project_root"], str(project_root.resolve()))
            self.assertIn("install_check", payload)
            self.assertIn("dependency_check", payload)
            self.assertEqual(
                payload["supported_commands"],
                ["doctor", "install", "task", "module", "file", "workflow", "borrowings"],
            )

    def test_install_cleanup_plan_uses_new_confirm_command_surface(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            suggestion_path = project_root / "knowledge" / "MIGRATION-SUGGESTION.md"
            suggestion_path.parent.mkdir(parents=True, exist_ok=True)
            suggestion_path.write_text("cleanup me\n", encoding="utf-8")

            result, payload = self.run_cli_json(
                "install",
                "cleanup-plan",
                "--project-root",
                str(project_root),
                "--existing-system-mode",
                "migrate",
            )

            self.assertEqual(result.returncode, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["mode"], "migrate-cleanup-plan")
            self.assertIn("task-knowledge install cleanup-confirm", payload["confirm_command"])

    def test_task_status_routes_to_query_runtime(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.write_registry(project_root)
            task_dir = project_root / "knowledge/tasks/TASK-2026-1200-alpha"
            self.write_task(
                task_dir,
                task_id="TASK-2026-1200",
                slug="alpha",
                branch="task/task-2026-1200-alpha",
                human_description="Тестовая задача для unified CLI.",
            )
            registry_path = project_root / "knowledge/tasks/registry.md"
            registry_path.write_text(
                registry_path.read_text(encoding="utf-8")
                + "| `TASK-2026-1200` | `—` | `в работе` | `средний` | `task/task-2026-1200-alpha` | `knowledge/tasks/TASK-2026-1200-alpha/` | Тестовая задача для unified CLI. |\n",
                encoding="utf-8",
            )

            git(project_root, "checkout", "-b", "task/task-2026-1200-alpha")
            git(project_root, "add", ".")
            git(project_root, "commit", "-m", "cli fixtures")

            result, payload = self.run_cli_json("task", "status", "--project-root", str(project_root))

            self.assertEqual(result.returncode, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "status")
            self.assertEqual(payload["current_task"]["state"], "resolved")

    def test_task_status_degrades_without_git_repository(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            self.write_registry(project_root)
            task_dir = project_root / "knowledge/tasks/TASK-2026-1201-archive"
            self.write_task(
                task_dir,
                task_id="TASK-2026-1201",
                slug="archive",
                branch="task/task-2026-1201-archive",
                priority="высокий",
                human_description="Архивная задача без git-контекста.",
            )
            registry_path = project_root / "knowledge/tasks/registry.md"
            registry_path.write_text(
                registry_path.read_text(encoding="utf-8")
                + "| `TASK-2026-1201` | `—` | `в работе` | `высокий` | `task/task-2026-1201-archive` | `knowledge/tasks/TASK-2026-1201-archive/` | Архивная задача без git-контекста. |\n",
                encoding="utf-8",
            )

            result, payload = self.run_cli_json("task", "status", "--project-root", str(project_root))

            self.assertEqual(result.returncode, 0)
            self.assertTrue(payload["ok"])
            self.assertIsNone(payload["active_branch"])
            self.assertEqual(payload["current_task"]["state"], "unresolved")
            self.assertEqual(payload["current_task"]["reason"], "git_unavailable")
            self.assertIsNone(payload["current_task"]["task"])
            self.assertEqual(payload["high_priority_open"][0]["summary"]["task_id"], "TASK-2026-1201")
            self.assertIn("git_context_unavailable", {item["code"] for item in payload["warnings"]})

    def test_doctor_reports_embedded_runtime_without_treating_project_as_source(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            self.write_registry(project_root)
            (project_root / "task-knowledge.project.json").write_text('{"schema": "test"}\n', encoding="utf-8")
            shutil.copytree(
                ROOT / "scripts",
                project_root / "scripts",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(project_root / "scripts/task_knowledge_cli.py"),
                    "--json",
                    "doctor",
                    "--project-root",
                    str(project_root),
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=SUBPROCESS_TIMEOUT_SECONDS,
            )
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 2)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["runtime_root"], str((project_root / "scripts").resolve()))
            self.assertEqual(payload["source_root"], str(project_root.resolve()))
            self.assertFalse(payload["source_root_valid"])
            self.assertEqual(payload["source_root_mode"], "embedded")
            self.assertEqual(payload["consumer_runtime_contract"], "consumer-runtime-v1")
            self.assertFalse(payload["install_check"]["source_root_valid"])
            self.assertEqual(payload["install_check"]["source_root_mode"], "embedded")
            self.assertIn("standalone-дистрибутив", payload["install_check"]["results"][0]["detail"])
            result_paths = [item.get("path", "") for item in payload["results"]]
            self.assertNotIn(str(project_root / "SKILL.md"), result_paths)
            self.assertNotIn(str(project_root / "assets/knowledge/README.md"), result_paths)

    def test_install_check_reports_single_source_root_blocker_for_embedded_runtime(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            self.write_registry(project_root)
            shutil.copytree(
                ROOT / "scripts",
                project_root / "scripts",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(project_root / "scripts/task_knowledge_cli.py"),
                    "--json",
                    "install",
                    "check",
                    "--project-root",
                    str(project_root),
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=SUBPROCESS_TIMEOUT_SECONDS,
            )
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 2)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["runtime_root"], str((project_root / "scripts").resolve()))
            self.assertFalse(payload["source_root_valid"])
            self.assertEqual(payload["source_root_mode"], "embedded")
            source_results = [item for item in payload["results"] if item["key"] in {"source", "source_root_unavailable"}]
            self.assertEqual(len(source_results), 1)
            self.assertEqual(source_results[0]["key"], "source_root_unavailable")
            self.assertIn("embedded runtime subset", source_results[0]["detail"])

    def test_embedded_runtime_allows_consumer_owned_assets_and_references(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            self.write_registry(project_root)
            (project_root / "assets/product").mkdir(parents=True)
            (project_root / "assets/product/logo.txt").write_text("consumer asset\n", encoding="utf-8")
            (project_root / "references").mkdir()
            (project_root / "references/product.md").write_text("# Consumer reference\n", encoding="utf-8")
            shutil.copytree(
                ROOT / "scripts",
                project_root / "scripts",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(project_root / "scripts/task_knowledge_cli.py"),
                    "--json",
                    "install",
                    "check",
                    "--project-root",
                    str(project_root),
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=SUBPROCESS_TIMEOUT_SECONDS,
            )
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 2)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["source_root_mode"], "embedded")
            source_results = [item for item in payload["results"] if item["key"] in {"source", "source_root_unavailable"}]
            self.assertEqual(len(source_results), 1)
            self.assertEqual(source_results[0]["key"], "source_root_unavailable")

    def test_install_doctor_deps_reports_single_source_root_blocker_for_embedded_runtime(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            self.write_registry(project_root)
            shutil.copytree(
                ROOT / "scripts",
                project_root / "scripts",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(project_root / "scripts/task_knowledge_cli.py"),
                    "--json",
                    "install",
                    "doctor-deps",
                    "--project-root",
                    str(project_root),
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=SUBPROCESS_TIMEOUT_SECONDS,
            )
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 2)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["runtime_root"], str((project_root / "scripts").resolve()))
            self.assertFalse(payload["source_root_valid"])
            self.assertEqual(payload["source_root_mode"], "embedded")
            source_results = [item for item in payload["results"] if item["key"] in {"source", "source_root_unavailable"}]
            self.assertEqual(len(source_results), 1)
            self.assertEqual(source_results[0]["key"], "source_root_unavailable")
            dependencies = {item["name"]: item for item in payload["dependencies"]}
            self.assertEqual(dependencies["skill_source"]["status"], "misconfigured")

    def test_embedded_runtime_accepts_explicit_external_source_root_for_install_check(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            self.write_registry(project_root)
            shutil.copytree(
                ROOT / "scripts",
                project_root / "scripts",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(project_root / "scripts/task_knowledge_cli.py"),
                    "--json",
                    "install",
                    "check",
                    "--project-root",
                    str(project_root),
                    "--source-root",
                    str(ROOT),
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=SUBPROCESS_TIMEOUT_SECONDS,
            )
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["runtime_root"], str((project_root / "scripts").resolve()))
            self.assertTrue(payload["source_root_valid"])
            self.assertEqual(payload["source_root_mode"], "external")
            self.assertEqual(payload["source_root"], str(ROOT.resolve()))

    def test_damaged_standalone_source_is_not_reported_as_embedded_runtime(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            self.write_registry(project_root)
            source_root = Path(tmp_dir) / "damaged-source"
            shutil.copytree(
                ROOT,
                source_root,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
            )
            (source_root / "references/consumer-runtime-v1.md").unlink()

            result, payload = self.run_cli_json(
                "install",
                "check",
                "--project-root",
                str(project_root),
                "--source-root",
                str(source_root),
            )

            self.assertEqual(result.returncode, 2)
            self.assertFalse(payload["ok"])
            self.assertFalse(payload["source_root_valid"])
            self.assertEqual(payload["source_root_mode"], "unavailable")
            self.assertNotIn("source_root_unavailable", {item["key"] for item in payload["results"]})
            missing_sources = [
                item for item in payload["results"]
                if item["key"] == "source" and item["status"] == "error"
            ]
            self.assertEqual(len(missing_sources), 1)
            self.assertTrue(missing_sources[0]["path"].endswith("references/consumer-runtime-v1.md"))

    def test_doctor_reports_damaged_standalone_source_as_missing_resource(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            self.write_registry(project_root)
            source_root = Path(tmp_dir) / "damaged-source"
            shutil.copytree(
                ROOT,
                source_root,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
            )
            (source_root / "references/consumer-runtime-v1.md").unlink()

            result, payload = self.run_cli_json(
                "doctor",
                "--project-root",
                str(project_root),
                "--source-root",
                str(source_root),
            )

            self.assertEqual(result.returncode, 2)
            self.assertFalse(payload["ok"])
            self.assertFalse(payload["source_root_valid"])
            self.assertEqual(payload["source_root_mode"], "unavailable")
            self.assertNotIn("source_root_unavailable", {item["key"] for item in payload["results"]})
            missing_sources = [
                item for item in payload["install_check"]["results"]
                if item["key"] == "source" and item["status"] == "error"
            ]
            self.assertEqual(len(missing_sources), 1)
            self.assertTrue(missing_sources[0]["path"].endswith("references/consumer-runtime-v1.md"))

    def test_workflow_finalize_routes_to_finalize_runtime(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            git(project_root, "branch", "-M", "main")
            self.write_registry(project_root)
            task_dir = project_root / "knowledge/tasks/TASK-2026-1300-finalize"
            self.write_task(
                task_dir,
                task_id="TASK-2026-1300",
                slug="finalize",
                branch="task/task-2026-1300-finalize",
                human_description="CLI finalize task.",
            )
            registry_path = project_root / "knowledge/tasks/registry.md"
            registry_path.write_text(
                registry_path.read_text(encoding="utf-8")
                + "| `TASK-2026-1300` | `—` | `в работе` | `средний` | `task/task-2026-1300-finalize` | `knowledge/tasks/TASK-2026-1300-finalize/` | CLI finalize task. |\n",
                encoding="utf-8",
            )
            git(project_root, "add", ".")
            git(project_root, "commit", "-m", "prepare finalize cli fixtures")
            git(project_root, "checkout", "-b", "task/task-2026-1300-finalize")
            (project_root / "feature.txt").write_text("cli finalize\n", encoding="utf-8")

            result, payload = self.run_cli_json(
                "workflow",
                "finalize",
                "--project-root",
                str(project_root),
                "--task-dir",
                "knowledge/tasks/TASK-2026-1300-finalize",
                "--base-branch",
                "main",
                "--commit-message",
                "TASK-2026-1300: finalize cli",
            )

            self.assertEqual(result.returncode, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["action"], "finalize")
            self.assertEqual(payload["outcome"], "finalized")
            self.assertEqual(payload["branch"], "main")
            self.assertEqual(git(project_root, "branch", "--show-current"), "main")

    def test_workflow_publish_error_payload_keeps_command_and_action(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))

            result, payload = self.run_cli_json(
                "workflow",
                "publish",
                "start",
                "--project-root",
                str(project_root),
                "--task-dir",
                str(project_root / "knowledge/tasks/TASK-2026-1399-missing"),
                "--purpose",
                "Broken publish fixture.",
            )

            self.assertEqual(result.returncode, 2)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["command"], "workflow")
            self.assertEqual(payload["action"], "start")
            self.assertEqual(payload["outcome"], "failed")
            self.assertEqual(payload["branch_action"], "failed")

    def test_borrowings_status_reports_missing_checkout_without_network(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))

            result, payload = self.run_cli_json(
                "borrowings",
                "status",
                "--project-root",
                str(project_root),
                "--source",
                "grace",
            )

            self.assertEqual(result.returncode, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "borrowings status")
            self.assertEqual(payload["checkout_state"], "missing")
            self.assertEqual(payload["pinned_revision"], "841337377254b205c55e77e7c8d963d1e688170a")
            self.assertEqual(payload["warnings"][0]["key"], "checkout")

    def test_module_find_routes_to_module_core_query_runtime(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            module_dir = project_root / "knowledge/modules/M-ALPHA-alpha"
            module_dir.mkdir(parents=True, exist_ok=True)
            (module_dir / "verification.md").write_text(
                (
                    "# Модульная верификация `M-ALPHA`\n\n"
                    "## Паспорт\n\n"
                    "| Поле | Значение |\n"
                    "|------|----------|\n"
                    "| Модуль | `M-ALPHA` |\n"
                    "| Ссылка верификации | `knowledge/modules/M-ALPHA-alpha/verification.md` |\n"
                    "| Статус готовности | `ready` |\n"
                    "| Дата обновления | `2026-04-20` |\n\n"
                    "## Канонические проверки\n\n"
                    "| ID проверки | Гейт | Тип | Команда | Блокирует | Назначение |\n"
                    "|------------|------|-----|---------|------------|------------|\n"
                    "| `CHK-01` | `writer` | `command` | `python3 -m unittest tests/test_alpha.py` | `да` | Writer path. |\n"
                    "| `CHK-02` | `task-followup` | `artifact-check` | `—` | `нет` | Follow-up. |\n\n"
                    "## Доказательства\n\n"
                    "| ID доказательства | Тип | Значение | Якорь | Заметки |\n"
                    "|------------------|-----|----------|-------|---------|\n"
                    "| `EVD-01` | `test-file` | `tests/test_alpha.py` | `BLOCK_ALPHA` | Test file. |\n"
                    "| `EVD-02` | `log-marker` | `[Alpha][FAIL]` | `BLOCK_ALPHA` | Marker. |\n\n"
                    "## Сценарии\n\n"
                    "| ID сценария | Тип | Описание | Обязательные проверки | Обязательные доказательства | Блокирует |\n"
                    "|-------------|-----|----------|-----------------------|--------------------------|------------|\n"
                    "| `SCN-01` | `success` | Success path. | `CHK-01` | `EVD-01` | `да` |\n"
                    "| `SCN-02` | `observability` | Marker path. | `CHK-01, CHK-02` | `EVD-01, EVD-02` | `да` |\n\n"
                    "## Ручной остаток\n\n"
                    "| ID риска | Применимость | Причина | Действие контроллера |\n"
                    "|----------|--------------|---------|----------------------|\n"
                    "| `RISK-01` | `task-followup` | Follow-up не должен блокировать writer-pass. | `Поднять в task-local matrix.` |\n"
                ),
                encoding="utf-8",
            )
            tests_dir = project_root / "tests"
            tests_dir.mkdir(exist_ok=True)
            (tests_dir / "test_alpha.py").write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")

            result, payload = self.run_cli_json(
                "module",
                "find",
                "--project-root",
                str(project_root),
                "M-ALPHA",
            )

            self.assertEqual(result.returncode, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "module find")
            self.assertEqual(payload["count"], 1)
            self.assertEqual(payload["items"][0]["module_id"], "M-ALPHA")

    def test_help_surface_uses_canonical_command_name_for_all_entrypoints(self) -> None:
        env = dict(os.environ)
        pythonpath_parts = [str(ROOT / "scripts")]
        existing_pythonpath = env.get("PYTHONPATH")
        if existing_pythonpath:
            pythonpath_parts.append(existing_pythonpath)
        env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)

        script_help = self.run_cli("--help", env=env)
        module_help = subprocess.run(
            [sys.executable, "-m", "task_knowledge", "--help"],
            capture_output=True,
            text=True,
            check=False,
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
            cwd=ROOT,
            env=env,
        )

        self.assertEqual(script_help.returncode, 0)
        self.assertEqual(module_help.returncode, 0)
        self.assertIn("usage: task-knowledge", script_help.stdout)
        self.assertIn("usage: task-knowledge", module_help.stdout)
        self.assertNotIn("task_knowledge_cli.py", script_help.stdout)
        self.assertNotIn("__main__.py", module_help.stdout)

    def test_module_show_text_can_render_relations_section(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            alpha_dir = project_root / "knowledge/modules/M-ALPHA-alpha"
            beta_dir = project_root / "knowledge/modules/M-BETA-beta"
            alpha_dir.mkdir(parents=True, exist_ok=True)
            beta_dir.mkdir(parents=True, exist_ok=True)

            verification_text = (
                "# Модульная верификация `{module_id}`\n\n"
                "## Паспорт\n\n"
                "| Поле | Значение |\n"
                "|------|----------|\n"
                "| Модуль | `{module_id}` |\n"
                "| Ссылка верификации | `knowledge/modules/{module_id}-{slug}/verification.md` |\n"
                "| Статус готовности | `ready` |\n"
                "| Дата обновления | `2026-04-20` |\n\n"
                "## Канонические проверки\n\n"
                "| ID проверки | Гейт | Тип | Команда | Блокирует | Назначение |\n"
                "|------------|------|-----|---------|------------|------------|\n"
                "| `CHK-01` | `writer` | `command` | `python3 -m unittest tests/test_{slug}.py` | `да` | Writer path. |\n"
                "| `CHK-02` | `task-followup` | `artifact-check` | `—` | `нет` | Follow-up. |\n\n"
                "## Доказательства\n\n"
                "| ID доказательства | Тип | Значение | Якорь | Заметки |\n"
                "|------------------|-----|----------|-------|---------|\n"
                "| `EVD-01` | `test-file` | `tests/test_{slug}.py` | `BLOCK_{module_id}` | Test file. |\n"
                "| `EVD-02` | `log-marker` | `[Domain][{module_id}][FAIL]` | `BLOCK_{module_id}` | Marker. |\n\n"
                "## Сценарии\n\n"
                "| ID сценария | Тип | Описание | Обязательные проверки | Обязательные доказательства | Блокирует |\n"
                "|-------------|-----|----------|-----------------------|--------------------------|------------|\n"
                "| `SCN-01` | `success` | Success path. | `CHK-01` | `EVD-01` | `да` |\n"
                "| `SCN-02` | `observability` | Marker path. | `CHK-01, CHK-02` | `EVD-01, EVD-02` | `да` |\n\n"
                "## Ручной остаток\n\n"
                "| ID риска | Применимость | Причина | Действие контроллера |\n"
                "|----------|--------------|---------|----------------------|\n"
                "| `RISK-01` | `task-followup` | Follow-up не должен блокировать writer-pass. | `Поднять в task-local matrix.` |\n"
            )
            alpha_verification = verification_text.format(module_id="M-ALPHA", slug="alpha")
            beta_verification = verification_text.format(module_id="M-BETA", slug="beta")
            (alpha_dir / "verification.md").write_text(alpha_verification, encoding="utf-8")
            (beta_dir / "verification.md").write_text(beta_verification, encoding="utf-8")

            alpha_passport = (
                "# Модульный паспорт `M-ALPHA`\n\n"
                "## Паспорт\n\n"
                "| Поле | Значение |\n"
                "|------|----------|\n"
                "| Модуль | `M-ALPHA` |\n"
                "| Слаг | `alpha` |\n"
                "| Название | `Module M-ALPHA` |\n"
                "| Краткое назначение | `Shared passport truth for governed module.` |\n"
                "| Ссылка верификации | `knowledge/modules/M-ALPHA-alpha/verification.md` |\n"
                "| Ссылка file-local policy | `—` |\n"
                "| Статус готовности исполнения | `ready` |\n"
                "| Краткая сводка готовности | `Writer-level readiness вычисляется через verification.md.` |\n"
                "| Задача происхождения | `TASK-2026-0024.2` |\n"
                "| Последняя задача обновления | `TASK-2026-0024.3` |\n"
                "| Дата обновления | `2026-04-21` |\n\n"
                "## Назначение и границы\n\n"
                "Этот passport хранит shared/public truth и owned surface.\n\n"
                "## Управляемая поверхность\n\n"
                "| Тип | Путь | Роль | Причина владения |\n"
                "|-----|------|------|------------------|\n"
                "| `runtime` | `scripts/alpha.py` | `entrypoint` | Runtime path governed module. |\n"
                "| `test` | `tests/test_alpha.py` | `verification` | Test path reused by verification runtime. |\n\n"
                "## Публичные контракты\n\n"
                "| Контракт | Форма | Ссылка/маркер | Для кого |\n"
                "|----------|-------|---------------|----------|\n"
                "| `CLI M-ALPHA` | `command-surface` | `task-knowledge module show M-ALPHA` | `operator` |\n"
                "| `Failure marker` | `log-marker` | `[Domain][M-ALPHA][FAIL]` | `controller` |\n\n"
                "## Связи\n\n"
                "| Тип связи | Цель | Статус | Заметка |\n"
                "|-----------|------|--------|---------|\n"
                "| `depends_on` | `M-BETA` | `required` | Writer path depends on beta. |\n"
            )
            beta_passport = (
                "# Модульный паспорт `M-BETA`\n\n"
                "## Паспорт\n\n"
                "| Поле | Значение |\n"
                "|------|----------|\n"
                "| Модуль | `M-BETA` |\n"
                "| Слаг | `beta` |\n"
                "| Название | `Module M-BETA` |\n"
                "| Краткое назначение | `Shared passport truth for governed module.` |\n"
                "| Ссылка верификации | `knowledge/modules/M-BETA-beta/verification.md` |\n"
                "| Ссылка file-local policy | `—` |\n"
                "| Статус готовности исполнения | `ready` |\n"
                "| Краткая сводка готовности | `Writer-level readiness вычисляется через verification.md.` |\n"
                "| Задача происхождения | `TASK-2026-0024.2` |\n"
                "| Последняя задача обновления | `TASK-2026-0024.3` |\n"
                "| Дата обновления | `2026-04-21` |\n\n"
                "## Назначение и границы\n\n"
                "Этот passport хранит shared/public truth и owned surface.\n\n"
                "## Управляемая поверхность\n\n"
                "| Тип | Путь | Роль | Причина владения |\n"
                "|-----|------|------|------------------|\n"
                "| `runtime` | `scripts/beta.py` | `entrypoint` | Runtime path governed module. |\n"
                "| `test` | `tests/test_beta.py` | `verification` | Test path reused by verification runtime. |\n\n"
                "## Публичные контракты\n\n"
                "| Контракт | Форма | Ссылка/маркер | Для кого |\n"
                "|----------|-------|---------------|----------|\n"
                "| `CLI M-BETA` | `command-surface` | `task-knowledge module show M-BETA` | `operator` |\n"
                "| `Failure marker` | `log-marker` | `[Domain][M-BETA][FAIL]` | `controller` |\n\n"
                "## Связи\n\n"
                "| Тип связи | Цель | Статус | Заметка |\n"
                "|-----------|------|--------|---------|\n"
            )
            (alpha_dir / "module.md").write_text(alpha_passport, encoding="utf-8")
            (beta_dir / "module.md").write_text(beta_passport, encoding="utf-8")

            registry_path = project_root / "knowledge/modules/registry.md"
            registry_path.parent.mkdir(parents=True, exist_ok=True)
            registry_path.write_text(
                (
                    "# Реестр governed modules\n\n"
                    "## Таблица\n\n"
                    "| MODULE-ID | Slug | Source State | Readiness | Паспорт | Верификация | File Policy | Каталог | Краткое назначение |\n"
                    "|-----------|------|--------------|-----------|---------|-------------|-------------|---------|--------------------|\n"
                    "| `M-ALPHA` | `alpha` | `passport_ready` | `ready` | `knowledge/modules/M-ALPHA-alpha/module.md` | `knowledge/modules/M-ALPHA-alpha/verification.md` | `—` | `knowledge/modules/M-ALPHA-alpha/` | Shared passport truth for governed module. |\n"
                    "| `M-BETA` | `beta` | `passport_ready` | `ready` | `knowledge/modules/M-BETA-beta/module.md` | `knowledge/modules/M-BETA-beta/verification.md` | `—` | `knowledge/modules/M-BETA-beta/` | Shared passport truth for governed module. |\n"
                ),
                encoding="utf-8",
            )

            scripts_dir = project_root / "scripts"
            tests_dir = project_root / "tests"
            scripts_dir.mkdir(exist_ok=True)
            tests_dir.mkdir(exist_ok=True)
            (scripts_dir / "alpha.py").write_text("def run():\n    return True\n", encoding="utf-8")
            (scripts_dir / "beta.py").write_text("def run():\n    return True\n", encoding="utf-8")
            (tests_dir / "test_alpha.py").write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")
            (tests_dir / "test_beta.py").write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")

            result = self.run_cli(
                "module",
                "show",
                "--project-root",
                str(project_root),
                "M-ALPHA",
                "--with",
                "relations",
            )

            self.assertEqual(result.returncode, 0)
            self.assertIn("Relations", result.stdout)
            self.assertIn("depends_on_total=1", result.stdout)
            self.assertIn("- M-BETA | type=depends_on | status=required", result.stdout)
            self.assertIn("used_by=—", result.stdout)

    def test_file_show_routes_to_module_core_query_runtime(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            module_dir = project_root / "knowledge/modules/M-ALPHA-alpha"
            module_dir.mkdir(parents=True, exist_ok=True)
            (module_dir / "verification.md").write_text(
                (
                    "# Модульная верификация `M-ALPHA`\n\n"
                    "## Паспорт\n\n"
                    "| Поле | Значение |\n"
                    "|------|----------|\n"
                    "| Модуль | `M-ALPHA` |\n"
                    "| Ссылка верификации | `knowledge/modules/M-ALPHA-alpha/verification.md` |\n"
                    "| Статус готовности | `ready` |\n"
                    "| Дата обновления | `2026-04-20` |\n\n"
                    "## Канонические проверки\n\n"
                    "| ID проверки | Гейт | Тип | Команда | Блокирует | Назначение |\n"
                    "|------------|------|-----|---------|------------|------------|\n"
                    "| `CHK-01` | `writer` | `command` | `python3 -m unittest tests/test_alpha.py` | `да` | Writer path. |\n"
                    "| `CHK-02` | `task-followup` | `artifact-check` | `—` | `нет` | Follow-up. |\n\n"
                    "## Доказательства\n\n"
                    "| ID доказательства | Тип | Значение | Якорь | Заметки |\n"
                    "|------------------|-----|----------|-------|---------|\n"
                    "| `EVD-01` | `test-file` | `tests/test_alpha.py` | `BLOCK_ALPHA` | Test file. |\n"
                    "| `EVD-02` | `log-marker` | `[Alpha][FAIL]` | `BLOCK_ALPHA` | Marker. |\n\n"
                    "## Сценарии\n\n"
                    "| ID сценария | Тип | Описание | Обязательные проверки | Обязательные доказательства | Блокирует |\n"
                    "|-------------|-----|----------|-----------------------|--------------------------|------------|\n"
                    "| `SCN-01` | `success` | Success path. | `CHK-01` | `EVD-01` | `да` |\n"
                    "| `SCN-02` | `observability` | Marker path. | `CHK-01, CHK-02` | `EVD-01, EVD-02` | `да` |\n\n"
                    "## Ручной остаток\n\n"
                    "| ID риска | Применимость | Причина | Действие контроллера |\n"
                    "|----------|--------------|---------|----------------------|\n"
                    "| `RISK-01` | `task-followup` | Follow-up не должен блокировать writer-pass. | `Поднять в task-local matrix.` |\n"
                ),
                encoding="utf-8",
            )
            tests_dir = project_root / "tests"
            tests_dir.mkdir(exist_ok=True)
            (tests_dir / "test_alpha.py").write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")

            result, payload = self.run_cli_json(
                "file",
                "show",
                "--project-root",
                str(project_root),
                "tests/test_alpha.py",
            )

            self.assertEqual(result.returncode, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "file show")
            self.assertEqual(payload["file"]["governance_state"], "verification_evidence_only")
            self.assertEqual(payload["file"]["owner_modules"][0]["module_id"], "M-ALPHA")

    def test_file_show_text_renders_contracts_and_blocks_sections(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            module_dir = project_root / "knowledge/modules/M-ALPHA-alpha"
            module_dir.mkdir(parents=True, exist_ok=True)
            (module_dir / "verification.md").write_text(
                (
                    "# Модульная верификация `M-ALPHA`\n\n"
                    "## Паспорт\n\n"
                    "| Поле | Значение |\n"
                    "|------|----------|\n"
                    "| Модуль | `M-ALPHA` |\n"
                    "| Ссылка верификации | `knowledge/modules/M-ALPHA-alpha/verification.md` |\n"
                    "| Статус готовности | `ready` |\n"
                    "| Дата обновления | `2026-04-20` |\n\n"
                    "## Канонические проверки\n\n"
                    "| ID проверки | Гейт | Тип | Команда | Блокирует | Назначение |\n"
                    "|------------|------|-----|---------|------------|------------|\n"
                    "| `CHK-01` | `writer` | `command` | `python3 -m unittest tests/test_alpha.py` | `да` | Writer path. |\n"
                    "| `CHK-02` | `task-followup` | `artifact-check` | `—` | `нет` | Follow-up. |\n\n"
                    "## Доказательства\n\n"
                    "| ID доказательства | Тип | Значение | Якорь | Заметки |\n"
                    "|------------------|-----|----------|-------|---------|\n"
                    "| `EVD-01` | `test-file` | `tests/test_alpha.py` | `BLOCK_ALPHA` | Test file. |\n"
                    "| `EVD-02` | `log-marker` | `[Alpha][FAIL]` | `BLOCK_ALPHA` | Marker. |\n\n"
                    "## Сценарии\n\n"
                    "| ID сценария | Тип | Описание | Обязательные проверки | Обязательные доказательства | Блокирует |\n"
                    "|-------------|-----|----------|-----------------------|--------------------------|------------|\n"
                    "| `SCN-01` | `success` | Success path. | `CHK-01` | `EVD-01` | `да` |\n"
                    "| `SCN-02` | `observability` | Marker path. | `CHK-01, CHK-02` | `EVD-01, EVD-02` | `да` |\n\n"
                    "## Ручной остаток\n\n"
                    "| ID риска | Применимость | Причина | Действие контроллера |\n"
                    "|----------|--------------|---------|----------------------|\n"
                    "| `RISK-01` | `task-followup` | Follow-up не должен блокировать writer-pass. | `Поднять в task-local matrix.` |\n"
                ),
                encoding="utf-8",
            )
            (module_dir / "module.md").write_text(
                (
                    "# Модульный паспорт `M-ALPHA`\n\n"
                    "## Паспорт\n\n"
                    "| Поле | Значение |\n"
                    "|------|----------|\n"
                    "| Модуль | `M-ALPHA` |\n"
                    "| Слаг | `alpha` |\n"
                    "| Название | `Module M-ALPHA` |\n"
                    "| Краткое назначение | `Shared passport truth for governed module.` |\n"
                    "| Ссылка верификации | `knowledge/modules/M-ALPHA-alpha/verification.md` |\n"
                    "| Ссылка file-local policy | `knowledge/modules/M-ALPHA-alpha/file-local-policy.md` |\n"
                    "| Статус готовности исполнения | `ready` |\n"
                    "| Краткая сводка готовности | `Writer-level readiness вычисляется через verification.md.` |\n"
                    "| Задача происхождения | `TASK-2026-0024.2` |\n"
                    "| Последняя задача обновления | `TASK-2026-0024.4` |\n"
                    "| Дата обновления | `2026-04-21` |\n\n"
                    "## Назначение и границы\n\n"
                    "Этот passport хранит shared/public truth и owned surface.\n\n"
                    "## Управляемая поверхность\n\n"
                    "| Тип | Путь | Роль | Причина владения |\n"
                    "|-----|------|------|------------------|\n"
                    "| `runtime` | `scripts/alpha.py` | `entrypoint` | Runtime path governed module. |\n"
                    "| `test` | `tests/test_alpha.py` | `verification` | Test path reused by verification runtime. |\n\n"
                    "## Публичные контракты\n\n"
                    "| Контракт | Форма | Ссылка/маркер | Для кого |\n"
                    "|----------|-------|---------------|----------|\n"
                    "| `CLI M-ALPHA` | `command-surface` | `task-knowledge module show M-ALPHA` | `operator` |\n"
                    "| `Failure marker` | `log-marker` | `[Domain][M-ALPHA][FAIL]` | `controller` |\n\n"
                    "## Связи\n\n"
                    "| Тип связи | Цель | Статус | Заметка |\n"
                    "|-----------|------|--------|---------|\n"
                ),
                encoding="utf-8",
            )
            (module_dir / "file-local-policy.md").write_text(
                (
                    "# File-local policy\n\n"
                    "## Hot spots\n\n"
                    "| Путь | Режим | Разрешённые markers | Обязательные blocks | Назначение |\n"
                    "|------|-------|---------------------|---------------------|------------|\n"
                    "| `scripts/alpha.py` | `required` | `MODULE_CONTRACT, MODULE_MAP` | `BLOCK_VALIDATE_INPUT` | Runtime hot spot. |\n"
                ),
                encoding="utf-8",
            )
            registry_path = project_root / "knowledge/modules/registry.md"
            registry_path.parent.mkdir(parents=True, exist_ok=True)
            registry_path.write_text(
                (
                    "# Реестр governed modules\n\n"
                    "## Таблица\n\n"
                    "| MODULE-ID | Slug | Source State | Readiness | Паспорт | Верификация | File Policy | Каталог | Краткое назначение |\n"
                    "|-----------|------|--------------|-----------|---------|-------------|-------------|---------|--------------------|\n"
                    "| `M-ALPHA` | `alpha` | `passport_ready` | `ready` | `knowledge/modules/M-ALPHA-alpha/module.md` | `knowledge/modules/M-ALPHA-alpha/verification.md` | `knowledge/modules/M-ALPHA-alpha/file-local-policy.md` | `knowledge/modules/M-ALPHA-alpha/` | Shared passport truth for governed module. |\n"
                ),
                encoding="utf-8",
            )
            scripts_dir = project_root / "scripts"
            tests_dir = project_root / "tests"
            scripts_dir.mkdir(exist_ok=True)
            tests_dir.mkdir(exist_ok=True)
            (scripts_dir / "alpha.py").write_text(
                (
                    "# MODULE_CONTRACT:BEGIN\n"
                    "# body\n"
                    "# MODULE_CONTRACT:END\n"
                    "# BLOCK_VALIDATE_INPUT:BEGIN\n"
                    "def run():\n"
                    "    return True\n"
                    "# BLOCK_VALIDATE_INPUT:END\n"
                ),
                encoding="utf-8",
            )
            (tests_dir / "test_alpha.py").write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")

            result = self.run_cli(
                "file",
                "show",
                "--project-root",
                str(project_root),
                "scripts/alpha.py",
                "--contracts",
                "--blocks",
            )
            _, payload_plain = self.run_cli_json(
                "file",
                "show",
                "--project-root",
                str(project_root),
                "scripts/alpha.py",
            )
            _, payload_with_flags = self.run_cli_json(
                "file",
                "show",
                "--project-root",
                str(project_root),
                "scripts/alpha.py",
                "--contracts",
                "--blocks",
            )

            self.assertEqual(result.returncode, 0)
            self.assertIn("Contract markers", result.stdout)
            self.assertIn("MODULE_CONTRACT", result.stdout)
            self.assertIn("Blocks", result.stdout)
            self.assertIn("BLOCK_VALIDATE_INPUT", result.stdout)
            self.assertEqual(payload_plain["file"]["contract_markers"], payload_with_flags["file"]["contract_markers"])
            self.assertEqual(payload_plain["file"]["blocks"], payload_with_flags["file"]["blocks"])

    def test_workflow_backfill_routes_to_legacy_upgrade_runtime(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.write_registry(project_root)
            task_dir = project_root / "knowledge/tasks/TASK-2026-1302-legacy"
            self.write_task(
                task_dir,
                task_id="TASK-2026-1302",
                slug="legacy",
                branch="main",
                human_description="Legacy task.",
            )
            registry_path = project_root / "knowledge/tasks/registry.md"
            registry_path.write_text(
                registry_path.read_text(encoding="utf-8")
                + "| `TASK-2026-1302` | `—` | `в работе` | `средний` | `main` | `knowledge/tasks/TASK-2026-1302-legacy/` | Legacy task. |\n",
                encoding="utf-8",
            )

            result, payload = self.run_cli_json(
                "workflow",
                "backfill",
                "--project-root",
                str(project_root),
                "--task-dir",
                str(task_dir),
                "--summary",
                "Backfilled legacy task.",
            )

            self.assertEqual(result.returncode, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["action"], "backfill")
            self.assertEqual(payload["task_class"], "active")
            self.assertEqual(payload["backfill_status"], "compatibility-backfilled")
            self.assertTrue((task_dir / "artifacts/migration/task-centric-knowledge-upgrade.md").exists())
