from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.common import ActiveFlag, AnyUUID, CreatedAt, ShortName


class OrganizationBase(BaseModel):
    """Shared fields for Organization schemas"""

    name: ShortName
    is_active: ActiveFlag = True


class OrganizationCreate(OrganizationBase):
    """
    Schema for creating an organization.
    Inherits name and is_active from base - both required except is_active which defaults to True.
    """

    pass


class OrganizationUpdate(BaseModel):
    """
    Schema for updating an organization.
    All fields optional - only provided fields will be updated (PATCH semantics).
    """

    name: Annotated[
        Optional[str], Field(min_length=1, max_length=255, description="Updated organization name")
    ] = None
    is_active: Annotated[Optional[bool], Field(description="Updated active status")] = None


class OrganizationResponse(OrganizationBase):
    """
    Schema for Organization API response.
    Extends base with DB-generated fields.
    """

    id: AnyUUID
    created_at: CreatedAt

    model_config = ConfigDict(from_attributes=True)
