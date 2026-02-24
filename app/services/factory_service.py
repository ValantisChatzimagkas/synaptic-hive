from uuid import UUID

from sqlalchemy.orm import Session

from app.db.schema import Factory as FactoryModel
from app.models.factory import FactoryCreate, FactoryUpdate


def get_all(db: Session, organization_id: UUID | None) -> list[FactoryModel] | None:
    """Fetch all factories.
    If `organization_id` is provided, fetch all factories for given organization
    """
    query = db.query(FactoryModel)

    if organization_id:
        query = query.filter(FactoryModel.organization_id == organization_id)
    return query.all()


def get_by_id(db: Session, factory_id: UUID) -> FactoryModel | None:
    """Fetch a factory by it's id"""
    return db.query(FactoryModel).filter(FactoryModel.id == factory_id).first()


def create(db: Session, payload: FactoryCreate, organization_id: UUID):
    """Create a new factory"""
    factory = FactoryModel(
        organization_id=organization_id,
        name=payload.name,
        industry=payload.industry,
        country_code=payload.country_code,
        city=payload.city,
        postal_code=payload.postal_code,
        latitude=payload.latitude,
        longitude=payload.longitude,
        is_active=payload.is_active,
    )

    db.add(factory)
    db.commit()
    db.refresh(factory)
    return factory


def update(db: Session, factory: FactoryModel, payload: FactoryUpdate) -> FactoryModel:
    """
    Update an existing factory.
    Only updates fields that were explicitly provided
    """
    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(factory, field, value)

    db.commit()
    db.refresh(factory)
    return factory


def delete(db: Session, factory: FactoryModel) -> None:
    """Delete a factory"""
    db.delete(factory)
    db.commit()
