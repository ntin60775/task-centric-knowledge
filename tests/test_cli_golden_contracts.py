from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from task_workflow_testlib import ROOT, SUBPROCESS_TIMEOUT_SECONDS, TempRepoCase, git


CLI_SCRIPT = ROOT / "scripts" / "task_knowledge_cli.py"
GOLDEN_DIR = ROOT / "tests" / "golden"


class CliGoldenContractTests(TempRepoCase):
    def run_cli_json(self, project_root: Path, *args: str) -> dict[str, object]:
        result = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), "--json", *args],
            capture_output=True,
            text=True,
            check=False,
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        return self._normalize_payload(payload, project_root)

    def assert_matches_golden(self, fixture_name: str, payload: dict[str, object]) -> None:
        expected = json.loads((GOLDEN_DIR / f"{fixture_name}.json").read_text(encoding="utf-8"))
        self.assertEqual(
            expected,
            payload,
            msg=json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        )

    def _normalize_payload(self, value: object, project_root: Path) -> object:
        if isinstance(value, dict):
            return {key: self._normalize_payload(item, project_root) for key, item in value.items()}
        if isinstance(value, list):
            return [self._normalize_payload(item, project_root) for item in value]
        if isinstance(value, str):
            return value.replace(str(project_root.resolve()), "<PROJECT_ROOT>")
        return value

    def prepare_task_golden_project(self, project_root: Path) -> None:
        self.write_registry(project_root)
        task_dir = project_root / "knowledge/tasks/TASK-2026-1400-golden-contract"
        self.write_task(
            task_dir,
            task_id="TASK-2026-1400",
            slug="golden-contract",
            branch="task/task-2026-1400-golden-contract",
            human_description="Golden contract CLI task.",
            goal="Проверить стабильность JSON-контракта CLI.",
        )
        registry_path = project_root / "knowledge/tasks/registry.md"
        registry_path.write_text(
            registry_path.read_text(encoding="utf-8")
            + "| `TASK-2026-1400` | `—` | `в работе` | `средний` | `task/task-2026-1400-golden-contract` | `knowledge/tasks/TASK-2026-1400-golden-contract/` | Golden contract CLI task. |\n",
            encoding="utf-8",
        )
        git(project_root, "checkout", "-b", "task/task-2026-1400-golden-contract")
        git(project_root, "add", ".")
        git(project_root, "commit", "-m", "golden fixture")

    def prepare_module_golden_project(self, project_root: Path) -> None:
        module_dir = project_root / "knowledge/modules/M-GOLDEN-golden"
        module_dir.mkdir(parents=True, exist_ok=True)
        (module_dir / "verification.md").write_text(
            textwrap.dedent(
                """\
                # Модульная верификация `M-GOLDEN`

                ## Паспорт

                | Поле | Значение |
                |------|----------|
                | Модуль | `M-GOLDEN` |
                | Ссылка верификации | `knowledge/modules/M-GOLDEN-golden/verification.md` |
                | Статус готовности | `ready` |
                | Дата обновления | `2026-04-20` |

                ## Канонические проверки

                | ID проверки | Гейт | Тип | Команда | Блокирует | Назначение |
                |------------|------|-----|---------|------------|------------|
                | `CHK-01` | `writer` | `command` | `python3 -m unittest tests/test_golden.py` | `да` | Writer path. |

                ## Доказательства

                | ID доказательства | Тип | Значение | Якорь | Заметки |
                |------------------|-----|----------|-------|---------|
                | `EVD-01` | `test-file` | `tests/test_golden.py` | `BLOCK_GOLDEN` | Test file. |

                ## Сценарии

                | ID сценария | Тип | Описание | Обязательные проверки | Обязательные доказательства | Блокирует |
                |-------------|-----|----------|-----------------------|--------------------------|------------|
                | `SCN-01` | `success` | Success path. | `CHK-01` | `EVD-01` | `да` |

                ## Ручной остаток

                | ID риска | Применимость | Причина | Действие контроллера |
                |----------|--------------|---------|----------------------|
                | `RISK-01` | `нет` | Нет ручного остатка. | `Не требуется.` |
                """
            ),
            encoding="utf-8",
        )
        tests_dir = project_root / "tests"
        tests_dir.mkdir(exist_ok=True)
        (tests_dir / "test_golden.py").write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")

    def test_task_cli_json_golden_contracts(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.prepare_task_golden_project(project_root)

            self.assert_matches_golden(
                "task_status",
                self.run_cli_json(project_root, "task", "status", "--project-root", str(project_root)),
            )
            self.assert_matches_golden(
                "task_current",
                self.run_cli_json(project_root, "task", "current", "--project-root", str(project_root)),
            )
            self.assert_matches_golden(
                "task_show",
                self.run_cli_json(project_root, "task", "show", "--project-root", str(project_root), "TASK-2026-1400"),
            )

    def test_module_and_file_cli_json_golden_contracts(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self.prepare_module_golden_project(project_root)

            self.assert_matches_golden(
                "module_find",
                self.run_cli_json(project_root, "module", "find", "--project-root", str(project_root), "golden"),
            )
            self.assert_matches_golden(
                "module_show",
                self.run_cli_json(
                    project_root,
                    "module",
                    "show",
                    "--project-root",
                    str(project_root),
                    "M-GOLDEN",
                    "--with",
                    "verification",
                ),
            )
            self.assert_matches_golden(
                "file_show",
                self.run_cli_json(project_root, "file", "show", "--project-root", str(project_root), "tests/test_golden.py"),
            )


if __name__ == "__main__":
    import unittest

    unittest.main()
