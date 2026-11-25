#!/usr/bin/env bash
# PostToolUse: format the Python file Claude just edited, so it never spends a turn on style.
# Only formatting + import sorting: `ruff check --fix` would delete imports that are added
# before the code that uses them.
set -euo pipefail

file=$(jq -r '.tool_input.file_path // empty')
case "$file" in
  "$CLAUDE_PROJECT_DIR"/*.py) ;;
  *) exit 0 ;;
esac

cd "$CLAUDE_PROJECT_DIR"
uv run --quiet ruff format --quiet "$file"
uv run --quiet ruff check --quiet --select I --fix "$file" || true
