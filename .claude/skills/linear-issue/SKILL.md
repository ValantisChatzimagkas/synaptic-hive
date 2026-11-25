---
name: linear-issue
description: Repo conventions for Linear issues: target project, template, labels, milestone. Use whenever the user asks to create, file, open, log or write up an issue, ticket, task or bug, or to turn something from the conversation into one.
---

# Linear issue

Every issue goes to the Linear project **Synaptic Hive**
(https://linear.app/tcv-coding-space/project/synaptic-hive-92451fc97b2b), team `Solo` (key `SOL`). Look up label IDs through the Linear MCP; don't guess them.

How to investigate, challenge and split a request lives in the personal `writing-tickets` skill. Without it: search the project for a duplicate, fill the template below, create the issue, reply with ID and link.

## Template

**Title:** imperative, ≤70 chars, no type prefix. `Reject measurements for a machine in another organization`, not `[Bug] Tenant check`.

**Description:**
```md
## Why
1–3 lines: the problem or the value. For a bug: steps → expected → actual.

## Done when
- Observable outcome, checkable from outside (an HTTP response, a row in the DB, a test that fails before the change)

## Notes
Pointers only: where to start (files, endpoints, commands, docs), constraints, assumptions, what's out of scope.
```
- `## Why` and `## Done when` are required. Omit `## Notes` when empty.
- "Done when" items are the tests and the definition of done: each one checkable through the API, the database or the worker, not an implementation step.
- An issue that changes the DB schema says so in Notes (it needs an Alembic migration).
- A doc that must change with it (`README.md`, `.env.example`): name it in Notes, not as a "Done when" item.
- Blocked-by goes in Linear's native relations, never in the description.
- Link, don't copy: name the file, endpoint, command or doc instead of pasting it.

## Fields
- **Type label** (exactly one), with the Conventional Commit it maps to: `Bug` → `fix:`, `Feature` → `feat:`, `Improvement` (refactor, deps, CI, tooling, docs, perf) → `refactor:` / `chore:` / `perf:` / `docs:`.
- **Milestone** (at most one): list them with `list_milestones` on the project. If none fits, ask before creating a new milestone.
- **Priority, estimate, assignee:** only if the user gives one.

## Never
- Put secrets, credentials or `.env` values in an issue, even redacted ones.
- Add sections, labels or fields beyond the above.
