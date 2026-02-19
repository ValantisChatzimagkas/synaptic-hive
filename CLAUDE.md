# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Synaptic Hive is a multi-tenant Industrial IoT monitoring platform built with FastAPI, TimescaleDB, and Redis. It manages a hierarchy of Organizations → Factories → Machines → MeasurementEvents, with time-series data optimized via TimescaleDB hypertables.

## Project purpose
* Showcase my data engineering and backend skills
* implement a solution that can handle a reasonable volume of data
* Support multi-tenancy concept by offering an easy way an organization can keep track of it's factories and machines inside these factories
* A later goal is to make it easy to check early issues regarding the production line and detecting anomalies in machines. ( like anomaly detection)
* I would eventually need authentication and maybe some Role Based Access enforcement and maybe protect in such way the endpoints (we must go that deep only if it really makes sense)
* After all the backend work is done I would like to build simple yet helpful frontend that can make it possible to inspect and interact the data an organization has under factories and machines in the factories, also some analytics section would be also nice to have.


## Coding standards
1. I want this to be as clean as possible and pragmatic without over-engineering or doing unecessary optimization or plans ahead, respect the YAGNI principle
2. The code should follow the SOLID software engineering coding standards, but must be reasonable when they really need to be applied and it must make sense
3. Code must be consistent in terms of patterns, design aspects and data types

## Common Commands

```bash
# Install dependencies
uv sync

# Start infrastructure (TimescaleDB + Redis)
docker-compose up -d

# Run database migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "description"

# Start dev server
uvicorn main:app --reload

# Run tests
pytest

# Run tests with coverage
pytest --cov --cov-report=term-missing

# Lint
ruff check .
ruff format .

# Generate test data
python -m app.scripts.setup_generator "OrgName" --factories 2 --machines 3
python -m app.scripts.data_generator
```

## Environment

Requires `.env` file with `DATABASE_URL` and `REDIS_URL`. Docker credentials go in `.env.docker`. Python 3.12+.

## Architecture

**Layered structure:**
- `app/api/v1/` — FastAPI route handlers (REST endpoints under `/api/v1`)
- `app/services/` — Business logic and database queries (one service per entity)
- `app/db/schema.py` — All SQLAlchemy ORM models in a single file
- `app/models/` — Pydantic request/response schemas (Base/Create/Update/Response pattern)
- `app/core/` — Config (Pydantic BaseSettings), dependencies, Redis client singleton
- `app/workers/` — Redis Stream consumers for async measurement ingestion
- `app/scripts/` — Data generation and simulation utilities

**Key patterns:**
- Sync SQLAlchemy with `get_db()` dependency for session lifecycle
- MeasurementEvent table is heavily denormalized (stores machine_name, factory_name, etc.) to avoid JOINs on time-series queries
- Composite PK `(machine_id, timestamp)` on MeasurementEvent for TimescaleDB hypertable optimization
- Single ingestion endpoint (`POST /measurements/`) with config-based routing: `INGESTION_MODE=async` queues via Redis Streams, `INGESTION_MODE=sync` writes directly to DB
- All entities use UUID primary keys
- Update endpoints use PATCH semantics with `model_dump(exclude_unset=True)`

**Pydantic schema convention:** Each entity has `*Base` (shared fields), `*Create` (POST body), `*Update` (all optional for PATCH), `*Response` (includes DB fields, `from_attributes=True`). Reusable annotated types live in `app/models/common.py`.

**Enums** (`app/enums.py`): `IndustryType` (automotive, metalworking, etc.) and `MachineType` (welding, press, lathe, etc.) shared across models and schemas.

## Linting

Ruff with 100-char line length. Rules: E, W, F, I, N, UP. E501 (line too long) is ignored.



## What I need from you
1. Enforce what has been specified in the coding standards section in a new branch and work there the refactoring needed
2. Make sure what we have done so far makes sense, is coherent, pragmatic and follows the best practices where they make sense (so that we don't overengineer and break YAGNI principle)
3. Tidy up things and enforce consistency and better organization of code and the project itself
4. I would ask you to help me in the things and steps I need to build in this project so that we break things step by step and progress with a steady pace.