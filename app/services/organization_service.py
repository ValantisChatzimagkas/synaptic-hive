from uuid import UUID

from sqlalchemy.orm import Session

from app.db.schema import Organization as OrganizationModel
from app.models.organization import OrganizationCreate, OrganizationUpdate


def get_all(db: Session) -> list[OrganizationModel] | None:
    """Fetch all organizations"""
    return db.query(OrganizationModel).all()


def get_by_id(db: Session, organization_id: UUID) -> OrganizationModel | None:
    """Fetch a single organization by ID. Returns None if not found."""
    return db.query(OrganizationModel).filter(OrganizationModel.id == organization_id).first()


def create(db: Session, payload: OrganizationCreate) -> OrganizationModel:
    """Create an organization"""
    organization = OrganizationModel(name=payload.name, is_active=payload.is_active)

    db.add(organization)
    db.commit()
    db.refresh(organization)
    return organization


def update(
    db: Session, organization: OrganizationModel, payload: OrganizationUpdate
) -> OrganizationModel:
    """
    Update an existing organization.
    Only updates fields that were explicitly provided
    """
    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(organization, field, value)

    db.commit()
    db.refresh(organization)
    return organization


def delete(db: Session, organization: OrganizationModel) -> None:
    """Delete Organization"""
    db.delete(organization)
    db.commit()
