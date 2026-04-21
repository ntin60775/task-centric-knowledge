from __future__ import annotations

import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

SCRIPTS_DIR = TESTS_DIR.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from module_core_runtime.file_local_contracts import load_file_local_policy, parse_file_local_contracts


def _policy_text(*rows: str) -> str:
    body = "\n".join(rows)
    return textwrap.dedent(
        f"""\
        # File-local policy

        ## Hot spots

        | Путь | Режим | Разрешённые markers | Обязательные blocks | Назначение |
        |------|-------|---------------------|---------------------|------------|
        {body}
        """
    )


class FileLocalContractsRuntimeTests(unittest.TestCase):
    def test_parser_detects_paired_markers_and_required_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            policy_path = project_root / "knowledge/modules/M-ALPHA-alpha/file-local-policy.md"
            policy_path.parent.mkdir(parents=True, exist_ok=True)
            policy_path.write_text(
                _policy_text(
                    "| `scripts/alpha.py` | `required` | `MODULE_CONTRACT, MODULE_MAP` | `BLOCK_VALIDATE_INPUT` | Runtime hot spot. |",
                ),
                encoding="utf-8",
            )
            governed_file = project_root / "scripts/alpha.py"
            governed_file.parent.mkdir(parents=True, exist_ok=True)
            governed_file.write_text(
                textwrap.dedent(
                    """\
                    # MODULE_CONTRACT:BEGIN
                    # contract body
                    # MODULE_CONTRACT:END
                    # BEGIN MODULE_MAP
                    # map body
                    # END MODULE_MAP
                    # BLOCK_VALIDATE_INPUT:BEGIN
                    def run():
                        return True
                    # BLOCK_VALIDATE_INPUT:END
                    """
                ),
                encoding="utf-8",
            )

            policy = load_file_local_policy(project_root, policy_path)
            parsed = parse_file_local_contracts(governed_file, policy.hot_spots_by_path["scripts/alpha.py"])

            self.assertEqual(len(parsed.contract_markers), 2)
            self.assertTrue(all(item.present for item in parsed.contract_markers))
            self.assertEqual(parsed.blocks[0].block_id, "BLOCK_VALIDATE_INPUT")
            self.assertTrue(parsed.blocks[0].present)
            self.assertEqual(parsed.warnings, ())

    def test_parser_reports_missing_end_marker_and_missing_required_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            policy_path = project_root / "knowledge/modules/M-ALPHA-alpha/file-local-policy.md"
            policy_path.parent.mkdir(parents=True, exist_ok=True)
            policy_path.write_text(
                _policy_text(
                    "| `scripts/alpha.py` | `required` | `MODULE_CONTRACT` | `BLOCK_VALIDATE_INPUT` | Runtime hot spot. |",
                ),
                encoding="utf-8",
            )
            governed_file = project_root / "scripts/alpha.py"
            governed_file.parent.mkdir(parents=True, exist_ok=True)
            governed_file.write_text(
                "// MODULE_CONTRACT:BEGIN\n"
                "def run():\n"
                "    return True\n",
                encoding="utf-8",
            )

            policy = load_file_local_policy(project_root, policy_path)
            parsed = parse_file_local_contracts(governed_file, policy.hot_spots_by_path["scripts/alpha.py"])

            warnings = {item.code for item in parsed.warnings}
            self.assertIn("file_contract_missing_end", warnings)
            self.assertIn("file_contract_required_marker_missing", warnings)
            self.assertIn("file_contract_required_block_missing", warnings)
            self.assertFalse(parsed.contract_markers[0].present)
            self.assertEqual(parsed.contract_markers[0].start_line, 1)
            self.assertIsNone(parsed.contract_markers[0].end_line)

    def test_parser_supports_all_declared_comment_prefixes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            policy_path = project_root / "knowledge/modules/M-ALPHA-alpha/file-local-policy.md"
            policy_path.parent.mkdir(parents=True, exist_ok=True)
            policy_path.write_text(
                _policy_text(
                    "| `scripts/prefixes.txt` | `advisory` | `MODULE_CONTRACT, MODULE_MAP, CHANGE_SUMMARY` | `BLOCK_PREFIX` | Prefix matrix. |",
                ),
                encoding="utf-8",
            )
            governed_file = project_root / "scripts/prefixes.txt"
            governed_file.parent.mkdir(parents=True, exist_ok=True)
            governed_file.write_text(
                textwrap.dedent(
                    """\
                    // MODULE_CONTRACT:BEGIN
                    // MODULE_CONTRACT:END
                    # MODULE_MAP:BEGIN
                    # MODULE_MAP:END
                    -- CHANGE_SUMMARY:BEGIN
                    -- CHANGE_SUMMARY:END
                    ; BLOCK_PREFIX:BEGIN
                    ; BLOCK_PREFIX:END
                    * BLOCK_STAR:BEGIN
                    * BLOCK_STAR:END
                    """
                ),
                encoding="utf-8",
            )

            policy = load_file_local_policy(project_root, policy_path)
            parsed = parse_file_local_contracts(governed_file, policy.hot_spots_by_path["scripts/prefixes.txt"])

            self.assertEqual({item.marker for item in parsed.contract_markers}, {"MODULE_CONTRACT", "MODULE_MAP", "CHANGE_SUMMARY"})
            self.assertTrue(all(item.present for item in parsed.contract_markers))
            block_ids = {item.block_id for item in parsed.blocks}
            self.assertIn("BLOCK_PREFIX", block_ids)
            self.assertIn("BLOCK_STAR", block_ids)

    def test_parser_handles_bsl_style_double_slash_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            policy_path = project_root / "knowledge/modules/M-BSL-example/file-local-policy.md"
            policy_path.parent.mkdir(parents=True, exist_ok=True)
            policy_path.write_text(
                _policy_text(
                    "| `src/example.bsl` | `required` | `CHANGE_SUMMARY` | `BLOCK_POSTING` | BSL hot spot. |",
                ),
                encoding="utf-8",
            )
            governed_file = project_root / "src/example.bsl"
            governed_file.parent.mkdir(parents=True, exist_ok=True)
            governed_file.write_text(
                textwrap.dedent(
                    """\
                    // CHANGE_SUMMARY:BEGIN
                    // Локальный смысловой контракт для 1С/BSL
                    // CHANGE_SUMMARY:END
                    // BLOCK_POSTING:BEGIN
                    Процедура ВыполнитьПроведение()
                    КонецПроцедуры
                    // BLOCK_POSTING:END
                    """
                ),
                encoding="utf-8",
            )

            policy = load_file_local_policy(project_root, policy_path)
            parsed = parse_file_local_contracts(governed_file, policy.hot_spots_by_path["src/example.bsl"])

            self.assertEqual(parsed.contract_markers[0].marker, "CHANGE_SUMMARY")
            self.assertTrue(parsed.contract_markers[0].present)
            self.assertEqual(parsed.blocks[0].block_id, "BLOCK_POSTING")
            self.assertTrue(parsed.blocks[0].present)


if __name__ == "__main__":
    unittest.main()
