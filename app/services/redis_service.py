# app/services/redis_service.py
"""
Redis streaming service for async measurement ingestion.
"""

import json
from datetime import datetime, timezone
from typing import Any, cast
from uuid import UUID

from app.core.config import settings
from app.core.redis_client import redis_client
from app.models.measurement import MeasurementEventCreate


def publish_measurement(
    machine_id: UUID,
    measurement_payload: MeasurementEventCreate,
    denormalized_data: dict[str, Any],
) -> str:
    """
    Publish a measurement to Redis Stream.
    """
    # Stamp at ingestion time so a queued measurement keeps its arrival time
    # instead of getting the worker's processing time.
    if measurement_payload.timestamp is None:
        measurement_payload = measurement_payload.model_copy(
            update={"timestamp": datetime.now(timezone.utc)}
        )

    # Use Pydantic's JSON serializer for the measurement (handles datetime, etc.)
    message: dict[str, str] = {
        "machine_id": str(machine_id),
        "measurement": measurement_payload.model_dump_json(exclude_unset=True),
        "denormalized": json.dumps(denormalized_data),
    }

    message_id = redis_client.client.xadd(
        name=settings.REDIS_STREAM_NAME,
        fields=cast(dict[str, str], message),
    )

    return message_id.decode() if isinstance(message_id, bytes) else str(message_id)
