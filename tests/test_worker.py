"""Worker tests: batch persistence, malformed messages and idempotent redelivery."""

import json

import pytest

from app.db.schema import MeasurementEvent
from app.workers.measurement_worker import MeasurementWorker


@pytest.fixture()
def worker():
    return MeasurementWorker()


def _message(machine, timestamp="2026-01-01T00:00:00Z", **measurement):
    return {
        "machine_id": str(machine.id),
        "measurement": json.dumps(
            {"machine_id": str(machine.id), "timestamp": timestamp, **measurement}
        ),
        "denormalized": json.dumps(
            {
                "organization_id": str(machine.organization_id),
                "machine_name": machine.name,
                "machine_type": "welding",
                "factory_id": str(machine.factory_id),
                "factory_name": "Test Factory",
            }
        ),
    }


def test_process_batch_persists_and_acks_all(worker, db_session, sample_machine):
    messages = [("1-0", _message(sample_machine, voltage=220.0))]

    ack_ids = worker.process_batch(messages, db_session)

    assert ack_ids == ["1-0"]
    assert db_session.query(MeasurementEvent).count() == 1
    assert worker.processed_count == 1


def test_malformed_message_is_acked_and_does_not_block_batch(worker, db_session, sample_machine):
    messages = [
        ("1-0", {"measurement": "not json"}),
        ("2-0", _message(sample_machine, voltage=1.0)),
        ("3-0", None),
    ]

    ack_ids = worker.process_batch(messages, db_session)

    assert ack_ids == ["1-0", "2-0", "3-0"]
    assert db_session.query(MeasurementEvent).count() == 1
    assert worker.error_count == 2


def test_redelivered_message_is_not_duplicated(worker, db_session, sample_machine):
    messages = [("1-0", _message(sample_machine, voltage=220.0))]

    worker.process_batch(messages, db_session)
    ack_ids = worker.process_batch(messages, db_session)

    assert ack_ids == ["1-0"]
    assert db_session.query(MeasurementEvent).count() == 1


def test_database_error_leaves_batch_unacked(worker, db_session, sample_machine):
    # Parses fine, but the non-numeric rpm is rejected by the database.
    bad = _message(sample_machine, rpm="not-a-number")

    with pytest.raises(Exception):
        worker.process_batch([("1-0", bad)], db_session)
