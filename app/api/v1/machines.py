from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.machine import MachineCreate, MachineResponse, MachineUpdate
from app.services import factory_service, machine_service

router = APIRouter(prefix="/machines", tags=["Machines"])


@router.get("/", response_model=list[MachineResponse])
def get_machines(
    factory_id: UUID = Query(None, description="Filter by factory by ID"),
    organization_id: UUID = Query(None, description="Filter by organization ID"),
    db: Session = Depends(get_db),
):
    """
    Retrieve all machines.
    Optionally filter by factory_id or organization_id
    """
    return machine_service.get_all(db, factory_id, organization_id)


@router.get("/{machine_id}", response_model=MachineResponse)
def get_machine(machine_id: UUID, db: Session = Depends(get_db)):
    """Retrieve a single machine by ID."""
    machine = machine_service.get_by_id(db, machine_id)
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with id '{machine_id}' not found",
        )
    return machine


@router.post("/", response_model=MachineResponse, status_code=status.HTTP_201_CREATED)
def create_machine(payload: MachineCreate, db: Session = Depends(get_db)):
    """Create a machine"""

    factory = factory_service.get_by_id(db, payload.factory_id)

    if not factory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Factory with id '{payload.factory_id}' not found",
        )

    return machine_service.create(db, payload, factory.organization_id)


@router.patch("/{machine_id}", response_model=MachineResponse)
def update_machine(machine_id: UUID, payload: MachineUpdate, db: Session = Depends(get_db)):
    """
    Partially update a machine.
    Only provided fields will be updated
    """

    machine = machine_service.get_by_id(db, machine_id)

    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with id '{machine_id}' not found",
        )

    return machine_service.update(db, machine, payload)


@router.delete("/{machine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_machine(machine_id: UUID, db: Session = Depends(get_db)):
    machine = machine_service.get_by_id(db, machine_id)

    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with id '{machine_id}' not found",
        )

    machine_service.delete(db, machine)
