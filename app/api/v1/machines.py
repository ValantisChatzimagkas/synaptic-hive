from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.anomaly import AnomalyEventResponse
from app.models.machine import MachineCreate, MachineResponse, MachineUpdate
from app.services import anomaly_service, factory_service, machine_service

router = APIRouter(tags=["Machines"])


@router.get("/factories/{factory_id}/machines", response_model=list[MachineResponse])
def get_machines(factory_id: UUID, db: Session = Depends(get_db)):
    """List all machines for a given factory."""
    if not factory_service.get_by_id(db, factory_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Factory with id '{factory_id}' not found",
        )
    return machine_service.get_all(db, factory_id=factory_id)


@router.post(
    "/factories/{factory_id}/machines",
    response_model=MachineResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_machine(factory_id: UUID, payload: MachineCreate, db: Session = Depends(get_db)):
    """Create a machine under a factory."""
    factory = factory_service.get_by_id(db, factory_id)
    if not factory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Factory with id '{factory_id}' not found",
        )
    return machine_service.create(db, payload, factory_id, factory.organization_id)


@router.get("/machines/{machine_id}", response_model=MachineResponse)
def get_machine(machine_id: UUID, db: Session = Depends(get_db)):
    """Retrieve a single machine by ID."""
    machine = machine_service.get_by_id(db, machine_id)
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with id '{machine_id}' not found",
        )
    return machine


@router.patch("/machines/{machine_id}", response_model=MachineResponse)
def update_machine(machine_id: UUID, payload: MachineUpdate, db: Session = Depends(get_db)):
    """Partially update a machine. Only provided fields will be updated."""
    machine = machine_service.get_by_id(db, machine_id)
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with id '{machine_id}' not found",
        )
    return machine_service.update(db, machine, payload)


@router.delete("/machines/{machine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_machine(machine_id: UUID, db: Session = Depends(get_db)):
    """Delete a machine."""
    machine = machine_service.get_by_id(db, machine_id)
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with id '{machine_id}' not found",
        )
    machine_service.delete(db, machine)


@router.get("/machines/{machine_id}/anomalies", response_model=list[AnomalyEventResponse])
def get_machine_anomalies(
    machine_id: UUID,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List anomaly events detected for a machine."""
    if not machine_service.get_by_id(db, machine_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with id '{machine_id}' not found",
        )
    return anomaly_service.get_anomalies(db, machine_id, start_time, end_time, limit)
