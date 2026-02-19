from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.common import FactoryId, MachineId, OrganizationId


class MeasurementEventCreate(BaseModel):
    """
    Schema for creating a measurement event.
    This is what the data generator or IoT devices send.
    """

    machine_id: MachineId
    timestamp: Annotated[
        Optional[datetime], Field(description="Measurement timestamp (server sets if not provided)")
    ] = None

    # Electrical measurements (welding machines)
    voltage: Annotated[Optional[float], Field(description="Voltage in V")] = None
    current: Annotated[Optional[float], Field(description="Current in A")] = None

    # Mechanical measurements (lathe, conveyor)
    rpm: Annotated[Optional[int], Field(description="Revolutions per minute")] = None
    torque: Annotated[Optional[float], Field(description="Torque in Nm")] = None

    # Flexible catch-all for other metrics
    additional_metrics: Annotated[
        dict, Field(default_factory=dict, description="Additional machine-specific metrics")
    ]


class MeasurementEventResponse(BaseModel):
    """
    Schema for MeasurementEvent API response.
    Includes all fields including denormalized data.
    """

    machine_id: MachineId
    organization_id: OrganizationId
    timestamp: datetime

    # Measurement Values
    voltage: Optional[float] = None
    current: Optional[float] = None
    rpm: Optional[int] = None
    torque: Optional[float] = None
    additional_metrics: dict | None = None

    # Denormalized fields (for queries without JOINs)
    machine_name: str
    machine_type: str
    factory_id: FactoryId
    factory_name: str

    model_config = ConfigDict(from_attributes=True)


class MeasurementStatistics(BaseModel):
    """
    Statistical Summary of measurements for a time range.
    """

    machine_id: MachineId
    machine_name: str
    time_range_start: datetime
    time_range_end: datetime
    total_measurements: int

    # Stats for each measurement that is present.
    voltage_avg: Optional[float] = None
    voltage_min: Optional[float] = None
    voltage_max: Optional[float] = None

    current_avg: Optional[float] = None
    current_min: Optional[float] = None
    current_max: Optional[float] = None

    rpm_avg: Optional[float] = None
    rpm_min: Optional[int] = None
    rpm_max: Optional[int] = None

    torque_avg: Optional[float] = None
    torque_min: Optional[float] = None
    torque_max: Optional[float] = None
