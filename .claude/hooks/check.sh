#!/usr/bin/env bash
# Stop: before Claude ends a turn, run the fast static checks (`make lint`) if Python changed.
# Exit 2 sends the errors back to Claude. Tests stay in `make check` / CI.
set -uo pipefail
cd "$CLAUDE_PROJECT_DIR"

# Skip when no uncommitted Python or project file changed since the last passing run
# (e.g. a Q&A turn, or a docs-only edit).
stamp="$(git rev-parse --git-dir)/claude-stop-check"
changed=0
while IFS= read -r f; do
  [[ -f "$f" && ( ! -e "$stamp" || "$f" -nt "$stamp" ) ]] && changed=1 && break
done < <(git ls-files --modified --others --exclude-standard -- '*.py' pyproject.toml)
(( changed )) || exit 0

if ! make -s lint >&2; then
  echo "Fix the errors above before finishing." >&2
  exit 2
fi
touch "$stamp"
