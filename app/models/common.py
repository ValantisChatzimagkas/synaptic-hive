"""
Reusable Pydantic annotated types shared across all models.
"""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import Field

# ========================= ID TYPES =========================

AnyUUID = Annotated[UUID, Field(description="UUID identifier")]

OrganizationId = Annotated[UUID, Field(description="UUID of the parent organization")]

FactoryId = Annotated[UUID, Field(description="UUID of the parent factory")]

MachineId = Annotated[UUID, Field(description="UUID of the machine")]

# ========================= TIMESTAMP TYPES =========================

CreatedAt = Annotated[datetime, Field(description="Timestamp when the record was created")]

RegisteredAt = Annotated[datetime, Field(description="Timestamp when the entity was registered")]

InstalledAt = Annotated[datetime, Field(description="Timestamp when the machine was installed")]

# ========================= COMMON FIELD TYPES =========================

ActiveFlag = Annotated[bool, Field(description="Whether the entity is currently active")]

ShortName = Annotated[str, Field(min_length=1, max_length=255, description="Name of the entity")]
