"""convert measurement_events to a TimescaleDB hypertable

Revision ID: b7c2d9e4a1f5
Revises: af6e41d9c031
Create Date: 2026-11-22 12:00:00.000000

"""

from collections.abc import Sequence
from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b7c2d9e4a1f5"
down_revision: Union[str, Sequence[str], None] = "af6e41d9c031"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")
    op.execute(
        "SELECT create_hypertable('measurement_events', 'timestamp', "
        "if_not_exists => TRUE, migrate_data => TRUE)"
    )


def downgrade() -> None:
    # A hypertable cannot be converted back to a plain table in place;
    # the table itself is dropped by the initial migration's downgrade.
    pass
