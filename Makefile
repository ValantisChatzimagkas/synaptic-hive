.PHONY: help setup infra dev worker up down logs migrate migration fmt lint test check

.DEFAULT_GOAL := help

help:       ## list targets
	@grep -E '^[a-zA-Z_-]+:.*## ' $(firstword $(MAKEFILE_LIST)) | awk -F':.*## ' '{printf "%-10s %s\n", $$1, $$2}'

setup:      ## install deps from uv.lock and create .env from .env.example (skips an existing file)
	uv sync --locked
	@if [ -e .env ]; then echo ".env exists, skipped"; else cp .env.example .env && echo "created .env"; fi

infra:      ## start TimescaleDB and Redis only, wait until healthy
	docker compose up -d --wait timescaledb redis

dev: infra  ## infra + migrations + API with reload on :8000 (from source, reads .env)
	uv run alembic upgrade head
	uv run uvicorn main:app --reload

worker:     ## Redis Stream consumer (needed when INGESTION_MODE=async)
	uv run python -m app.workers.measurement_worker

up:         ## whole backend in Docker (TimescaleDB, Redis, API, worker)
	docker compose up --build

down:       ## stop the compose stack (keeps the data volumes)
	docker compose down

logs:       ## tail the compose stack's logs
	docker compose logs -f --tail=100

migrate:    ## apply database migrations
	uv run alembic upgrade head

migration:  ## make migration m="describe change"
	uv run alembic revision --autogenerate -m "$(m)"

fmt:        ## format and sort imports
	uv run ruff format .
	uv run ruff check --select I --fix .

lint:       ## ruff (format check + lint)
	uv run ruff format --check .
	uv run ruff check .

test:       ## pytest (needs TimescaleDB: `make infra`; creates and uses iot_db_test)
	uv run pytest

check: lint test  ## everything CI runs; must pass before a task is done
