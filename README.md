# Synaptic Hive

A multi-tenant Industrial IoT monitoring platform built with FastAPI, TimescaleDB, and Redis.

## What is this?

Synaptic Hive manages a hierarchy of **Organizations > Factories > Machines > Measurements**, with time-series data optimized via TimescaleDB hypertables. It supports dual ingestion paths (synchronous and async via Redis Streams) and is designed for high-throughput machine telemetry.

## Tech Stack

- **FastAPI** - REST API framework
- **TimescaleDB** - Time-series optimized PostgreSQL
- **Redis** - Async measurement ingestion via Streams
- **SQLAlchemy** - ORM with sync sessions
- **Pydantic** - Request/response validation
- **Alembic** - Database migrations

## Architecture

```
Organization
├── Factory (industry, location)
│   ├── Machine (type, manufacturer)
│   │   └── MeasurementEvent (voltage, current, rpm, torque, ...)
│   └── Machine
└── Factory
    └── Machine
```

**Layered structure:**
- `app/api/v1/` - REST route handlers
- `app/services/` - Business logic and database queries
- `app/db/schema.py` - SQLAlchemy ORM models
- `app/models/` - Pydantic request/response schemas
- `app/core/` - Config, dependencies, Redis client
- `app/workers/` - Redis Stream consumers for async ingestion
- `app/scripts/` - Data generation and simulation utilities

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (package manager)
- Docker & Docker Compose

### Setup

```bash
# 1. Clone the repo
git clone <repo-url> && cd synaptic-hive

# 2. Install dependencies
uv sync

# 3. Configure environment
cp .env.example .env
# Edit .env if you need to change defaults

# 4. Start infrastructure (TimescaleDB + Redis)
docker-compose up -d

# 5. Run database migrations
alembic upgrade head

# 6. Start the dev server
uvicorn main:app --reload
```

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL/TimescaleDB connection string | `postgresql://iot_user:iot_password@localhost:5432/iot_db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |

Docker credentials are configured separately in `.env.docker`.

## Generating Test Data

### Quick Start (all-in-one)

Creates the hierarchy and starts sending simulated measurements:

```bash
python -m app.scripts.run_simulation "Siemens Manufacturing" --factories 2 --machines 3
```

### Setup Only (hierarchy without measurements)

```bash
python -m app.scripts.run_simulation "Siemens Manufacturing" --factories 2 --machines 3 --setup-only
```

### Individual Scripts

**Setup generator** - create org/factory/machine hierarchy:
```bash
python -m app.scripts.setup_generator "Siemens Manufacturing" --factories 2 --machines 3
```

**Data generator** - simulate measurements for a single machine:
```bash
python -m app.scripts.data_generator <machine-uuid> welding --interval 1.0 --duration 60
```

### Simulation Options

| Flag | Description | Default |
|---|---|---|
| `--factories` | Number of factories to create | 2 |
| `--machines` | Machines per factory | 3 |
| `--interval` | Seconds between measurements | 1.0 |
| `--duration` | Total runtime in seconds | Continuous |
| `--setup-only` | Only create hierarchy, skip measurements | Off |
| `--api-url` | API base URL | `http://localhost:8000` |

## API Endpoints

All endpoints are prefixed with `/api/v1`.

### Organizations

| Method | Path | Description |
|---|---|---|
| `GET` | `/organizations` | List all organizations |
| `GET` | `/organizations/{id}` | Get organization by ID |
| `POST` | `/organizations` | Create organization |
| `PATCH` | `/organizations/{id}` | Update organization |
| `DELETE` | `/organizations/{id}` | Delete organization |

### Factories

| Method | Path | Description |
|---|---|---|
| `GET` | `/factories` | List all factories (filter by `organization_id`) |
| `GET` | `/factories/{id}` | Get factory by ID |
| `POST` | `/factories` | Create factory |
| `PATCH` | `/factories/{id}` | Update factory |
| `DELETE` | `/factories/{id}` | Delete factory |

### Machines

| Method | Path | Description |
|---|---|---|
| `GET` | `/machines` | List all machines (filter by `factory_id`, `organization_id`) |
| `GET` | `/machines/{id}` | Get machine by ID |
| `POST` | `/machines` | Create machine |
| `PATCH` | `/machines/{id}` | Update machine |
| `DELETE` | `/machines/{id}` | Delete machine |

### Measurements

| Method | Path | Description |
|---|---|---|
| `GET` | `/measurements` | Query measurements (filter by machine, factory, org, time range) |
| `POST` | `/measurements` | Ingest measurement (synchronous) |
| `POST` | `/measurements/async` | Ingest measurement (async via Redis Stream) |
| `GET` | `/measurements/statistics/{machine_id}` | Aggregate stats (min/max/avg) for a machine |

## Development

```bash
# Lint and format
ruff check .
ruff format .

# Create a new migration
alembic revision --autogenerate -m "description"

# Run tests
pytest
```
