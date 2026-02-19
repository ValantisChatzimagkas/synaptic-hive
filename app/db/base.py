# app/db/base.py
"""
Import all SQLAlchemy models here.
This ensures Alembic can discover them for migrations.
"""

from app.db.schema import Base

# Export Base for Alembic
__all__ = ["Base"]
