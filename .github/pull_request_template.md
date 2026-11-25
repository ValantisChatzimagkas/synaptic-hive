<!--
Title: a Conventional Commit, imperative, ≤72 chars. On squash merge it becomes the commit on main.
  feat(ingestion): batch-insert measurements from the Redis Stream worker
Link the Linear issue below: "Fixes SOL-123" closes it on merge, "Part of SOL-123" only links it.
Delete these comments and any section marked optional when it's empty.
-->

Fixes SOL-

## Why
<!-- 1–3 lines: the problem or the value. Link the issue; don't restate it. -->

## What changed
<!-- Bullets a reviewer can check against the diff. Name what you reused, or why nothing fit. -->

## Verified
<!-- What you checked beyond CI (CI runs `make check` against TimescaleDB): requests against the running stack, a migration on real data, the worker draining a stream. -->

## Review focus (optional)
<!-- The risky part, a trade-off, or an open question. -->

## Flags (optional)
<!-- Keep only the lines that apply. -->
- New dependency: `name` (why, what it replaces)
- DB schema changed: migration `alembic/versions/<file>`, reversible / not reversible
- API contract changed (request/response shape, status codes): who calls it
- New env var, added to `.env.example`
- Follow-up: SOL-
