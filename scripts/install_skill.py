#!/usr/bin/env python3
"""Thin compatibility facade for install skill runtime."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from install_skill_runtime import (  # noqa: E402
    ADDITIVE_MANAGED_TARGET_FILES,
    BEGIN_MARKER,
    COMPATIBILITY_BASELINE_TARGET_FILES,
    END_MARKER,
    ExistingSystemReport,
    FORCE_OVERWRITABLE_TARGET_FILES,
    KNOWLEDGE_ASSET_FILES,
    MANAGED_TARGET_FILES,
    MIGRATION_NOTE_NAME,
    PROFILE_TO_BLOCK,
    PROJECT_DATA_TARGET_FILES,
    REQUIRED_RELATIVE_PATHS,
    SKILL_NAME,
    StepResult,
    VALID_MODES,
    check,
    detect_existing_system,
    main,
    skill_root,
)
from install_skill_runtime import doctor_deps as _doctor_deps  # noqa: E402
from install_skill_runtime import environment as _environment_module  # noqa: E402
from install_skill_runtime import migrate_cleanup_confirm as _migrate_cleanup_confirm  # noqa: E402
from install_skill_runtime import migrate_cleanup_plan as _migrate_cleanup_plan  # noqa: E402


def install(*args, **kwargs):
    return _environment_module.install(*args, **kwargs)


def doctor_deps(*args, **kwargs):
    return _doctor_deps(*args, **kwargs)


def migrate_cleanup_plan(*args, **kwargs):
    return _migrate_cleanup_plan(*args, **kwargs)


def migrate_cleanup_confirm(*args, **kwargs):
    return _migrate_cleanup_confirm(*args, **kwargs)


if __name__ == "__main__":
    raise SystemExit(main(script_path=Path(__file__).resolve()))
