from __future__ import annotations

import argparse
import sys
import textwrap
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

SCRIPTS_DIR = TESTS_DIR.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from module_core_runtime.query_cli import dispatch_file, dispatch_module, format_module_show_payload
from task_workflow_testlib import TempRepoCase


def _verification_text(
    module_id: str,
    *,
    slug: str,
    declared_status: str = "ready",
    writer_gate: str = "writer",
) -> str:
    return textwrap.dedent(
        f"""\
        # Модульная верификация `{module_id}`

        ## Паспорт

        | Поле | Значение |
        |------|----------|
        | Модуль | `{module_id}` |
        | Ссылка верификации | `knowledge/modules/{module_id}-{slug}/verification.md` |
        | Статус готовности | `{declared_status}` |
        | Дата обновления | `2026-04-20` |

        ## Канонические проверки

        | ID проверки | Гейт | Тип | Команда | Блокирует | Назначение |
        |------------|------|-----|---------|------------|------------|
        | `CHK-01` | `{writer_gate}` | `command` | `python3 -m unittest tests/test_{slug}.py` | `да` | Writer-level smoke path. |
        | `CHK-02` | `task-followup` | `artifact-check` | `—` | `нет` | Follow-up наблюдаемость для `1С/BSL`. |

        ## Доказательства

        | ID доказательства | Тип | Значение | Якорь | Заметки |
        |------------------|-----|----------|-------|---------|
        | `EVD-01` | `test-file` | `tests/test_{slug}.py` | `BLOCK_{module_id}` | Основной test file. |
        | `EVD-02` | `log-marker` | `[Domain][{module_id}][FAIL]` | `BLOCK_{module_id}` | Marker для отказа. |

        ## Сценарии

        | ID сценария | Тип | Описание | Обязательные проверки | Обязательные доказательства | Блокирует |
        |-------------|-----|----------|-----------------------|--------------------------|------------|
        | `SCN-01` | `success` | Writer path проходит smoke-check. | `CHK-01` | `EVD-01` | `да` |
        | `SCN-02` | `observability` | Ошибка остаётся наблюдаемой. | `CHK-01, CHK-02` | `EVD-01, EVD-02` | `да` |

        ## Ручной остаток

        | ID риска | Применимость | Причина | Действие контроллера |
        |----------|--------------|---------|----------------------|
        | `RISK-01` | `task-followup` | Интеграционный follow-up не должен блокировать writer-pass. | `Поднять в task-local matrix.` |
        """
    )


def _module_text(
    module_id: str,
    *,
    slug: str,
    purpose_summary: str = "Shared passport truth for governed module.",
    readiness_status: str = "ready",
    readiness_summary: str = "Writer-level readiness вычисляется через verification.md.",
    file_policy_ref: str = "—",
    source_task: str = "TASK-2026-0024.2",
    update_task: str = "TASK-2026-0024.2",
    relation_rows: str = "",
) -> str:
    relation_block = textwrap.indent(relation_rows, "        ") if relation_rows else ""
    return textwrap.dedent(
        f"""\
        # Модульный паспорт `{module_id}`

        ## Паспорт

        | Поле | Значение |
        |------|----------|
        | Модуль | `{module_id}` |
        | Слаг | `{slug}` |
        | Название | `Module {module_id}` |
        | Краткое назначение | `{purpose_summary}` |
        | Ссылка верификации | `knowledge/modules/{module_id}-{slug}/verification.md` |
        | Ссылка file-local policy | `{file_policy_ref}` |
        | Статус готовности исполнения | `{readiness_status}` |
        | Краткая сводка готовности | `{readiness_summary}` |
        | Задача происхождения | `{source_task}` |
        | Последняя задача обновления | `{update_task}` |
        | Дата обновления | `2026-04-21` |

        ## Назначение и границы

        Этот passport хранит shared/public truth и owned surface.

        ## Управляемая поверхность

        | Тип | Путь | Роль | Причина владения |
        |-----|------|------|------------------|
        | `runtime` | `scripts/{slug}.py` | `entrypoint` | Runtime path governed module. |
        | `test` | `tests/test_{slug}.py` | `verification` | Test path reused by verification runtime. |

        ## Публичные контракты

        | Контракт | Форма | Ссылка/маркер | Для кого |
        |----------|-------|---------------|----------|
        | `CLI {module_id}` | `command-surface` | `task-knowledge module show {module_id}` | `operator` |
        | `Failure marker` | `log-marker` | `[Domain][{module_id}][FAIL]` | `controller` |

        ## Связи

        | Тип связи | Цель | Статус | Заметка |
        |-----------|------|--------|---------|
{relation_block}
        """
    )


