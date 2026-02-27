from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.enums import MachineType
from app.models.common import AnyUUID, FactoryId, InstalledAt, OrganizationId, ShortName


class MachineBase(BaseModel):
    """Shared fields for Machine schemas"""

    name: ShortName
    machine_type: MachineType
    manufacturer: Annotated[
        Optional[str], Field(max_length=100, description="Machine manufacturer")
    ] = None
    model: Annotated[Optional[str], Field(max_length=100, description="Machine model")] = None
    serial_number: Annotated[
        Optional[str], Field(max_length=100, description="Unique serial number")
    ] = None
    meta: Annotated[dict, Field(default_factory=dict, description="Metadata as JSONB")]


class MachineCreate(MachineBase):
    """Schema for creating a machine. factory_id is provided via the URL path."""

    pass


class MachineUpdate(MachineBase):
    """
    Schema for updating a machine.
    All fields optional - only provided fields will be updated (PATCH semantics)
    """

    name: Annotated[Optional[str], Field(min_length=1, max_length=255)] = None
    machine_type: Optional[MachineType] = None
    manufacturer: Annotated[Optional[str], Field(max_length=100)] = None
    model: Annotated[Optional[str], Field(max_length=100)] = None
    serial_number: Annotated[Optional[str], Field(max_length=100)] = None
    meta: Optional[dict] = None


class MachineResponse(MachineBase):
    """
    Schema for Machine API response.
    """

    id: AnyUUID
    factory_id: FactoryId
    organization_id: OrganizationId
    installed_at: InstalledAt
    last_seen_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
