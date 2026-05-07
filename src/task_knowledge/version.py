"""Single-source version and public consumer contract constants."""

from __future__ import annotations

__version__ = "0.1.0"

CLI_VERSION = __version__
CONSUMER_RUNTIME_CONTRACT = "consumer-runtime-v1"
CONSUMER_RUNTIME_SCHEMA_VERSION = 1

CONSUMER_RUNTIME_MANIFEST_KEYS = (
    "integration_contract",
    "pinned_commit",
    "included_paths",
    "consumer_runtime_root",
    "consumer_entrypoint",
)

