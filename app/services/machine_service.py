from uuid import UUID

from sqlalchemy.orm import Session

from app.db.schema import Machine as MachineModel
from app.models.machine import MachineCreate, MachineUpdate


def get_all(db: Session, factory_id: UUID, organization_id: UUID) -> list[MachineModel] | None:
    """
    Fetch all machines.
    Optionally, filter by factory_id or organization_id
    """
    query = db.query(MachineModel)

    if factory_id:
        query = query.filter(MachineModel.factory_id == factory_id)

    if organization_id:
        query = query.filter(MachineModel.organization_id == organization_id)

    return query.all()


def get_by_id(db: Session, machine_id: UUID) -> MachineModel | None:
    """Fetch a single machine by ID. Returns None if not found"""

    return db.query(MachineModel).filter(MachineModel.id == machine_id).first()


def create(db: Session, payload: MachineCreate, organization_id: UUID) -> MachineModel:
    """
    Create a new machine.
    organization_id is denormalized from the parent factory
    """

    machine = MachineModel(
        factory_id=payload.factory_id,
        organization_id=organization_id,
        name=payload.name,
        machine_type=payload.machine_type,
        manufacturer=payload.manufacturer,
        model=payload.model,
        serial_number=payload.serial_number,
        meta=payload.meta,
    )
    db.add(machine)
    db.commit()
    db.refresh(machine)
    return machine


def update(db: Session, machine: MachineModel, payload: MachineUpdate) -> MachineModel:
    """
    Update an existing machine.
    Only updates fields that were explicitly provided.
    """

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(machine, field, value)

    db.commit()
    db.refresh(machine)
    return machine


def delete(db: Session, machine: MachineModel) -> None:
    """Delete a machine"""
    db.delete(machine)
    db.commit()
