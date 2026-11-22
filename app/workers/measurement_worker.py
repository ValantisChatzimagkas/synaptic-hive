import json
import logging
import signal
import time
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from redis.exceptions import ResponseError
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.redis_client import redis_client
from app.db.schema import MeasurementEvent
from app.db.session import SessionLocal

logger = logging.getLogger("measurement_worker")


class MeasurementWorker:
    """
    Consumes measurements from a Redis Stream and writes them to the database.

    Delivery is at-least-once: a message is acknowledged only after its batch is
    committed, and unacknowledged messages are re-read on the next iteration.
    Inserts ignore (machine_id, timestamp) conflicts, so redelivery never
    produces duplicates or failed batches. Messages that cannot be parsed are
    logged and acknowledged, since retrying cannot fix them.
    """

    def __init__(
        self,
        stream_name: str = settings.REDIS_STREAM_NAME,
        consumer_group: str = "measurement_workers",
        consumer_name: str = "worker_1",
        batch_size: int = 100,
        block_ms: int = 5000,
    ):
        self.stream_name = stream_name
        self.consumer_group = consumer_group
        self.consumer_name = consumer_name
        self.batch_size = batch_size
        self.block_ms = block_ms
        self.running = True

        # stats
        self.processed_count = 0
        self.error_count = 0
        self.start_time = time.time()

        # setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info("Received signal %s, shutting down", signum)
        self.running = False

    def ensure_consumer_group(self):
        """Create consumer group (and stream) if they don't exist."""
        try:
            redis_client.client.xgroup_create(
                name=self.stream_name,
                groupname=self.consumer_group,
                id="0",  # Start from beginning
                mkstream=True,
            )
            logger.info("Created consumer group: %s", self.consumer_group)
        except ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise
            logger.info("Consumer group already exists: %s", self.consumer_group)

    @staticmethod
    def _parse_message(message_data: dict[str, str]) -> dict[str, Any]:
        """Convert a stream message into a measurement_events row."""
        measurement = json.loads(message_data["measurement"])
        denormalized = json.loads(message_data["denormalized"])
        timestamp = measurement.get("timestamp")

        return {
            "machine_id": UUID(measurement["machine_id"]),
            "timestamp": datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            if timestamp
            else datetime.now(timezone.utc),
            "organization_id": UUID(denormalized["organization_id"]),
            "voltage": measurement.get("voltage"),
            "current": measurement.get("current"),
            "rpm": measurement.get("rpm"),
            "torque": measurement.get("torque"),
            "additional_metrics": measurement.get("additional_metrics", {}),
            "machine_name": denormalized["machine_name"],
            "machine_type": denormalized["machine_type"],
            "factory_id": UUID(denormalized["factory_id"]),
            "factory_name": denormalized["factory_name"],
        }

    def process_batch(self, messages: list, db: Session) -> list[str]:
        """
        Persist a batch of messages.

        Returns the IDs that are safe to acknowledge (stored or unparseable).
        Raises on database errors, leaving the whole batch unacknowledged.
        """
        rows = []
        ack_ids = []

        for message_id, message_data in messages:
            ack_ids.append(message_id)
            try:
                rows.append(self._parse_message(message_data))
            except (KeyError, ValueError, TypeError, AttributeError) as e:
                logger.error("Dropping malformed message %s: %s", message_id, e)
                self.error_count += 1

        if rows:
            try:
                db.execute(insert(MeasurementEvent).values(rows).on_conflict_do_nothing())
                db.commit()
            except Exception:
                db.rollback()
                raise
            self.processed_count += len(rows)

        return ack_ids

    def run(self):
        """Main worker loop: read from the stream, persist, acknowledge."""
        logger.info(
            "Starting worker: stream=%s group=%s consumer=%s batch_size=%d",
            self.stream_name,
            self.consumer_group,
            self.consumer_name,
            self.batch_size,
        )

        self.ensure_consumer_group()
        db = SessionLocal()

        # "0" re-reads this consumer's unacknowledged messages (left over from a
        # crash or a failed batch); ">" reads only new messages.
        read_id = "0"

        try:
            while self.running:
                try:
                    response = redis_client.client.xreadgroup(
                        groupname=self.consumer_group,
                        consumername=self.consumer_name,
                        streams={self.stream_name: read_id},
                        count=self.batch_size,
                        block=self.block_ms,
                    )
                    messages = response[0][1] if response else []

                    if not messages:
                        read_id = ">"
                        continue

                    ack_ids = self.process_batch(messages, db)
                    redis_client.client.xack(self.stream_name, self.consumer_group, *ack_ids)
                    logger.info(
                        "Processed batch of %d (total: %d, errors: %d)",
                        len(ack_ids),
                        self.processed_count,
                        self.error_count,
                    )

                except Exception:
                    logger.exception("Worker error, retrying unacknowledged messages")
                    read_id = "0"
                    time.sleep(1)  # Backoff on error

        finally:
            db.close()
            elapsed = time.time() - self.start_time
            logger.info(
                "Worker stopped: processed=%d errors=%d runtime=%.1fs rate=%.2f msg/s",
                self.processed_count,
                self.error_count,
                elapsed,
                self.processed_count / elapsed,
            )


def main():
    """Entry point for the worker."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    MeasurementWorker().run()


if __name__ == "__main__":
    main()
