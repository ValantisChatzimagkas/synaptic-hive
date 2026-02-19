from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Import your settings and models
from app.core.config import settings
from app.db.schema import Base  # All models must be imported via Base

# Alembic Config object
config = context.config

# Set the database URL from your settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("+asyncpg", ""))
# Note: Alembic uses sync driver, so we strip +asyncpg

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Your metadata - Alembic uses this to detect schema changes
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
