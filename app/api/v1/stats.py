from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.schema import AnomalyEvent, Factory, Machine, MeasurementEvent, Organization
from app.db.session import get_db

router = APIRouter(prefix="/stats", tags=["Stats"])


class PlatformStats(BaseModel):
    organizations: int
    factories: int
    machines: int
    measurements_24h: int


class HourlyMeasurements(BaseModel):
    hour: datetime
    count: int


class MachineAnomalyCount(BaseModel):
    machine_id: str
    machine_name: str
    factory_name: str
    organization_name: str
    count: int


class ActivityStats(BaseModel):
    hourly_measurements: list[HourlyMeasurements]
    top_anomalous_machines: list[MachineAnomalyCount]


@router.get("/", response_model=PlatformStats)
def get_stats(db: Session = Depends(get_db)):
    """Return platform-wide aggregate counts."""
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    return PlatformStats(
        organizations=db.query(Organization).count(),
        factories=db.query(Factory).count(),
        machines=db.query(Machine).count(),
        measurements_24h=db.query(MeasurementEvent)
        .filter(MeasurementEvent.timestamp >= since)
        .count(),
    )


@router.get("/activity", response_model=ActivityStats)
def get_activity(db: Session = Depends(get_db)):
    """Return hourly measurement counts and top anomalous machines for the last 24h."""
    since = datetime.now(timezone.utc) - timedelta(hours=24)

    hourly = (
        db.query(
            func.date_trunc("hour", MeasurementEvent.timestamp).label("hour"),
            func.count().label("count"),
        )
        .filter(MeasurementEvent.timestamp >= since)
        .group_by(func.date_trunc("hour", MeasurementEvent.timestamp))
        .order_by(func.date_trunc("hour", MeasurementEvent.timestamp))
        .all()
    )

    top_machines = (
        db.query(
            AnomalyEvent.machine_id,
            Machine.name.label("machine_name"),
            Factory.name.label("factory_name"),
            Organization.name.label("organization_name"),
            func.count().label("count"),
        )
        .join(Machine, Machine.id == AnomalyEvent.machine_id)
        .join(Factory, Factory.id == Machine.factory_id)
        .join(Organization, Organization.id == Factory.organization_id)
        .filter(AnomalyEvent.timestamp >= since)
        .group_by(AnomalyEvent.machine_id, Machine.name, Factory.name, Organization.name)
        .order_by(func.count().desc())
        .limit(5)
        .all()
    )

    return ActivityStats(
        hourly_measurements=[HourlyMeasurements(hour=r.hour, count=r.count) for r in hourly],
        top_anomalous_machines=[
            MachineAnomalyCount(
                machine_id=str(r.machine_id),
                machine_name=r.machine_name,
                factory_name=r.factory_name,
                organization_name=r.organization_name,
                count=r.count,
            )
            for r in top_machines
        ],
    )
