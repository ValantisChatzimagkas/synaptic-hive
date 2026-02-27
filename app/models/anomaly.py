from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.models.common import MachineId


class AnomalyEventResponse(BaseModel):
    machine_id: MachineId
    timestamp: Annotated[
        datetime, Field(description="Measurement timestamp at which the anomaly was detected")
    ]
    metric: Annotated[str, Field(description="Available metric names: e.g. current, voltage etc.")]
    value: Annotated[float, Field(description="Value of observed metric")]
    score: Annotated[
        float, Field(description="Anomaly score assigned by the detector (higher = more anomalous)")
    ]
    detector: Annotated[str, Field(description="Method used to detect anomaly")]

    model_config = ConfigDict(from_attributes=True)
