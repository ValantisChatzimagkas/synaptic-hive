"""
Test fixtures: real PostgreSQL database with transaction rollback isolation,
fakeredis for Redis, and TestClient wired to both.
"""

import fakeredis
import psycopg2
import pytest
from fastapi.testclient import TestClient
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.schema import Base, Factory, Machine, Organization
from app.db.session import get_db
from app.enums import IndustryType, MachineType

# ---------------------------------------------------------------------------
# Derive test database URL from the main DATABASE_URL
# ---------------------------------------------------------------------------
_base_url = settings.DATABASE_URL.replace("+asyncpg", "")
# Replace the database name at the end of the URL
_parts = _base_url.rsplit("/", 1)
TEST_DATABASE_URL = f"{_parts[0]}/iot_db_test"

# Connection params for creating/dropping the test database
_admin_url = f"{_parts[0]}/postgres"


def _create_test_database():
    """Create the iot_db_test database if it doesn't exist."""
    conn = psycopg2.connect(_admin_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'iot_db_test'")
    if not cur.fetchone():
        cur.execute("CREATE DATABASE iot_db_test")
    cur.close()
    conn.close()


def _drop_test_database():
    """Drop the iot_db_test database."""
    conn = psycopg2.connect(_admin_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("DROP DATABASE IF EXISTS iot_db_test WITH (FORCE)")
    cur.close()
    conn.close()


# ---------------------------------------------------------------------------
# Session-scoped engine: create tables once per test session
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def test_engine():
    _create_test_database()
    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    _drop_test_database()


# ---------------------------------------------------------------------------
# Function-scoped session with transaction rollback
# ---------------------------------------------------------------------------
@pytest.fixture()
def db_session(test_engine):
    """
    Each test gets a session wrapped in a transaction that is rolled back
    at the end. Services calling db.commit() hit a savepoint instead of
    a real commit, so isolation is maintained.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    # When the app code calls session.commit(), restart a nested savepoint
    # so the outer transaction stays open for rollback.
    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, trans):
        nonlocal nested
        if trans.nested and not trans._parent.nested:
            nested = connection.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# ---------------------------------------------------------------------------
# Fake Redis
# ---------------------------------------------------------------------------
@pytest.fixture()
def fake_redis():
    return fakeredis.FakeRedis(decode_responses=True)


# ---------------------------------------------------------------------------
# TestClient with dependency overrides
# ---------------------------------------------------------------------------
@pytest.fixture()
def client(db_session, fake_redis):
    from app.core import redis_client as redis_module
    from main import app

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    # Patch the Redis singleton's client
    original_client = redis_module.redis_client._client
    redis_module.redis_client._client = fake_redis

    with TestClient(app) as tc:
        yield tc

    app.dependency_overrides.clear()
    redis_module.redis_client._client = original_client


# ---------------------------------------------------------------------------
# Entity fixtures
# ---------------------------------------------------------------------------
@pytest.fixture()
def sample_organization(db_session):
    org = Organization(name="Test Organization")
    db_session.add(org)
    db_session.flush()
    return org


@pytest.fixture()
def sample_factory(db_session, sample_organization):
    factory = Factory(
        organization_id=sample_organization.id,
        name="Test Factory",
        industry=IndustryType.AUTOMOTIVE,
        country_code="DE",
        city="Munich",
        postal_code="80331",
    )
    db_session.add(factory)
    db_session.flush()
    return factory


@pytest.fixture()
def sample_machine(db_session, sample_factory):
    machine = Machine(
        factory_id=sample_factory.id,
        organization_id=sample_factory.organization_id,
        name="Test Welding Robot",
        machine_type=MachineType.WELDING,
        manufacturer="KUKA",
        model="KR 16",
        serial_number="TEST-SN-001",
    )
    db_session.add(machine)
    db_session.flush()
    return machine
