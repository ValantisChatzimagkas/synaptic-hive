from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.schema import Factory, Machine, MeasurementEvent, Organization
from app.db.session import get_db

router = APIRouter(prefix="/stats", tags=["Stats"])


class PlatformStats(BaseModel):
    organizations: int
    factories: int
    machines: int
    measurements_24h: int


@router.get("/", response_model=PlatformStats)
def get_stats(db: Session = Depends(get_db)):
    """Return platform-wide aggregate counts."""
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    return PlatformStats(
        organizations=db.query(Organization).count(),
        factories=db.query(Factory).count(),
        machines=db.query(Machine).count(),
        measurements_24h=db.query(MeasurementEvent).filter(MeasurementEvent.timestamp >= since).count(),
    )
