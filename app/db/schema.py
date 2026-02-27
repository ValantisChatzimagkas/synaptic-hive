"""
SQLAlchemy ORM models for TimescaleDB.
These represent the actual database tables.
"""

from datetime import datetime
from uuid import UUID as UUID_TYPE
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.enums import IndustryType, MachineType

# ========================= BASE =========================


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""

    pass


# ========================= MAIN ENTITIES =========================


class Organization(Base):
    """The top-level multi-tenant entity. One org has many factories."""

    __tablename__ = "organizations"

    id: Mapped[UUID_TYPE] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    factories = relationship("Factory", back_populates="organization", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}')>"


class Factory(Base):
    """A physical facility belonging to an organization."""

    __tablename__ = "factories"

    id: Mapped[UUID_TYPE] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID_TYPE] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[str] = mapped_column(SQLEnum(IndustryType, native_enum=False), nullable=False)

    # Location
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)

    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    organization = relationship("Organization", back_populates="factories")
    machines = relationship("Machine", back_populates="factory", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_factory_org_id", "organization_id"),
        Index("idx_factory_location", "country_code", "city"),
    )

    def __repr__(self):
        return f"<Factory(id={self.id}, name='{self.name}')>"


class Machine(Base):
    """A machine located inside a factory."""

    __tablename__ = "machines"

    id: Mapped[UUID_TYPE] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    factory_id: Mapped[UUID_TYPE] = mapped_column(
        UUID(as_uuid=True), ForeignKey("factories.id", ondelete="CASCADE"), nullable=False
    )
    organization_id: Mapped[UUID_TYPE] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    machine_type: Mapped[str] = mapped_column(
        SQLEnum(MachineType, native_enum=False), nullable=False
    )
    manufacturer: Mapped[str] = mapped_column(String(100), nullable=True)
    model: Mapped[str] = mapped_column(String(100), nullable=True)
    serial_number: Mapped[str] = mapped_column(String(100), nullable=True, unique=True)

    installed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False, server_default="{}")

    # Relationships
    factory = relationship("Factory", back_populates="machines")
    anomalies = relationship("AnomalyEvent", back_populates="machine", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_machine_factory_id", "factory_id"),
        Index("idx_machine_org_id", "organization_id"),
        Index("idx_machine_type", "machine_type"),
    )

    def __repr__(self):
        return f"<Machine(id={self.id}, name='{self.name}', type={self.machine_type})>"


class MeasurementEvent(Base):
    """
    Time-series measurement events from machines.
    Wide table: one row per timestamp per machine.
    """

    __tablename__ = "measurement_events"

    # Composite primary key (machine + time = unique moment)
    machine_id: Mapped[UUID_TYPE] = mapped_column(
        UUID(as_uuid=True), nullable=False, primary_key=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, primary_key=True, server_default=func.now()
    )

    # Multi-tenant boundary
    organization_id: Mapped[UUID_TYPE] = mapped_column(UUID(as_uuid=True), nullable=False)

    # Electrical measurements (welding, press, assembly)
    voltage: Mapped[float] = mapped_column(Float, nullable=True)  # Volts
    current: Mapped[float] = mapped_column(Float, nullable=True)  # Amperes

    # Mechanical measurements (lathe, conveyor)
    rpm: Mapped[int] = mapped_column(Integer, nullable=True)  # Revolutions per minute
    torque: Mapped[float] = mapped_column(Float, nullable=True)  # Newton-metres

    # Flexible catch-all for future metrics
    additional_metrics: Mapped[dict] = mapped_column(
        JSONB, default=dict, nullable=False, server_default="{}"
    )

    # Denormalized fields (fast analytics without JOINs)
    machine_name: Mapped[str] = mapped_column(String(255), nullable=False)
    machine_type: Mapped[str] = mapped_column(String(50), nullable=False)
    factory_id: Mapped[UUID_TYPE] = mapped_column(UUID(as_uuid=True), nullable=False)
    factory_name: Mapped[str] = mapped_column(String(255), nullable=False)

    __table_args__ = (
        Index("idx_measurement_org_id", "organization_id"),
        Index("idx_measurement_machine_id", "machine_id"),
        Index("idx_measurement_factory_id", "factory_id"),
    )

    def __repr__(self):
        return f"<MeasurementEvent(machine_id={self.machine_id}, timestamp={self.timestamp})>"


class AnomalyEvent(Base):
    __tablename__ = "anomaly_events"

    machine_id: Mapped[UUID_TYPE] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("machines.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, primary_key=True, server_default=func.now()
    )
    metric: Mapped[str] = mapped_column(String(60), nullable=False, primary_key=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    detector: Mapped[str] = mapped_column(String(100), nullable=False)

    # relationship
    machine = relationship("Machine", back_populates="anomalies")
