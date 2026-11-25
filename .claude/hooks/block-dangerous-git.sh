#!/bin/bash
# Blocks destructive git commands. Plain `git push` of a feature branch stays
# allowed: the pull-request skill needs it. Limits: it runs in the session's
# cwd, and a feature branch tracking origin/main with push.default=upstream
# is not caught.

# Fail closed: without jq the command can't be read and the guard would be off.
command -v jq >/dev/null || { echo "BLOCKED: this hook needs jq." >&2; exit 2; }

COMMAND=$(jq -r '.tool_input.command')

DANGEROUS_PATTERNS=(
  "^git push\b.*( --(force|mirror)| -[a-zA-Z]*f| \+)"
  "^git push\b.*(^| |:|\"|'|refs/heads/)main(\"|'| |$)"
  "^git reset\b.* --hard"
  "^git clean\b.*( -[a-zA-Z]*f| --force)"
  "^git branch\b.*( -[a-zA-Z]*D| -[a-zA-Z]*[df][a-zA-Z]*[df]| -f( |$)| --force)"
  "^git checkout\b.* (-f|--force)( |$)"
  "^git (checkout|restore)\b.* \.( |$)"
)

# One segment per command in a chain, with git's global options (-C dir, -c k=v) dropped,
# so `cd x && git -C y push --force` is checked as `git push --force`.
SEGMENTS=$(printf '%s\n' "$COMMAND" \
  | sed -E 's/(&&|\|\||[;|&])/\n/g' \
  | sed -E 's/ +/ /g; s/^ //' \
  | sed -E 's/^git ((-[cC] [^ ]+|--[a-z-]+(=[^ ]+)?) )*/git /' \
  | grep -E '^git ')

while IFS= read -r segment; do
  [ -z "$segment" ] && continue
  for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if printf '%s\n' "$segment" | grep -qE "$pattern"; then
      echo "BLOCKED: '$segment' matches dangerous pattern '$pattern'. The user has prevented you from doing this." >&2
      exit 2
    fi
  done
  # Bare `git push` / `git push origin HEAD` while main is checked out.
  if [[ "$segment" == "git push"* ]] && [ "$(git rev-parse --abbrev-ref HEAD 2>/dev/null)" = "main" ]; then
    echo "BLOCKED: '$segment' would push main. Branch first." >&2
    exit 2
  fi
done <<< "$SEGMENTS"

exit 0
