FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# psycopg2 is built from source and needs a compiler and libpq headers
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libc6-dev libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Install dependencies first so this layer is cached until the lockfile changes
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project


FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /app/.venv .venv
COPY alembic.ini main.py ./
COPY alembic alembic
COPY app app

ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1

# Default process is the API; the compose "worker" service overrides the command.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
