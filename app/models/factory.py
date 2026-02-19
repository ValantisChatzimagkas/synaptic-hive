from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic_extra_types.coordinate import Latitude, Longitude
from pydantic_extra_types.country import CountryAlpha2

from app.enums import IndustryType
from app.models.common import ActiveFlag, AnyUUID, OrganizationId, RegisteredAt, ShortName


class FactoryBase(BaseModel):
    """Shared fields for Factory schemas"""

    name: ShortName
    industry: Annotated[IndustryType, Field(description="Available industries supported")]
    country_code: Annotated[
        CountryAlpha2, Field(description="Country code in ISO 3166-1 alpha-2 country code")
    ]
    city: Annotated[str, Field(min_length=1, max_length=100, description="City name")]
    postal_code: Annotated[str, Field(min_length=1, max_length=20, description="Postal/ZIP code")]
    latitude: Annotated[
        Optional[Latitude], Field(description="Latitude of location where factory is located")
    ] = None
    longitude: Annotated[
        Optional[Longitude], Field(description="Longitude of location where factory is located")
    ] = None
    is_active: ActiveFlag = True


class FactoryCreate(FactoryBase):
    """Schema for creating a factory."""

    organization_id: OrganizationId


class FactoryUpdate(FactoryBase):
    """Schema for updating a factory."""

    name: Annotated[Optional[ShortName], Field(min_length=1, max_length=255)] = None
    industry: Annotated[
        Optional[IndustryType], Field(description="Available industries supported")
    ] = None
    country_code: Annotated[
        Optional[CountryAlpha2],
        Field(description="Country code in ISO 3166-1 alpha-2 country code"),
    ] = None
    city: Annotated[Optional[str], Field(min_length=1, max_length=100, description="City name")] = (
        None
    )
    postal_code: Annotated[
        Optional[str], Field(min_length=1, max_length=20, description="Postal/ZIP code")
    ] = None
    latitude: Annotated[
        Optional[Latitude], Field(description="Latitude of location where factory is located")
    ] = None
    longitude: Annotated[
        Optional[Longitude], Field(description="Longitude of location where factory is located")
    ] = None
    is_active: Optional[ActiveFlag] = None


class FactoryResponse(FactoryBase):
    id: AnyUUID
    organization_id: OrganizationId
    registered_at: RegisteredAt

    model_config = ConfigDict(from_attributes=True)
