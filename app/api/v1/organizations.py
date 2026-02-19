from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.organization import OrganizationCreate, OrganizationResponse, OrganizationUpdate
from app.services import organization_service

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("/", response_model=list[OrganizationResponse])
def get_organizations(db: Session = Depends(get_db)):
    """Get all organizations"""
    return organization_service.get_all(db)


@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(organization_id: UUID, db: Session = Depends(get_db)):
    """Retrieve a single organization by ID"""
    organization = organization_service.get_by_id(db, organization_id)

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with id '{organization_id}' not found",
        )

    return organization


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(payload: OrganizationCreate, db: Session = Depends(get_db)):
    """Create a new organization."""
    return organization_service.create(db, payload)


@router.patch("/{organization_id}", response_model=OrganizationResponse)
def update_organization(
    organization_id: UUID,
    payload: OrganizationUpdate,
    db: Session = Depends(get_db),
):
    """
    Partially update an organization.
    Only provided fields will be updated.
    """
    organization = organization_service.get_by_id(db, organization_id)

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with id '{organization_id}' not found",
        )

    return organization_service.update(db, organization, payload)


@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(organization_id: UUID, db: Session = Depends(get_db)):
    """Delete an organization."""
    organization = organization_service.get_by_id(db, organization_id)

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with id '{organization_id}' not found",
        )

    organization_service.delete(db, organization)
