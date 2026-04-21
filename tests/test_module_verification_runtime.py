from __future__ import annotations

import textwrap
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

SCRIPTS_DIR = TESTS_DIR.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from task_workflow_testlib import TempRepoCase

from module_core_runtime import (
    ModuleVerificationError,
    build_failure_handoff,
    build_verification_excerpt,
    load_module_verification,
    resolve_execution_readiness,
)


def _verification_text(
    *,
    declared_status: str = "ready",
    verification_ref: str = "knowledge/modules/M-TEST-test/verification.md",
    writer_gate: str = "writer",
    duplicate_check_ref: bool = False,
    followup_command: str = "`oscript scripts/check-observability.bsl`",
    evidence_anchor: str = "`BLOCK_VALIDATE_INPUT`",
) -> str:
    second_check_ref = "CHK-01" if duplicate_check_ref else "CHK-02"
    return textwrap.dedent(
        f"""\
        # Модульная верификация `M-TEST`

        ## Паспорт

        | Поле | Значение |
        |------|----------|
        | Модуль | `M-TEST` |
        | Ссылка верификации | `{verification_ref}` |
        | Статус готовности | `{declared_status}` |
        | Дата обновления | `2026-04-20` |

        ## Канонические проверки

        | ID проверки | Гейт | Тип | Команда | Блокирует | Назначение |
        |------------|------|-----|---------|------------|------------|
        | `CHK-01` | `{writer_gate}` | `command` | `python3 -m unittest tests/test_module_test.py` | `да` | Writer-level smoke path. |
        | `{second_check_ref}` | `task-followup` | `artifact-check` | {followup_command} | `нет` | Follow-up наблюдаемость для `1С/BSL`. |

        ## Доказательства

        | ID доказательства | Тип | Значение | Якорь | Заметки |
        |------------------|-----|----------|-------|---------|
        | `EVD-01` | `test-file` | `tests/test_module_test.py` | `—` | Основной test file. |
        | `EVD-02` | `log-marker` | `[TestDomain][run][BLOCK_VALIDATE_INPUT]` | {evidence_anchor} | Marker для отказа. |

        ## Сценарии

        | ID сценария | Тип | Описание | Обязательные проверки | Обязательные доказательства | Блокирует |
        |-------------|-----|----------|-----------------------|--------------------------|------------|
        | `SCN-01` | `success` | Writer path проходит детерминированный smoke-check. | `CHK-01` | `EVD-01` | `да` |
        | `SCN-02` | `observability` | Ошибка остаётся наблюдаемой через стабильный marker. | `CHK-01, {second_check_ref}` | `EVD-01, EVD-02` | `да` |

        ## Ручной остаток

        | ID риска | Применимость | Причина | Действие контроллера |
        |----------|--------------|---------|----------------------|
        | `RISK-01` | `task-followup` | Интеграционный follow-up не должен блокировать writer-pass. | `Поднять в task-local matrix.` |
        """
    )


