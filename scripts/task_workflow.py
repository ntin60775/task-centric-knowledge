#!/usr/bin/env python3
"""Thin compatibility facade for modular task workflow runtime."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from task_workflow_runtime import (  # noqa: E402
    DELIVERY_ROW_PLACEHOLDER,
    DeliveryUnit,
    PublicationSnapshot,
    StepResult,
    main,
    update_task_file_with_delivery_units,
)
from task_workflow_runtime import publish_flow as _publish_flow_module  # noqa: E402
from task_workflow_runtime import sync_flow as _sync_flow_module  # noqa: E402
from task_workflow_runtime.forge import resolve_forge_adapter  # noqa: E402


def sync_task(*args, **kwargs):
    return _sync_flow_module.sync_task(*args, **kwargs)


def run_publish_flow(*args, **kwargs):
    _publish_flow_module.resolve_forge_adapter = resolve_forge_adapter
    return _publish_flow_module.run_publish_flow(*args, **kwargs)


__all__ = [
    "DELIVERY_ROW_PLACEHOLDER",
    "DeliveryUnit",
    "PublicationSnapshot",
    "StepResult",
    "main",
    "resolve_forge_adapter",
    "run_publish_flow",
    "sync_task",
    "update_task_file_with_delivery_units",
]


if __name__ == "__main__":
    raise SystemExit(main())
