# Synaptic Hive

Multi-tenant industrial IoT monitoring backend: FastAPI, TimescaleDB, Redis Streams. Organizations → Factories → Machines → MeasurementEvents, with measurements in a TimescaleDB hypertable. A portfolio project to show data engineering and backend skills on a realistic data volume. The plan and issues live in the Linear project **Synaptic Hive** (team `SOL`); break work into small steps and progress at a steady pace.

## Purpose and direction
- Multi-tenancy: an organization keeps track of its factories and the machines in them.
- Later: spot early production-line issues and machine anomalies (anomaly detection).
- Authentication and role-based access only when it really makes sense; today there is none (see README, Limitations).
- After the backend: a simple frontend to inspect and interact with an organization's data, plus an analytics section.

## Commands
- `make help` → every target. `make setup` → `uv sync --locked` + `.env` from `.env.example`.
- `make check` → lint and tests, exactly what CI runs. **Must pass before you call a task done.** Tests need TimescaleDB: `make infra` first.
- `make fmt` → format + sort imports. One test: `uv run pytest tests/test_machines.py -k create`.
- `make dev` → TimescaleDB + Redis in Docker, migrations, API with reload on :8000. `make worker` → stream consumer. `make up` → whole stack in Docker.
- `make migration m="..."` / `make migrate` → Alembic. Never edit an applied migration; add a new one.
- Deps: `uv add <pkg>` / `uv add --dev <pkg>`; never edit `uv.lock` by hand.
- Demo data: `uv run python -m app.scripts.run_simulation "Acme Manufacturing" --factories 2 --machines 3` (stack must be running).

## Layout
- `app/api/v1/` route handlers (REST under `/api/v1`). `app/services/` business logic and queries, one service per entity.
- `app/db/schema.py` all SQLAlchemy ORM models. `app/models/` Pydantic request/response schemas; shared annotated types in `app/models/common.py`.
- `app/enums.py` `IndustryType`, `MachineType`. `app/core/` config (Pydantic `BaseSettings`), dependencies, Redis client.
- `app/workers/` Redis Stream consumers. `app/scripts/` demo-data generators that call the HTTP API.
- `alembic/` migrations. `tests/` pytest against a real `iot_db_test` database with transaction rollback; Redis is `fakeredis`.

## Key patterns
- Sync SQLAlchemy; `get_db()` dependency owns the session lifecycle. All entities use UUID primary keys.
- Schemas per entity: `*Base` (shared fields), `*Create` (POST body), `*Update` (all optional, PATCH with `model_dump(exclude_unset=True)`), `*Response` (DB fields, `from_attributes=True`).
- `MeasurementEvent` is denormalized (machine/factory names) to avoid joins on time-series queries; composite PK `(machine_id, timestamp)` for the hypertable.
- One ingestion endpoint (`POST /measurements/`); `INGESTION_MODE=async` publishes to a Redis Stream, `sync` writes directly. The worker acks only after commit and inserts ignore `(machine_id, timestamp)` conflicts: at-least-once without duplicates. Keep it that way.
- No authentication yet: tenant scoping is by ID only.

## Coding standards
- Clean and pragmatic. YAGNI: no over-engineering, no premature optimization, no "for later" code.
- SOLID where it earns its keep, not by reflex.
- Consistent patterns, design and data types across entities: a new entity looks like the existing ones.

## Before writing code: extend, don't add
- Search before adding a function, schema, service, dependency or fixture; extend the closest one. Name what you reused, or why nothing fit.
- Smallest diff that solves the task. No drive-by refactors, speculative abstractions or config flags. Extract a helper on the second real use. Delete dead code.
- **New dependency, new top-level folder or new infrastructure service: propose it first** and say what code or risk it removes; put the why in the commit.
- ORM change → Alembic migration in the same commit (`make migration`), reviewed by hand before committing.

## Tests
- Test through the HTTP API (`TestClient`) or the public function someone calls, not private helpers. No mocks of our own code.
- New behaviour or bug fix gets a test that fails before the change. Variants of one rule go in one `pytest.mark.parametrize` table.

## Docs: one home per fact, fixed in the same commit
- `README.md`: what it is, how to run it, limitations. `CLAUDE.md`: rules for changing code. `.env.example`: env vars. `Makefile`: commands. Docs link to these; they don't copy them.
- A change that makes a doc wrong fixes it in the same commit. Keep this file under ~100 lines: cut a stale rule before adding one.

## Gotchas
- Running from source needs `DATABASE_URL` and `REDIS_URL` (`.env`, see `.env.example`); Compose builds its own from `POSTGRES_*`. Ports come from `DB_PORT`, `API_PORT`, `REDIS_PORT`: set `DB_PORT` if 5432 is taken, and match `DATABASE_URL`.
- Ruff: 100-char lines, rules E, W, F, I, N, UP, E501 ignored.

## Agent setup (`.claude/`)
- `settings.json`: `.env` unreadable, `uv.lock` not hand-editable, Python auto-formatted on edit, `make lint` re-run when you stop, and `hooks/block-dangerous-git.sh` blocks pushes to `main`, force-push, `reset --hard`, `clean -f`, `branch -D` and `checkout .`/`restore .`.
- After a non-trivial change, run the `reviewer` agent on the diff and fix what it finds.
- Linear issues only through the `linear-issue` skill; PRs only through the `pull-request` skill.

## Commits
Conventional Commits with the issue ID: `feat(ingestion): batch stream inserts (SOL-123)`. Small and focused. Never commit `.env`.
