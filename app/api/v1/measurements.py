from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.measurement import (
    MeasurementEventCreate,
    MeasurementEventResponse,
    MeasurementStatistics,
)
from app.services import machine_service, measurement_service, redis_service

router = APIRouter(prefix="/measurements", tags=["Measurements"])


@router.get("/", response_model=list[MeasurementEventResponse])
def get_measurement(
    machine_id: UUID | None = Query(None, description="Filter by machine"),
    factory_id: UUID | None = Query(None, description="Filter by factory"),
    organization_id: UUID | None = Query(None, description="Filter by organization"),
    start_time: datetime | None = Query(None, description="Start of time range (ISO 8601)"),
    end_time: datetime | None = Query(None, description="End of time range (ISO 8601)"),
    limit: int = Query(1000, ge=1, le=1000, description="Max results to return"),
    db: Session = Depends(get_db),
):
    """
    Query measurements with various filters.
    Optimized for time-series queries on TimescaleDB hypertable.
    """
    return measurement_service.get_measurements(
        db,
        machine_id=machine_id,
        factory_id=factory_id,
        organization_id=organization_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
    )


@router.post("/")
def ingest_measurement(payload: MeasurementEventCreate, db: Session = Depends(get_db)):
    """
    Ingest a single measurement event.

    Routing is controlled by the INGESTION_MODE setting:
    - "async": publishes to Redis Stream for background processing (returns 202)
    - "sync": writes directly to TimescaleDB (returns 201)
    """
    machine = machine_service.get_by_id(db, payload.machine_id)
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with id '{payload.machine_id}' not found",
        )

    denormalized_data = {
        "organization_id": str(machine.organization_id),
        "machine_name": machine.name,
        "machine_type": machine.machine_type,
        "factory_id": str(machine.factory_id),
        "factory_name": machine.factory.name,
    }

    if settings.INGESTION_MODE == "async":
        message_id = redis_service.publish_measurement(
            machine_id=payload.machine_id,
            measurement_payload=payload,
            denormalized_data=denormalized_data,
        )
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "status": "accepted",
                "message": "Measurement queued for processing",
                "redis_message_id": message_id,
            },
        )

    measurement = measurement_service.create(
        db,
        payload,
        organization_id=machine.organization_id,
        machine_name=machine.name,
        machine_type=machine.machine_type,
        factory_id=machine.factory_id,
        factory_name=machine.factory.name,
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=MeasurementEventResponse.model_validate(measurement).model_dump(mode="json"),
    )


@router.get("/statistics/{machine_id}", response_model=MeasurementStatistics)
def get_machine_statistics(
    machine_id: UUID,
    start_time: datetime | None = Query(
        None, description="Start of time range (defaults to 24h ago)"
    ),
    end_time: datetime | None = Query(None, description="End of time range (defaults to now)"),
    db: Session = Depends(get_db),
):
    """
    Get aggregate statistics for a machine over a time range.
    Returns min/max/avg for all measurement types.
    """
    stats = measurement_service.get_statistics(db, machine_id, start_time, end_time)

    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No measurements found for machine '{machine_id}' in the specified time range",
        )

    return stats
