import json
import signal
import time
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.redis_client import redis_client
from app.db.schema import MeasurementEvent
from app.db.session import SessionLocal


class MeasurementWorker:
    """
    Worker that processes measurements from Redis Stream.
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
        print(f"\n  Received signal {signum}, shutting down gracefully...")
        self.running = False

    def ensure_consumer_group(self):
        """Create consumer group if it doesn't exist."""
        try:
            redis_client.client.xgroup_create(
                name=self.stream_name,
                groupname=self.consumer_group,
                id="0",  # Start from beginning
                mkstream=True,  # Create stream if it doesn't exist
            )
            print(f"Created consumer group: {self.consumer_group}")
        except Exception as e:
            # Group already exists
            if "BUSYGROUP" in str(e):
                print(f"Consumer group already exists: {self.consumer_group}")
            else:
                print(f"Error creating consumer group: {e}")

    def process_batch(self, messages: list, db: Session) -> int:
        """
        Process a batch of messages and write to database.

        Returns: Number of successfully processed messages.
        """
        measurements = []

        for message_id, message_data in messages:
            try:
                # Parse message fields
                measurement_json = message_data.get("measurement", "{}")
                denormalized_json = message_data.get("denormalized", "{}")

                measurement_dict = json.loads(measurement_json)
                denormalized_dict = json.loads(denormalized_json)

                # Create MeasurementEvent object
                measurement = MeasurementEvent(
                    machine_id=UUID(measurement_dict["machine_id"]),
                    timestamp=datetime.fromisoformat(
                        measurement_dict["timestamp"].replace("Z", "+00:00")
                    )
                    if measurement_dict.get("timestamp")
                    else datetime.now(timezone.utc),
                    organization_id=UUID(denormalized_dict["organization_id"]),
                    voltage=measurement_dict.get("voltage"),
                    current=measurement_dict.get("current"),
                    rpm=measurement_dict.get("rpm"),
                    torque=measurement_dict.get("torque"),
                    additional_metrics=measurement_dict.get("additional_metrics", {}),
                    machine_name=denormalized_dict["machine_name"],
                    machine_type=denormalized_dict["machine_type"],
                    factory_id=UUID(denormalized_dict["factory_id"]),
                    factory_name=denormalized_dict["factory_name"],
                )

                measurements.append(measurement)

            except Exception as e:
                print(f"Error parsing message {message_id}: {e}")
                self.error_count += 1
                continue

        # Batch insert to database
        if measurements:
            try:
                db.bulk_save_objects(measurements)
                db.commit()
                self.processed_count += len(measurements)
                return len(measurements)
            except Exception as e:
                print(f"Database error: {e}")
                db.rollback()
                self.error_count += len(measurements)
                return 0

        return 0

    def run(self):
        """
        Main worker loop.
        Reads from Redis Stream and processes messages in batches.
        """
        print("   Starting Measurement Worker")
        print(f"   Stream: {self.stream_name}")
        print(f"   Consumer Group: {self.consumer_group}")
        print(f"   Consumer Name: {self.consumer_name}")
        print(f"   Batch Size: {self.batch_size}")
        print(f"   Block Time: {self.block_ms}ms\n")

        # Ensure consumer group exists
        self.ensure_consumer_group()

        db = SessionLocal()

        try:
            while self.running:
                try:
                    # Read messages from stream
                    # XREADGROUP GROUP <group> <consumer> COUNT <count> BLOCK <ms> STREAMS <stream> >
                    messages = redis_client.client.xreadgroup(
                        groupname=self.consumer_group,
                        consumername=self.consumer_name,
                        streams={self.stream_name: ">"},  # ">" = only new messages
                        count=self.batch_size,
                        block=self.block_ms,
                    )

                    if not messages:
                        continue

                    # Process messages
                    for stream_name, stream_messages in messages:
                        if stream_messages:
                            processed = self.process_batch(stream_messages, db)

                            if processed > 0:
                                # Acknowledge processed messages
                                message_ids = [msg_id for msg_id, _ in stream_messages]
                                redis_client.client.xack(
                                    self.stream_name,
                                    self.consumer_group,
                                    *message_ids,
                                )

                                print(
                                    f"Processed batch: {processed} measurements "
                                    f"(Total: {self.processed_count}, Errors: {self.error_count})"
                                )

                except Exception as e:
                    print(f"Worker error: {e}")
                    time.sleep(1)  # Backoff on error

        except KeyboardInterrupt:
            print("\n Interrupted by user")

        finally:
            db.close()
            elapsed = time.time() - self.start_time
            print("\n Worker Statistics:")
            print(f"   Processed: {self.processed_count}")
            print(f"   Errors: {self.error_count}")
            print(f"   Runtime: {elapsed:.1f}s")
            print(f"   Rate: {self.processed_count / elapsed:.2f} msg/sec")


def main():
    """Entry point for the worker."""
    worker = MeasurementWorker()
    worker.run()


if __name__ == "__main__":
    main()