def _registry_text(*rows: str) -> str:
    body = "\n".join(rows) if rows else ""
    return textwrap.dedent(
        f"""\
        # Реестр governed modules

        ## Таблица

        | MODULE-ID | Slug | Source State | Readiness | Паспорт | Верификация | File Policy | Каталог | Краткое назначение |
        |-----------|------|--------------|-----------|---------|-------------|-------------|---------|--------------------|
        {body}
        """
    )


def _file_local_policy_text(*rows: str) -> str:
    body = "\n".join(rows) if rows else ""
    return textwrap.dedent(
        f"""\
        # File-local policy

        ## Hot spots

        | Путь | Режим | Разрешённые markers | Обязательные blocks | Назначение |
        |------|-------|---------------------|---------------------|------------|
        {body}
        """
    )


class ModuleQueryRuntimeTests(TempRepoCase):
    def _write_module(
        self,
        project_root: Path,
        module_id: str,
        slug: str,
        *,
        verification_text: str | None = None,
        passport_text: str | None = None,
        file_policy_text: str | None = None,
    ) -> None:
        module_dir = project_root / f"knowledge/modules/{module_id}-{slug}"
        module_dir.mkdir(parents=True, exist_ok=True)
        (module_dir / "verification.md").write_text(
            verification_text or _verification_text(module_id, slug=slug),
            encoding="utf-8",
        )
        if passport_text is not None:
            (module_dir / "module.md").write_text(passport_text, encoding="utf-8")
            scripts_dir = project_root / "scripts"
            scripts_dir.mkdir(exist_ok=True)
            (scripts_dir / f"{slug}.py").write_text("def run():\n    return True\n", encoding="utf-8")
        if file_policy_text is not None:
            (module_dir / "file-local-policy.md").write_text(file_policy_text, encoding="utf-8")
        tests_dir = project_root / "tests"
        tests_dir.mkdir(exist_ok=True)
        (tests_dir / f"test_{slug}.py").write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")

    def _write_registry(self, project_root: Path, *rows: str) -> None:
        registry_path = project_root / "knowledge/modules/registry.md"
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text(_registry_text(*rows), encoding="utf-8")

    def _write_passport_only_module(self, project_root: Path, module_id: str, slug: str) -> None:
        module_dir = project_root / f"knowledge/modules/{module_id}-{slug}"
        module_dir.mkdir(parents=True, exist_ok=True)
        (module_dir / "module.md").write_text(_module_text(module_id, slug=slug), encoding="utf-8")
        scripts_dir = project_root / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        (scripts_dir / f"{slug}.py").write_text("def run():\n    return True\n", encoding="utf-8")
        tests_dir = project_root / "tests"
        tests_dir.mkdir(exist_ok=True)
        (tests_dir / f"test_{slug}.py").write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")

    def test_module_find_filters_by_readiness_and_source_state(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self._write_module(project_root, "M-ALPHA", "alpha")
            self._write_module(
                project_root,
                "M-BETA",
                "beta",
                verification_text=_verification_text(
                    "M-BETA",
                    slug="beta",
                    declared_status="partial",
                    writer_gate="task-followup",
                ),
            )

            payload, exit_code = dispatch_module(
                argparse.Namespace(
                    project_root=project_root,
                    module_command="find",
                    query="M-",
                    readiness="ready",
                    source_state="verification_only",
                    limit=10,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 1)
            self.assertEqual(payload["items"][0]["module_id"], "M-ALPHA")
            self.assertEqual(payload["items"][0]["source_state"], "verification_only")
            self.assertIn("module_id", payload["items"][0]["matched_fields"])

    def test_module_show_returns_verification_excerpt_and_partial_rollout_warnings(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self._write_module(project_root, "M-ALPHA", "alpha")

            payload, exit_code = dispatch_module(
                argparse.Namespace(
                    project_root=project_root,
                    module_command="show",
                    selector="M-ALPHA",
                    query=None,
                    readiness=None,
                    source_state=None,
                    limit=20,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            module = payload["module"]
            self.assertEqual(module["module_id"], "M-ALPHA")
            self.assertEqual(module["verification_excerpt"]["readiness_status"], "ready")
            self.assertEqual(module["public_truth"]["passport_ref"], None)
            warning_codes = {item["code"] for item in payload["warnings"]}
            self.assertIn("module_passport_missing", warning_codes)
            self.assertIn("partial_governed_scope", warning_codes)
            self.assertEqual(module["relations"]["status"], "unavailable")
            self.assertIn("relation-truth не может быть собран", module["relations"]["reason"])

    def test_module_show_merges_passport_public_truth_and_marks_passport_ready(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self._write_module(
                project_root,
                "M-ALPHA",
                "alpha",
                passport_text=_module_text(
                    "M-ALPHA",
                    slug="alpha",
                    file_policy_ref="knowledge/modules/M-ALPHA-alpha/file-local-policy.md",
                ),
                file_policy_text=_file_local_policy_text(
                    "| `scripts/alpha.py` | `required` | `MODULE_CONTRACT, MODULE_MAP` | `BLOCK_VALIDATE_INPUT` | Runtime hot spot. |",
                ),
            )
            self._write_registry(
                project_root,
                "| `M-ALPHA` | `alpha` | `passport_ready` | `ready` | `knowledge/modules/M-ALPHA-alpha/module.md` | `knowledge/modules/M-ALPHA-alpha/verification.md` | `knowledge/modules/M-ALPHA-alpha/file-local-policy.md` | `knowledge/modules/M-ALPHA-alpha/` | Shared passport truth for governed module. |",
            )

            payload, exit_code = dispatch_module(
                argparse.Namespace(
                    project_root=project_root,
                    module_command="show",
                    selector="M-ALPHA",
                    query=None,
                    readiness=None,
                    source_state=None,
                    limit=20,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            module = payload["module"]
            self.assertEqual(module["source_state"], "passport_ready")
            self.assertEqual(module["purpose_summary"], "Shared passport truth for governed module.")
            self.assertEqual(
                module["public_truth"]["file_local_policy_ref"],
                "knowledge/modules/M-ALPHA-alpha/file-local-policy.md",
            )
            self.assertEqual(module["public_truth"]["owned_surface"][0]["path_ref"], "scripts/alpha.py")
            self.assertEqual(module["public_truth"]["public_contracts"][0]["contract"], "CLI M-ALPHA")
            warning_codes = {item["code"] for item in payload["warnings"]}
            self.assertNotIn("module_passport_missing", warning_codes)
            self.assertNotIn("module_registry_missing_row", warning_codes)
            self.assertNotIn("file_contract_unavailable", warning_codes)
            self.assertEqual(module["relations"]["status"], "ready")
            self.assertEqual(module["relations"]["summary"]["depends_on_total"], 0)

    def test_module_show_accepts_top_level_makefile_owned_surface(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            passport_text = _module_text("M-ALPHA", slug="alpha").replace(
                "| `runtime` | `scripts/alpha.py` | `entrypoint` | Runtime path governed module. |",
                "| `runtime` | `Makefile` | `build` | Top-level governed file. |",
            )
            self._write_module(
                project_root,
                "M-ALPHA",
                "alpha",
                passport_text=passport_text,
            )
            self._write_registry(
                project_root,
                "| `M-ALPHA` | `alpha` | `passport_ready` | `ready` | `knowledge/modules/M-ALPHA-alpha/module.md` | `knowledge/modules/M-ALPHA-alpha/verification.md` | `—` | `knowledge/modules/M-ALPHA-alpha/` | Shared passport truth for governed module. |",
            )
            (project_root / "Makefile").write_text("all:\n\t@true\n", encoding="utf-8")

            payload, exit_code = dispatch_module(
                argparse.Namespace(
                    project_root=project_root,
                    module_command="show",
                    selector="M-ALPHA",
                    query=None,
                    readiness=None,
                    source_state=None,
                    limit=20,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            module = payload["module"]
            self.assertEqual(module["public_truth"]["owned_surface"][0]["path_ref"], "Makefile")
            self.assertIn("Makefile", module["public_truth"]["governed_files"])
            self.assertIn("Makefile", module["files"]["governed_files"])

    def test_module_show_warns_about_invalid_file_local_policy(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self._write_module(
                project_root,
                "M-ALPHA",
                "alpha",
                passport_text=_module_text(
                    "M-ALPHA",
                    slug="alpha",
                    file_policy_ref="knowledge/modules/M-ALPHA-alpha/file-local-policy.md",
                ),
                file_policy_text=(
                    "# File-local policy\n\n"
                    "## Hot spots\n\n"
                    "| Путь | Режим | Неправильная колонка |\n"
                    "|------|-------|----------------------|\n"
                    "| `scripts/alpha.py` | `required` | `oops` |\n"
                ),
            )
            self._write_registry(
                project_root,
                "| `M-ALPHA` | `alpha` | `passport_ready` | `ready` | `knowledge/modules/M-ALPHA-alpha/module.md` | `knowledge/modules/M-ALPHA-alpha/verification.md` | `knowledge/modules/M-ALPHA-alpha/file-local-policy.md` | `knowledge/modules/M-ALPHA-alpha/` | Shared passport truth for governed module. |",
            )

            payload, exit_code = dispatch_module(
                argparse.Namespace(
                    project_root=project_root,
                    module_command="show",
                    selector="M-ALPHA",
                    query=None,
                    readiness=None,
                    source_state=None,
                    limit=20,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            warning_codes = {item["code"] for item in payload["warnings"]}
            self.assertIn("file_local_policy_invalid", warning_codes)
            self.assertNotIn("file_contract_unavailable", warning_codes)

    def test_module_show_rejects_owned_surface_path_outside_project(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            passport_text = _module_text("M-ALPHA", slug="alpha").replace("scripts/alpha.py", "../outside.py", 1)
            self._write_module(
                project_root,
                "M-ALPHA",
                "alpha",
                passport_text=passport_text,
            )

            payload, exit_code = dispatch_module(
                argparse.Namespace(
                    project_root=project_root,
                    module_command="show",
                    selector="M-ALPHA",
                    query=None,
                    readiness=None,
                    source_state=None,
                    limit=20,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["module"]["source_state"], "verification_only")
            self.assertEqual(payload["module"]["public_truth"]["owned_surface"], [])
            warning_codes = {item["code"] for item in payload["warnings"]}
            self.assertIn("module_passport_invalid", warning_codes)
            self.assertIn("module_passport_missing", warning_codes)

    def test_module_show_warns_when_registry_row_drifted_from_passport(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self._write_module(
                project_root,
                "M-ALPHA",
                "alpha",
                passport_text=_module_text("M-ALPHA", slug="alpha"),
            )
            self._write_registry(
                project_root,
                "| `M-ALPHA` | `alpha` | `verification_only` | `partial` | `knowledge/modules/M-ALPHA-alpha/module.md` | `knowledge/modules/M-ALPHA-alpha/verification.md` | `—` | `knowledge/modules/M-ALPHA-alpha/` | Drifted cache summary. |",
            )

            payload, exit_code = dispatch_module(
                argparse.Namespace(
                    project_root=project_root,
                    module_command="show",
                    selector="M-ALPHA",
                    query=None,
                    readiness=None,
                    source_state=None,
                    limit=20,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            warning_codes = {item["code"] for item in payload["warnings"]}
            self.assertIn("module_registry_drift", warning_codes)

    def test_module_show_blocks_passport_without_verification_file(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self._write_passport_only_module(project_root, "M-ONLY", "only")
            self._write_registry(
                project_root,
                "| `M-ONLY` | `only` | `partial` | `blocked` | `knowledge/modules/M-ONLY-only/module.md` | `knowledge/modules/M-ONLY-only/verification.md` | `—` | `knowledge/modules/M-ONLY-only/` | Shared passport truth for governed module. |",
            )

            payload, exit_code = dispatch_module(
                argparse.Namespace(
                    project_root=project_root,
                    module_command="show",
                    selector="M-ONLY",
                    query=None,
                    readiness=None,
                    source_state=None,
                    limit=20,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            module = payload["module"]
            self.assertEqual(module["source_state"], "partial")
            self.assertEqual(module["readiness"]["status"], "blocked")
            warning_codes = {item["code"] for item in payload["warnings"]}
            self.assertIn("module_verification_missing", warning_codes)

    def test_module_show_blocks_mismatched_passport_and_verification_module_id(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            verification_text = _verification_text("M-ALPHA", slug="alpha").replace(
                "| Модуль | `M-ALPHA` |",
                "| Модуль | `M-BETA` |",
                1,
            )
            self._write_module(
                project_root,
                "M-ALPHA",
                "alpha",
                verification_text=verification_text,
                passport_text=_module_text("M-ALPHA", slug="alpha"),
            )
            self._write_registry(
                project_root,
                "| `M-ALPHA` | `alpha` | `passport_ready` | `blocked` | `knowledge/modules/M-ALPHA-alpha/module.md` | `knowledge/modules/M-ALPHA-alpha/verification.md` | `—` | `knowledge/modules/M-ALPHA-alpha/` | Shared passport truth for governed module. |",
            )

            payload, exit_code = dispatch_module(
                argparse.Namespace(
                    project_root=project_root,
                    module_command="show",
                    selector="M-ALPHA",
                    query=None,
                    readiness=None,
                    source_state=None,
                    limit=20,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["module"]["readiness"]["status"], "blocked")
            warning_codes = {item["code"] for item in payload["warnings"]}
            self.assertIn("module_passport_verification_module_mismatch", warning_codes)

    def test_module_show_rejects_ambiguous_slug(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self._write_module(project_root, "M-ONE", "shared")
            self._write_module(project_root, "M-TWO", "shared")

            payload, exit_code = dispatch_module(
                argparse.Namespace(
                    project_root=project_root,
                    module_command="show",
                    selector="shared",
                    query=None,
                    readiness=None,
                    source_state=None,
                    limit=20,
                )
            )

            self.assertEqual(exit_code, 2)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["warnings"][0]["code"], "module_selector_ambiguous")

    def test_module_show_rejects_duplicate_module_id(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self._write_module(project_root, "M-DUP", "one")
            self._write_module(project_root, "M-DUP", "two")

            payload, exit_code = dispatch_module(
                argparse.Namespace(
                    project_root=project_root,
                    module_command="show",
                    selector="M-DUP",
                    query=None,
                    readiness=None,
                    source_state=None,
                    limit=20,
                )
            )

            self.assertEqual(exit_code, 2)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["warnings"][0]["code"], "duplicate_module_id")

    def test_module_show_builds_outgoing_and_used_by_relations(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self._write_module(
                project_root,
                "M-ALPHA",
                "alpha",
                passport_text=_module_text(
                    "M-ALPHA",
                    slug="alpha",
                    relation_rows="| `depends_on` | `M-BETA` | `required` | Writer path depends on beta. |",
                ),
            )
            self._write_module(
                project_root,
                "M-BETA",
                "beta",
                passport_text=_module_text("M-BETA", slug="beta"),
            )
            self._write_registry(
                project_root,
                "| `M-ALPHA` | `alpha` | `passport_ready` | `ready` | `knowledge/modules/M-ALPHA-alpha/module.md` | `knowledge/modules/M-ALPHA-alpha/verification.md` | `—` | `knowledge/modules/M-ALPHA-alpha/` | Shared passport truth for governed module. |",
                "| `M-BETA` | `beta` | `passport_ready` | `ready` | `knowledge/modules/M-BETA-beta/module.md` | `knowledge/modules/M-BETA-beta/verification.md` | `—` | `knowledge/modules/M-BETA-beta/` | Shared passport truth for governed module. |",
            )

            alpha_payload, alpha_exit = dispatch_module(
                argparse.Namespace(
                    project_root=project_root,
                    module_command="show",
                    selector="M-ALPHA",
                    query=None,
                    readiness=None,
                    source_state=None,
                    limit=20,
                )
            )
            beta_payload, beta_exit = dispatch_module(
                argparse.Namespace(
                    project_root=project_root,
                    module_command="show",
                    selector="M-BETA",
                    query=None,
                    readiness=None,
                    source_state=None,
                    limit=20,
                )
            )

            self.assertEqual(alpha_exit, 0)
            self.assertEqual(beta_exit, 0)
            self.assertEqual(alpha_payload["module"]["relations"]["status"], "ready")
            self.assertEqual(alpha_payload["module"]["relations"]["summary"]["depends_on_total"], 1)
            self.assertEqual(alpha_payload["module"]["relations"]["outgoing"][0]["target_module_id"], "M-BETA")
            self.assertEqual(alpha_payload["module"]["relations"]["outgoing"][0]["target_slug"], "beta")
            self.assertEqual(beta_payload["module"]["relations"]["used_by"][0]["source_module_id"], "M-ALPHA")
            self.assertEqual(beta_payload["module"]["relations"]["summary"]["used_by_total"], 1)

            text_payload = format_module_show_payload(alpha_payload, with_sections={"relations"})
            self.assertIn("depends_on_total=1", text_payload)
            self.assertIn("used_by=—", text_payload)
            self.assertIn("- M-BETA | type=depends_on | status=required", text_payload)

    def test_module_show_marks_missing_relation_target_as_degraded(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self._write_module(
                project_root,
                "M-ALPHA",
                "alpha",
                passport_text=_module_text(
                    "M-ALPHA",
                    slug="alpha",
                    relation_rows="| `depends_on` | `M-GAMMA` | `planned` | Future dependency. |",
                ),
            )
            self._write_registry(
                project_root,
                "| `M-ALPHA` | `alpha` | `passport_ready` | `ready` | `knowledge/modules/M-ALPHA-alpha/module.md` | `knowledge/modules/M-ALPHA-alpha/verification.md` | `—` | `knowledge/modules/M-ALPHA-alpha/` | Shared passport truth for governed module. |",
            )

            payload, exit_code = dispatch_module(
                argparse.Namespace(
                    project_root=project_root,
                    module_command="show",
                    selector="M-ALPHA",
                    query=None,
                    readiness=None,
                    source_state=None,
                    limit=20,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["module"]["relations"]["status"], "degraded")
            self.assertEqual(payload["module"]["relations"]["outgoing"][0]["target_module_id"], "M-GAMMA")
            self.assertIsNone(payload["module"]["relations"]["outgoing"][0]["target_slug"])
            warning_codes = {item["code"] for item in payload["warnings"]}
            self.assertIn("module_relation_target_missing", warning_codes)

    def test_module_show_reports_invalid_relation_rows_without_breaking_module(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            relation_rows = "\n".join(
                [
                    "| `imports` | `M-BETA` | `required` | Unsupported type. |",
                    "| `depends_on` | `docs/spec.md` | `required` | Invalid target format. |",
                    "| `depends_on` | `M-ALPHA` | `required` | Self edge. |",
                    "| `depends_on` | `M-BETA` | `optional` | Invalid status. |",
                    "| `depends_on` | `M-BETA` | `required` | First valid edge. |",
                    "| `depends_on` | `M-BETA` | `required` | Duplicate edge. |",
                ]
            )
            self._write_module(
                project_root,
                "M-ALPHA",
                "alpha",
                passport_text=_module_text("M-ALPHA", slug="alpha", relation_rows=relation_rows),
            )
            self._write_module(
                project_root,
                "M-BETA",
                "beta",
                passport_text=_module_text("M-BETA", slug="beta"),
            )
            self._write_registry(
                project_root,
                "| `M-ALPHA` | `alpha` | `passport_ready` | `ready` | `knowledge/modules/M-ALPHA-alpha/module.md` | `knowledge/modules/M-ALPHA-alpha/verification.md` | `—` | `knowledge/modules/M-ALPHA-alpha/` | Shared passport truth for governed module. |",
                "| `M-BETA` | `beta` | `passport_ready` | `ready` | `knowledge/modules/M-BETA-beta/module.md` | `knowledge/modules/M-BETA-beta/verification.md` | `—` | `knowledge/modules/M-BETA-beta/` | Shared passport truth for governed module. |",
            )

            payload, exit_code = dispatch_module(
                argparse.Namespace(
                    project_root=project_root,
                    module_command="show",
                    selector="M-ALPHA",
                    query=None,
                    readiness=None,
                    source_state=None,
                    limit=20,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["module"]["relations"]["status"], "degraded")
            self.assertEqual(payload["module"]["relations"]["summary"]["depends_on_total"], 1)
            self.assertEqual(payload["module"]["relations"]["outgoing"][0]["target_module_id"], "M-BETA")
            warning_codes = {item["code"] for item in payload["warnings"]}
            self.assertIn("module_relation_invalid_type", warning_codes)
            self.assertIn("module_relation_invalid_target", warning_codes)
            self.assertIn("module_relation_self_reference", warning_codes)
            self.assertIn("module_relation_invalid_status", warning_codes)
            self.assertIn("module_relation_duplicate", warning_codes)

    def test_module_find_warns_about_duplicate_module_id(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self._write_module(project_root, "M-DUP", "one")
            self._write_module(project_root, "M-DUP", "two")

            payload, exit_code = dispatch_module(
                argparse.Namespace(
                    project_root=project_root,
                    module_command="find",
                    query="M-DUP",
                    readiness=None,
                    source_state=None,
                    limit=20,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 2)
            warning_codes = {item["code"] for item in payload["warnings"]}
            self.assertIn("duplicate_module_id", warning_codes)

    def test_file_show_uses_verification_evidence_fallback(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self._write_module(project_root, "M-ALPHA", "alpha")

            payload, exit_code = dispatch_file(
                argparse.Namespace(
                    project_root=project_root,
                    file_command="show",
                    path="tests/test_alpha.py",
                    module=None,
                    contracts=False,
                    blocks=False,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            file_payload = payload["file"]
            self.assertEqual(file_payload["governance_state"], "verification_evidence_only")
            self.assertEqual(file_payload["owner_modules"][0]["module_id"], "M-ALPHA")
            self.assertEqual(file_payload["verification_anchors"][0]["evidence_ref"], "EVD-01")
            self.assertIn("knowledge/modules/M-ALPHA-alpha/verification.md#SCN-01", file_payload["failure_handoff_refs"])
            self.assertIn("knowledge/modules/M-ALPHA-alpha/verification.md#SCN-02", file_payload["failure_handoff_refs"])

    def test_module_show_filters_outside_project_evidence_from_governed_paths(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            verification_text = _verification_text("M-ALPHA", slug="alpha").replace(
                "| `EVD-01` | `test-file` | `tests/test_alpha.py` | `BLOCK_M-ALPHA` | Основной test file. |",
                "| `EVD-01` | `test-file` | `/tmp/outside.py` | `BLOCK_M-ALPHA` | Outside path must not leak into governed surface. |",
                1,
            )
            self._write_module(
                project_root,
                "M-ALPHA",
                "alpha",
                verification_text=verification_text,
                passport_text=_module_text("M-ALPHA", slug="alpha"),
            )

            payload, exit_code = dispatch_module(
                argparse.Namespace(
                    project_root=project_root,
                    module_command="show",
                    selector="M-ALPHA",
                    query=None,
                    readiness=None,
                    source_state=None,
                    limit=20,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            module = payload["module"]
            self.assertNotIn("/tmp/outside.py", module["public_truth"]["governed_files"])
            self.assertNotIn("/tmp/outside.py", module["public_truth"]["evidence_file_refs"])
            self.assertNotIn("/tmp/outside.py", module["files"]["governed_files"])
            self.assertNotIn("/tmp/outside.py", module["files"]["evidence_file_refs"])
            self.assertNotIn("/tmp/outside.py", module["readiness"]["required_governed_files"])

    def test_file_show_prefers_passport_governed_state_when_owned_surface_present(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self._write_module(
                project_root,
                "M-ALPHA",
                "alpha",
                passport_text=_module_text("M-ALPHA", slug="alpha"),
            )
            self._write_registry(
                project_root,
                "| `M-ALPHA` | `alpha` | `passport_ready` | `ready` | `knowledge/modules/M-ALPHA-alpha/module.md` | `knowledge/modules/M-ALPHA-alpha/verification.md` | `—` | `knowledge/modules/M-ALPHA-alpha/` | Shared passport truth for governed module. |",
            )

            payload, exit_code = dispatch_file(
                argparse.Namespace(
                    project_root=project_root,
                    file_command="show",
                    path="scripts/alpha.py",
                    module=None,
                    contracts=False,
                    blocks=False,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            file_payload = payload["file"]
            self.assertEqual(file_payload["governance_state"], "passport_governed")
            self.assertEqual(file_payload["owner_modules"][0]["module_id"], "M-ALPHA")

    def test_file_show_parses_governed_hotspot_contract_markers_and_blocks(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self._write_module(
                project_root,
                "M-ALPHA",
                "alpha",
                passport_text=_module_text(
                    "M-ALPHA",
                    slug="alpha",
                    file_policy_ref="knowledge/modules/M-ALPHA-alpha/file-local-policy.md",
                ),
                file_policy_text=_file_local_policy_text(
                    "| `scripts/alpha.py` | `required` | `MODULE_CONTRACT, MODULE_MAP` | `BLOCK_VALIDATE_INPUT` | Runtime hot spot. |",
                ),
            )
            self._write_registry(
                project_root,
                "| `M-ALPHA` | `alpha` | `passport_ready` | `ready` | `knowledge/modules/M-ALPHA-alpha/module.md` | `knowledge/modules/M-ALPHA-alpha/verification.md` | `knowledge/modules/M-ALPHA-alpha/file-local-policy.md` | `knowledge/modules/M-ALPHA-alpha/` | Shared passport truth for governed module. |",
            )
            (project_root / "scripts/alpha.py").write_text(
                textwrap.dedent(
                    """\
                    # MODULE_CONTRACT:BEGIN
                    # shared context
                    # MODULE_CONTRACT:END
                    # BEGIN MODULE_MAP
                    # map
                    # END MODULE_MAP
                    # BLOCK_VALIDATE_INPUT:BEGIN
                    def run():
                        return True
                    # BLOCK_VALIDATE_INPUT:END
                    """
                ),
                encoding="utf-8",
            )

            payload, exit_code = dispatch_file(
                argparse.Namespace(
                    project_root=project_root,
                    file_command="show",
                    path="scripts/alpha.py",
                    module=None,
                    contracts=False,
                    blocks=False,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            file_payload = payload["file"]
            self.assertEqual(file_payload["governance_state"], "passport_governed")
            self.assertEqual(len(file_payload["contract_markers"]), 2)
            self.assertEqual(
                {item["marker"] for item in file_payload["contract_markers"]},
                {"MODULE_CONTRACT", "MODULE_MAP"},
            )
            self.assertTrue(all(item["present"] for item in file_payload["contract_markers"]))
            self.assertEqual(file_payload["blocks"][0]["block_id"], "BLOCK_VALIDATE_INPUT")
            self.assertTrue(file_payload["blocks"][0]["present"])
            warning_codes = {item["code"] for item in payload["warnings"]}
            self.assertNotIn("file_contract_unavailable", warning_codes)
            self.assertNotIn("file_not_governed_hotspot", warning_codes)

    def test_file_show_warns_when_owned_file_is_not_in_hotspot_policy(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self._write_module(
                project_root,
                "M-ALPHA",
                "alpha",
                passport_text=_module_text(
                    "M-ALPHA",
                    slug="alpha",
                    file_policy_ref="knowledge/modules/M-ALPHA-alpha/file-local-policy.md",
                ),
                file_policy_text=_file_local_policy_text(
                    "| `tests/test_alpha.py` | `advisory` | `CHANGE_SUMMARY` | `—` | Test-only hot spot. |",
                ),
            )
            self._write_registry(
                project_root,
                "| `M-ALPHA` | `alpha` | `passport_ready` | `ready` | `knowledge/modules/M-ALPHA-alpha/module.md` | `knowledge/modules/M-ALPHA-alpha/verification.md` | `knowledge/modules/M-ALPHA-alpha/file-local-policy.md` | `knowledge/modules/M-ALPHA-alpha/` | Shared passport truth for governed module. |",
            )

            payload, exit_code = dispatch_file(
                argparse.Namespace(
                    project_root=project_root,
                    file_command="show",
                    path="scripts/alpha.py",
                    module=None,
                    contracts=False,
                    blocks=False,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["file"]["contract_markers"], [])
            self.assertEqual(payload["file"]["blocks"], [])
            warning_codes = {item["code"] for item in payload["warnings"]}
            self.assertIn("file_not_governed_hotspot", warning_codes)

    def test_file_show_keeps_contracts_empty_for_multi_owner_without_module(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            shared_surface_alpha = _module_text(
                "M-ALPHA",
                slug="alpha",
                file_policy_ref="knowledge/modules/M-ALPHA-alpha/file-local-policy.md",
            ).replace("tests/test_alpha.py", "tests/shared.py")
            shared_surface_beta = _module_text(
                "M-BETA",
                slug="beta",
                file_policy_ref="knowledge/modules/M-BETA-beta/file-local-policy.md",
            ).replace("tests/test_beta.py", "tests/shared.py")
            self._write_module(
                project_root,
                "M-ALPHA",
                "alpha",
                passport_text=shared_surface_alpha,
                file_policy_text=_file_local_policy_text(
                    "| `tests/shared.py` | `required` | `MODULE_CONTRACT` | `BLOCK_SHARED` | Shared alpha hot spot. |",
                ),
            )
            self._write_module(
                project_root,
                "M-BETA",
                "beta",
                passport_text=shared_surface_beta,
                file_policy_text=_file_local_policy_text(
                    "| `tests/shared.py` | `required` | `MODULE_MAP` | `BLOCK_SHARED` | Shared beta hot spot. |",
                ),
            )
            self._write_registry(
                project_root,
                "| `M-ALPHA` | `alpha` | `passport_ready` | `ready` | `knowledge/modules/M-ALPHA-alpha/module.md` | `knowledge/modules/M-ALPHA-alpha/verification.md` | `knowledge/modules/M-ALPHA-alpha/file-local-policy.md` | `knowledge/modules/M-ALPHA-alpha/` | Shared passport truth for governed module. |",
                "| `M-BETA` | `beta` | `passport_ready` | `ready` | `knowledge/modules/M-BETA-beta/module.md` | `knowledge/modules/M-BETA-beta/verification.md` | `knowledge/modules/M-BETA-beta/file-local-policy.md` | `knowledge/modules/M-BETA-beta/` | Shared passport truth for governed module. |",
            )
            shared_test = project_root / "tests/shared.py"
            shared_test.write_text(
                "# MODULE_CONTRACT:BEGIN\n# body\n# MODULE_CONTRACT:END\n# BLOCK_SHARED:BEGIN\n# BLOCK_SHARED:END\n",
                encoding="utf-8",
            )

            payload, exit_code = dispatch_file(
                argparse.Namespace(
                    project_root=project_root,
                    file_command="show",
                    path="tests/shared.py",
                    module=None,
                    contracts=False,
                    blocks=False,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(payload["file"]["owner_modules"]), 2)
            self.assertEqual(payload["file"]["contract_markers"], [])
            self.assertEqual(payload["file"]["blocks"], [])
            warning_codes = {item["code"] for item in payload["warnings"]}
            self.assertIn("multi_owner_file_contract_ambiguous", warning_codes)

    def test_module_find_ignores_templates_directory(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            templates_dir = project_root / "knowledge/modules/_templates"
            templates_dir.mkdir(parents=True, exist_ok=True)
            (templates_dir / "verification.md").write_text(
                _verification_text("M-XXX", slug="example"),
                encoding="utf-8",
            )

            payload, exit_code = dispatch_module(
                argparse.Namespace(
                    project_root=project_root,
                    module_command="find",
                    query="M-XXX",
                    readiness=None,
                    source_state=None,
                    limit=20,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 0)
            self.assertEqual(payload["warnings"][0]["code"], "module_query_empty")

    def test_file_show_rejects_path_outside_project(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))

            payload, exit_code = dispatch_file(
                argparse.Namespace(
                    project_root=project_root,
                    file_command="show",
                    path="/tmp/outside-file.txt",
                    module=None,
                    contracts=False,
                    blocks=False,
                )
            )

            self.assertEqual(exit_code, 2)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["warnings"][0]["code"], "path_outside_project")

    def test_file_show_rejects_existing_module_that_does_not_own_file(self) -> None:
        with self.make_tempdir() as tmp_dir:
            project_root = self.init_repo(Path(tmp_dir))
            self._write_module(project_root, "M-ONE", "one")
            self._write_module(project_root, "M-TWO", "two")

            payload, exit_code = dispatch_file(
                argparse.Namespace(
                    project_root=project_root,
                    file_command="show",
                    path="tests/test_one.py",
                    module="M-TWO",
                    contracts=False,
                    blocks=False,
                )
            )

            self.assertEqual(exit_code, 2)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["warnings"][0]["code"], "file_module_mismatch")


if __name__ == "__main__":
    unittest.main()
