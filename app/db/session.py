"""
Database engine and session configuration.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# Alembic already stripped +asyncpg, but here we use
# the sync driver directly since we're using sync SQLAlchemy
SYNC_DATABASE_URL = settings.DATABASE_URL.replace("+asyncpg", "")

engine = create_engine(
    SYNC_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verifies connection is alive before using it
    echo=settings.DEBUG,  # Logs SQL queries when DEBUG=true - useful now
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


def get_db():
    """
    FastAPI dependency that provides a database session.
    Automatically closes the session when the request is done.

    Usage in endpoints:
        @router.get("/something")
        def my_endpoint(db: Session = Depends(get_db)):
            ...
    """
    db: Session = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
