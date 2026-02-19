# app/services/redis_service.py
"""
Redis streaming service for async measurement ingestion.
"""

import json
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


def get_stream_length() -> int:
    """Get the current length of the measurements stream."""
    length = redis_client.client.xlen(settings.REDIS_STREAM_NAME)
    return cast(int, length)
