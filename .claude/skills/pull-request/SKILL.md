---
name: pull-request
description: Open or edit a GitHub pull request for this repo using the project template. Use whenever the user asks to open, create, raise or update a PR, or to push work up for review.
---

# Pull request

The body follows `.github/pull_request_template.md`; read it, don't work from memory.

## Steps
1. Not on `main`: if you are, branch first (use the Linear issue's branch name). `make check` passed and the `reviewer` agent ran on the diff (`CLAUDE.md`).
2. Find the Linear issue (Linear MCP, project in the `linear-issue` skill): from the branch name, the conversation, or a search. None and the work is non-trivial: ask whether to create one through `linear-issue`. Trivial chores need none; delete the `Fixes` line.
3. Fill the template: drop its HTML comments, empty optional sections and Flags lines that don't apply. Every Flags line that applies must be there.
4. `git push -u origin HEAD`, then `gh pr create --title "<title>" --body-file <file>` (or `gh pr edit` for an existing PR).
5. Reply with the PR link, nothing else.

## Title
Conventional Commit, the same type the Linear label maps to (see `linear-issue`): `feat(ingestion): …`, `fix(machines): …`. Imperative, ≤72 chars, no issue ID (it goes in the body).

## Body rules
- `Fixes SOL-<n>` when the PR finishes the issue; `Part of SOL-<n>` when it doesn't.
- "What changed" says what a reviewer can check in the diff, not the commit log. Name reused code, new dependencies and anything skipped.
- "Verified" is what you ran or looked at yourself, beyond CI: requests against the running stack, a migration applied to a real database, the worker draining a stream. If you didn't check something, say so; never imply it.
- Link, don't copy: name files, commands and docs.

## Never
- Secrets, credentials or `.env` values, even redacted.
- Sections beyond the template.
- Merge or force-push unless the user asks.
