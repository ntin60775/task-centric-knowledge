#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
guard_script="$HOME/.agents/skills/owned-text-localization-guard/scripts/markdown_localization_guard.py"

exec python3 "$guard_script" \
  --root "$repo_root" \
  --resolve-relative-to-root \
  --allow-phrase "Hot spots" \
  "$@"