class ModuleVerificationRuntimeTests(TempRepoCase):
    def _write_verification(self, root: Path, text: str) -> Path:
        verification_path = root / "knowledge/modules/M-TEST-test/verification.md"
        verification_path.parent.mkdir(parents=True, exist_ok=True)
        verification_path.write_text(text, encoding="utf-8")
        return verification_path

    def test_load_module_verification_parses_valid_markdown_artifact(self) -> None:
        with self.make_tempdir() as tmp_dir:
            verification_path = self._write_verification(Path(tmp_dir), _verification_text())

            record = load_module_verification(verification_path)

            self.assertEqual(record.module_id, "M-TEST")
            self.assertEqual(record.verification_ref, "knowledge/modules/M-TEST-test/verification.md")
            self.assertEqual(tuple(record.checks), ("CHK-01", "CHK-02"))
            self.assertEqual(record.evidence["EVD-02"].anchor_ref, "BLOCK_VALIDATE_INPUT")
            self.assertEqual(record.scenarios["SCN-02"].required_check_refs, ("CHK-01", "CHK-02"))

    def test_resolve_execution_readiness_reports_ready_for_valid_writer_gate(self) -> None:
        with self.make_tempdir() as tmp_dir:
            verification_path = self._write_verification(Path(tmp_dir), _verification_text())

            readiness = resolve_execution_readiness(
                verification_path,
                expected_verification_ref="knowledge/modules/M-TEST-test/verification.md",
            )

            self.assertEqual(readiness.status, "ready")
            self.assertEqual(readiness.blocking_reasons, ())
            self.assertIn("knowledge/modules/M-TEST-test/verification.md#SCN-01", readiness.required_verification_refs)
            self.assertEqual(readiness.residual_manual_risk, ("RISK-01",))

    def test_resolve_execution_readiness_reports_partial_without_writer_level_check(self) -> None:
        with self.make_tempdir() as tmp_dir:
            verification_path = self._write_verification(
                Path(tmp_dir),
                _verification_text(declared_status="partial", writer_gate="task-followup"),
            )

            readiness = resolve_execution_readiness(verification_path)

            self.assertEqual(readiness.status, "partial")
            self.assertTrue(
                any("не содержит writer-level проверки" in reason for reason in readiness.blocking_reasons)
            )

    def test_resolve_execution_readiness_reports_blocked_for_invalid_duplicate_refs(self) -> None:
        with self.make_tempdir() as tmp_dir:
            verification_path = self._write_verification(
                Path(tmp_dir),
                _verification_text(declared_status="blocked", duplicate_check_ref=True),
            )

            readiness = resolve_execution_readiness(verification_path)

            self.assertEqual(readiness.status, "blocked")
            self.assertTrue(any("задан более одного раза" in reason for reason in readiness.blocking_reasons))

    def test_build_verification_excerpt_keeps_writer_checks_and_followups_separate(self) -> None:
        with self.make_tempdir() as tmp_dir:
            verification_path = self._write_verification(Path(tmp_dir), _verification_text())
            record = load_module_verification(verification_path)

            excerpt = build_verification_excerpt(record)

            self.assertEqual(excerpt.readiness_status, "ready")
            self.assertEqual(tuple(item.ref for item in excerpt.writer_checks), ("CHK-01",))
            self.assertEqual(tuple(item.ref for item in excerpt.task_followups), ("CHK-02",))
            self.assertEqual(tuple(item.ref for item in excerpt.required_scenarios), ("SCN-01", "SCN-02"))
            self.assertEqual(tuple(item.ref for item in excerpt.manual_residual), ("RISK-01",))

    def test_build_failure_handoff_uses_scenario_anchor_and_expected_evidence(self) -> None:
        with self.make_tempdir() as tmp_dir:
            verification_path = self._write_verification(Path(tmp_dir), _verification_text())
            record = load_module_verification(verification_path)

            handoff = build_failure_handoff(
                record,
                reference="SCN-02",
                observed_evidence=(
                    "Marker BLOCK_VALIDATE_INPUT отсутствует в логе.",
                    "Команда завершилась кодом 1.",
                ),
            )

            self.assertEqual(
                handoff.contract_ref,
                "knowledge/modules/M-TEST-test/verification.md#SCN-02",
            )
            self.assertEqual(handoff.first_divergent_anchor, "BLOCK_VALIDATE_INPUT")
            self.assertEqual(
                handoff.expected_evidence,
                ("tests/test_module_test.py", "[TestDomain][run][BLOCK_VALIDATE_INPUT]"),
            )
            self.assertEqual(handoff.suggested_next_action, "fix_code")

    def test_load_module_verification_rejects_self_mismatched_ref_without_external_hint(self) -> None:
        with self.make_tempdir() as tmp_dir:
            verification_path = self._write_verification(
                Path(tmp_dir),
                _verification_text(verification_ref="knowledge/modules/M-OTHER/verification.md"),
            )

            with self.assertRaises(ModuleVerificationError):
                load_module_verification(verification_path)

    def test_load_module_verification_rejects_section_without_canonical_header(self) -> None:
        with self.make_tempdir() as tmp_dir:
            verification_text = _verification_text().replace(
                "| ID доказательства | Тип | Значение | Якорь | Заметки |\n",
                "",
            )
            verification_path = self._write_verification(Path(tmp_dir), verification_text)

            with self.assertRaises(ModuleVerificationError):
                load_module_verification(verification_path)

    def test_resolve_execution_readiness_reports_partial_without_anchor_and_governed_file(self) -> None:
        with self.make_tempdir() as tmp_dir:
            verification_path = self._write_verification(
                Path(tmp_dir),
                _verification_text(declared_status="partial", evidence_anchor="`—`"),
            )

            readiness = resolve_execution_readiness(verification_path)

            self.assertEqual(readiness.status, "partial")
            self.assertTrue(any("governed-file fallback" in reason for reason in readiness.blocking_reasons))
            self.assertIn("tests/test_module_test.py", readiness.required_governed_files)

    def test_build_failure_handoff_falls_back_to_governed_file_when_anchor_missing(self) -> None:
        with self.make_tempdir() as tmp_dir:
            verification_path = self._write_verification(
                Path(tmp_dir),
                _verification_text(evidence_anchor="`—`"),
            )
            record = load_module_verification(
                verification_path,
                governed_files=("src/cf/CommonModules/Example/Ext/Module.bsl",),
            )

            handoff = build_failure_handoff(
                record,
                reference="SCN-02",
                observed_evidence="Marker не найден.",
            )

            self.assertEqual(
                handoff.first_divergent_anchor,
                "src/cf/CommonModules/Example/Ext/Module.bsl",
            )

    def test_build_failure_handoff_falls_back_to_evidence_file_path(self) -> None:
        with self.make_tempdir() as tmp_dir:
            verification_path = self._write_verification(Path(tmp_dir), _verification_text())
            record = load_module_verification(verification_path)

            handoff = build_failure_handoff(
                record,
                reference="SCN-01",
                observed_evidence="Smoke-check упал.",
            )

            self.assertEqual(handoff.first_divergent_anchor, "tests/test_module_test.py")

    def test_load_module_verification_allows_followup_artifact_check_without_command(self) -> None:
        with self.make_tempdir() as tmp_dir:
            verification_path = self._write_verification(
                Path(tmp_dir),
                _verification_text(followup_command="`—`"),
            )

            record = load_module_verification(verification_path)

            self.assertEqual(record.checks["CHK-02"].command, "—")

    def test_load_module_verification_rejects_mismatched_ref(self) -> None:
        with self.make_tempdir() as tmp_dir:
            verification_path = self._write_verification(Path(tmp_dir), _verification_text())

            with self.assertRaises(ModuleVerificationError):
                load_module_verification(
                    verification_path,
                    expected_verification_ref="knowledge/modules/M-OTHER/verification.md",
                )
