# Synaptic Hive

[![CI](https://github.com/ValantisChatzimagkas/synaptic-hive/actions/workflows/ci.yml/badge.svg)](https://github.com/ValantisChatzimagkas/synaptic-hive/actions/workflows/ci.yml)

## Overview

Synaptic Hive is a multi-tenant industrial IoT monitoring backend. Organizations own factories, factories contain machines, and machines emit time-series measurements (voltage, current, RPM, torque and free-form metrics). Measurements are stored in a TimescaleDB hypertable and can be ingested either synchronously or asynchronously through a Redis Stream.

Stack: FastAPI, SQLAlchemy (sync), Alembic, TimescaleDB, Redis Streams, uv.

## Architecture

```mermaid
flowchart LR
    Client --> API[FastAPI]
    API -- "sync mode" --> DB[(TimescaleDB)]
    API -- "async mode" --> Stream[Redis Stream]
    Stream --> Worker[Worker]
    Worker --> DB
```

The API validates the request, looks up the machine and, depending on `INGESTION_MODE`, either writes the measurement directly or publishes it to a Redis Stream. The worker consumes the stream in batches and bulk-inserts into the `measurement_events` hypertable. Delivery is at-least-once: a batch is acknowledged only after it is committed, unacknowledged messages are retried, and inserts ignore `(machine_id, timestamp)` conflicts so retries do not create duplicates. Malformed messages are logged and dropped.

### Domain model

```
Organization
├── Factory (industry, location)
│   ├── Machine (type, manufacturer)
│   │   └── MeasurementEvent (voltage, current, rpm, torque, ...)
│   └── Machine
└── Factory
    └── Machine
```

## Getting started

Requires Docker with Compose.

```bash
docker compose up --build
```

This starts TimescaleDB, Redis, the API (which applies migrations on startup) and the ingestion worker. The API is at http://localhost:8000 and the interactive docs at http://localhost:8000/docs.

Credentials and published ports have defaults and can be overridden with environment variables (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `INGESTION_MODE`, `DB_PORT`, `API_PORT`, `REDIS_PORT`); see `.env.example`.

### Demo data

The scripts in `app/scripts` call the HTTP API, so the stack must be running. Run them from the host with [uv](https://docs.astral.sh/uv/):

```bash
uv sync

# Create an organization with factories and machines, then stream simulated measurements
uv run python -m app.scripts.run_simulation "Acme Manufacturing" --factories 2 --machines 3

# Only create the hierarchy
uv run python -m app.scripts.run_simulation "Acme Manufacturing" --setup-only

# Simulate a single existing machine
uv run python -m app.scripts.data_generator <machine-uuid> welding --duration 60
```

Use `--api-url` if the API is not on `http://localhost:8000`, and `--interval` / `--duration` to control the simulation.

## API overview

All routes are under `/api/v1`. Full request and response schemas are in the interactive docs at `/docs`.

| Resource | Routes |
|---|---|
| Organizations | `GET/POST /organizations`, `GET/PATCH/DELETE /organizations/{id}` |
| Factories | `GET/POST /factories` (filter by `organization_id`), `GET/PATCH/DELETE /factories/{id}` |
| Machines | `GET/POST /machines` (filter by `factory_id`, `organization_id`), `GET/PATCH/DELETE /machines/{id}` |
| Measurements | `POST /measurements` (ingest), `GET /measurements` (filter by machine, factory, organization, time range), `GET /measurements/statistics/{machine_id}` |

`POST /measurements` returns `202 Accepted` in async mode and `201 Created` in sync mode. A `GET /health` endpoint is also available.

## Running tests

The tests need a real PostgreSQL with TimescaleDB (a temporary `iot_db_test` database is created and dropped automatically). Redis is replaced by fakeredis, but `REDIS_URL` must still be set.

```bash
docker run -d --rm --name hive-testdb \
  -e POSTGRES_USER=iot_user -e POSTGRES_PASSWORD=iot_password -e POSTGRES_DB=iot_db \
  -p 5433:5432 timescale/timescaledb:latest-pg16

DATABASE_URL=postgresql://iot_user:iot_password@localhost:5433/iot_db \
REDIS_URL=redis://localhost:6379/0 \
uv run pytest -q

docker stop hive-testdb
```

CI runs `ruff check` and the same test suite against a TimescaleDB service container.

## Design decisions

**TimescaleDB hypertables.** Measurements are append-heavy and almost always queried by time range. `measurement_events` is converted to a hypertable (in an Alembic migration), which partitions it into time-based chunks so that time-bounded queries only touch the relevant chunks as data grows. The composite primary key `(machine_id, timestamp)` includes the partitioning column, as hypertables require.

**Sync vs async ingestion.** `INGESTION_MODE=sync` writes each measurement in the request, which is simple and gives immediate read-after-write. `INGESTION_MODE=async` (the default) publishes to a Redis Stream and returns `202`, decoupling request latency from database writes and letting the worker batch inserts. The trade-off is eventual consistency and an extra process to run. Both paths share one endpoint; only configuration changes.

**Denormalized measurements.** Each measurement row stores `organization_id`, `factory_id`, `factory_name`, `machine_name` and `machine_type` next to the machine ID. Hot read paths (listing and filtering by factory or organization, statistics) then need no joins against the relational tables. The cost is storage and stale names: renaming a machine or factory does not rewrite historical rows, which is acceptable for an event log.

## Limitations and roadmap

- **No authentication or authorization.** Tenants are separated by ID only: any caller can read or modify any organization's data by supplying its ID. The intended direction is per-organization API keys (for devices) and JWT-based user auth, with every query scoped to the caller's organization. Do not expose this API publicly in its current state.
- **No dashboard.** A web UI to browse organizations, factories, machines and their measurements is planned.
- **No anomaly detection.** Detecting early issues in machine behaviour from the measurement stream is a planned later step.
- Ingestion offers no deduplication beyond `(machine_id, timestamp)`; a single worker consumer is assumed.

## License

[MIT](LICENSE)
