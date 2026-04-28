#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
guard_script="$HOME/.agents/skills/owned-text-localization-guard/scripts/markdown_localization_guard.py"

exec python3 "$guard_script" \
  --root "$repo_root" \
  --resolve-relative-to-root \
  --allow-phrase "Hot spots" \
  --allow-phrase "bash" \
  --allow-phrase "make check" \
  --allow-phrase "make check-strict" \
  --allow-phrase "make install-global-dry-run" \
  --allow-phrase "make install-global" \
  --allow-phrase "make verify-global-install" \
  --allow-phrase "make project-install-check" \
  --allow-phrase "make project-install-apply" \
  --allow-phrase "make project-install-verify" \
  --allow-phrase "PROJECT_ROOT" \
  --allow-phrase "SOURCE_ROOT" \
  --allow-phrase "PROFILE" \
  --allow-phrase "generic" \
  --allow-phrase "task-knowledge install check" \
  --allow-phrase "task-knowledge install apply" \
  --allow-phrase "task-knowledge install verify-project" \
  --allow-phrase "task-knowledge install doctor-deps" \
  --allow-phrase "task-knowledge workflow sync" \
  --allow-phrase "task-knowledge doctor" \
  --allow-phrase "git status" \
  --allow-phrase "git diff" \
  --allow-phrase=--check \
  --allow-phrase "git switch" \
  --allow-phrase "git add" \
  --allow-phrase "git commit" \
  --allow-phrase "python3" \
  --allow-phrase "compileall" \
  --allow-phrase "unittest" \
  --allow-phrase "discover" \
  --allow-phrase "source-root" \
  --allow-phrase "project-root" \
  --allow-phrase "profile" \
  --allow-phrase "force" \
  --allow-phrase "short" \
  --allow-phrase "upgrade-task-knowledge" \
  --allow-phrase "task-id" \
  --allow-phrase "task-dir" \
  --allow-phrase "tasks" \
  --allow-phrase "tests" \
  --allow-phrase "Ran" \
  --allow-phrase "TASK" \
  --allow-phrase "upgrade" \
  --allow-phrase "strict" \
  --allow-phrase "knowledge" \
  --allow-phrase "AGENTS.md" \
  --allow-phrase "abs" \
  --allow-phrase "project" \
  --allow-phrase "HOME" \
  --allow-phrase "agents" \
  --allow-phrase "skills" \
  --allow-phrase "scripts" \
  --allow-phrase "task-centric-knowledge" \
  --allow-phrase "centric" \
  --allow-phrase "OK" \
  "$@"
