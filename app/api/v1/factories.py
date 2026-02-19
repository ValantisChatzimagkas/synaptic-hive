from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.factory import FactoryCreate, FactoryResponse, FactoryUpdate
from app.services import factory_service, organization_service

router = APIRouter(prefix="/factories", tags=["Factories"])


@router.get("/", response_model=list[FactoryResponse])
def get_factories(
    organization_id: UUID | None = Query(None, description="Filter by organization ID"),
    db: Session = Depends(get_db),
):
    """
    Retrieve all factories.
    Optionally filter by organization_id.
    """
    return factory_service.get_all(db, organization_id=organization_id)


@router.get("/{factory_id}", response_model=FactoryResponse)
def get_factory(factory_id: UUID, db: Session = Depends(get_db)):
    """Retrieve a single factory by ID"""
    factory = factory_service.get_by_id(db, factory_id)

    if not factory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Factory with id '{factory_id}' not found",
        )

    return factory


@router.post("/", response_model=FactoryResponse, status_code=status.HTTP_201_CREATED)
def create_factory(payload: FactoryCreate, db: Session = Depends(get_db)):
    """Create a new factory"""
    organization = organization_service.get_by_id(db, payload.organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with id '{payload.organization_id}' not found",
        )

    return factory_service.create(db, payload)


@router.patch("/{factory_id}", response_model=FactoryResponse)
def update_factory(factory_id: UUID, payload: FactoryUpdate, db: Session = Depends(get_db)):
    """Partially update a factory, only provided fields from payload will be updated"""

    factory = factory_service.get_by_id(db, factory_id)

    if not factory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Factory with id '{factory_id}' not found",
        )

    return factory_service.update(db, factory, payload)


@router.delete("/{factory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_factory(factory_id: UUID, db: Session = Depends(get_db)):
    """Delete a factory"""
    factory = factory_service.get_by_id(db, factory_id)

    if not factory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Factory with id '{factory_id}' not found",
        )

    factory_service.delete(db, factory)
