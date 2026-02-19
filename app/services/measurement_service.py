from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.schema import MeasurementEvent as MeasurementModel
from app.models.measurement import MeasurementEventCreate, MeasurementStatistics


def create(
    db: Session,
    payload: MeasurementEventCreate,
    organization_id: UUID,
    machine_name: str,
    machine_type: str,
    factory_id: UUID,
    factory_name: str,
) -> MeasurementModel:
    """
    Create a new measurement event.
    All denormalized fields are provided by the router to avoid JOINs.
    """

    measurement = MeasurementModel(
        machine_id=payload.machine_id,
        timestamp=payload.timestamp or datetime.now(timezone.utc),
        organization_id=organization_id,
        voltage=payload.voltage,
        current=payload.current,
        rpm=payload.rpm,
        torque=payload.torque,
        additional_metrics=payload.additional_metrics,
        # Denormalized fields
        machine_name=machine_name,
        machine_type=machine_type,
        factory_id=factory_id,
        factory_name=factory_name,
    )
    db.add(measurement)
    db.commit()
    db.refresh(measurement)
    return measurement


def get_measurements(
    db: Session,
    machine_id: UUID | None = None,
    factory_id: UUID | None = None,
    organization_id: UUID | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    limit: int = 1000,
) -> list[MeasurementModel]:
    """
    Query measurements with filters.
    Optimized for time-series queries using TimescaleDB hypertable.
    """
    query = db.query(MeasurementModel)

    # Filter by entity hierarchy
    if machine_id:
        query = query.filter(MeasurementModel.machine_id == machine_id)
    elif factory_id:
        query = query.filter(MeasurementModel.factory_id == factory_id)
    elif organization_id:
        query = query.filter(MeasurementModel.organization_id == organization_id)

    # Time range filter (critical for time-series performance)
    if start_time:
        query = query.filter(MeasurementModel.timestamp >= start_time)
    if end_time:
        query = query.filter(MeasurementModel.timestamp <= end_time)

    # Order by time (newest first) and limit
    query = query.order_by(MeasurementModel.timestamp.desc()).limit(limit)

    return query.all()


def get_statistics(
    db: Session,
    machine_id: UUID,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> MeasurementStatistics | None:
    """
    Calculate aggregate statistics for a machine over a time range.
    Uses SQL aggregation for performance.
    """
    # Default to last 24 hours if no time range specified
    if not end_time:
        end_time = datetime.now(timezone.utc)
    if not start_time:
        start_time = end_time - timedelta(hours=24)

    query = (
        db.query(
            MeasurementModel.machine_id,
            MeasurementModel.machine_name,
            func.count().label("total_measurements"),
            # Voltage stats
            func.avg(MeasurementModel.voltage).label("voltage_avg"),
            func.min(MeasurementModel.voltage).label("voltage_min"),
            func.max(MeasurementModel.voltage).label("voltage_max"),
            # Current stats
            func.avg(MeasurementModel.current).label("current_avg"),
            func.min(MeasurementModel.current).label("current_min"),
            func.max(MeasurementModel.current).label("current_max"),
            # RPM stats
            func.avg(MeasurementModel.rpm).label("rpm_avg"),
            func.min(MeasurementModel.rpm).label("rpm_min"),
            func.max(MeasurementModel.rpm).label("rpm_max"),
            # Torque stats
            func.avg(MeasurementModel.torque).label("torque_avg"),
            func.min(MeasurementModel.torque).label("torque_min"),
            func.max(MeasurementModel.torque).label("torque_max"),
        )
        .filter(
            MeasurementModel.machine_id == machine_id,
            MeasurementModel.timestamp >= start_time,
            MeasurementModel.timestamp <= end_time,
        )
        .group_by(
            MeasurementModel.machine_id,
            MeasurementModel.machine_name,
        )
        .first()
    )

    if not query:
        return None

    return MeasurementStatistics(
        machine_id=query.machine_id,
        machine_name=query.machine_name,
        time_range_start=start_time,
        time_range_end=end_time,
        total_measurements=query.total_measurements,
        voltage_avg=query.voltage_avg,
        voltage_min=query.voltage_min,
        voltage_max=query.voltage_max,
        current_avg=query.current_avg,
        current_min=query.current_min,
        current_max=query.current_max,
        rpm_avg=query.rpm_avg,
        rpm_min=query.rpm_min,
        rpm_max=query.rpm_max,
        torque_avg=query.torque_avg,
        torque_min=query.torque_min,
        torque_max=query.torque_max,
    )
