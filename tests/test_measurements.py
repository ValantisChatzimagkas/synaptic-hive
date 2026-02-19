from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import uuid4

API = "/api/v1/measurements"


def _make_measurement_payload(machine_id, **overrides):
    base = {
        "machine_id": str(machine_id),
        "voltage": 220.5,
        "current": 15.3,
        "rpm": 1500,
        "torque": 45.2,
        "additional_metrics": {},
    }
    base.update(overrides)
    return base


def test_ingest_measurement_sync(client, sample_machine):
    with patch("app.core.config.settings.INGESTION_MODE", "sync"):
        payload = _make_measurement_payload(sample_machine.id)
        response = client.post(API + "/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["machine_id"] == str(sample_machine.id)
    assert data["voltage"] == 220.5


def test_ingest_measurement_async(client, sample_machine, fake_redis):
    with patch("app.core.config.settings.INGESTION_MODE", "async"):
        payload = _make_measurement_payload(sample_machine.id)
        response = client.post(API + "/", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "accepted"
    assert "redis_message_id" in data

    # Verify the message was added to the Redis stream
    stream_len = fake_redis.xlen("measurements")
    assert stream_len >= 1


def test_ingest_measurement_machine_not_found(client):
    with patch("app.core.config.settings.INGESTION_MODE", "sync"):
        payload = _make_measurement_payload(uuid4())
        response = client.post(API + "/", json=payload)
    assert response.status_code == 404


def test_get_measurements(client, sample_machine):
    # Create a measurement first
    with patch("app.core.config.settings.INGESTION_MODE", "sync"):
        payload = _make_measurement_payload(sample_machine.id)
        client.post(API + "/", json=payload)

    response = client.get(API + "/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_measurements_by_machine(client, sample_machine):
    with patch("app.core.config.settings.INGESTION_MODE", "sync"):
        payload = _make_measurement_payload(sample_machine.id)
        client.post(API + "/", json=payload)

    response = client.get(API + "/", params={"machine_id": str(sample_machine.id)})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(m["machine_id"] == str(sample_machine.id) for m in data)


def test_get_measurements_time_range(client, sample_machine):
    now = datetime.now(timezone.utc)
    ts = (now - timedelta(minutes=5)).isoformat()

    with patch("app.core.config.settings.INGESTION_MODE", "sync"):
        payload = _make_measurement_payload(sample_machine.id, timestamp=ts)
        client.post(API + "/", json=payload)

    start = (now - timedelta(hours=1)).isoformat()
    end = now.isoformat()
    response = client.get(API + "/", params={"start_time": start, "end_time": end})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_get_statistics(client, sample_machine):
    with patch("app.core.config.settings.INGESTION_MODE", "sync"):
        for v in [220.0, 230.0, 225.0]:
            payload = _make_measurement_payload(sample_machine.id, voltage=v)
            client.post(API + "/", json=payload)

    response = client.get(f"{API}/statistics/{sample_machine.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total_measurements"] == 3
    assert data["voltage_min"] == 220.0
    assert data["voltage_max"] == 230.0


def test_get_statistics_no_data(client):
    response = client.get(f"{API}/statistics/{uuid4()}")
    assert response.status_code == 404
