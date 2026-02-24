"""Cross-entity workflow tests: hierarchy creation and cascade deletes."""

from unittest.mock import patch

ORG_API = "/api/v1/organizations"
FACTORY_API = "/api/v1/factories"
MACHINE_API = "/api/v1/machines"
MEASUREMENT_API = "/api/v1/measurements"


def test_full_hierarchy_creation(client):
    """Create org → factory → machine → measurement, verify all linked."""
    # Organization
    org = client.post(ORG_API + "/", json={"name": "Workflow Org"})
    assert org.status_code == 201
    org_id = org.json()["id"]

    # Factory
    factory = client.post(
        f"{ORG_API}/{org_id}/factories",
        json={
            "name": "Workflow Factory",
            "industry": "metalworking",
            "country_code": "DE",
            "city": "Stuttgart",
            "postal_code": "70173",
        },
    )
    assert factory.status_code == 201
    factory_data = factory.json()
    assert factory_data["organization_id"] == org_id
    factory_id = factory_data["id"]

    # Machine
    machine = client.post(
        f"{FACTORY_API}/{factory_id}/machines",
        json={"name": "Workflow Lathe", "machine_type": "lathe"},
    )
    assert machine.status_code == 201
    machine_data = machine.json()
    assert machine_data["factory_id"] == factory_id
    assert machine_data["organization_id"] == org_id
    machine_id = machine_data["id"]

    # Measurement (sync)
    with patch("app.core.config.settings.INGESTION_MODE", "sync"):
        measurement = client.post(
            MEASUREMENT_API + "/",
            json={
                "machine_id": machine_id,
                "voltage": 240.0,
                "current": 18.5,
                "additional_metrics": {},
            },
        )
    assert measurement.status_code == 201
    m_data = measurement.json()
    assert m_data["machine_id"] == machine_id
    assert m_data["factory_name"] == "Workflow Factory"


def test_cascade_delete_organization(client):
    """Deleting an organization cascades to factories and machines."""
    org = client.post(ORG_API + "/", json={"name": "Cascade Org"})
    org_id = org.json()["id"]

    factory = client.post(
        f"{ORG_API}/{org_id}/factories",
        json={
            "name": "Cascade Factory",
            "industry": "electronics",
            "country_code": "JP",
            "city": "Tokyo",
            "postal_code": "100-0001",
        },
    )
    factory_id = factory.json()["id"]

    machine = client.post(
        f"{FACTORY_API}/{factory_id}/machines",
        json={"name": "Cascade Conveyor", "machine_type": "conveyor"},
    )
    machine_id = machine.json()["id"]

    # Delete org
    assert client.delete(f"{ORG_API}/{org_id}").status_code == 204

    # Factory and machine should be gone
    assert client.get(f"{FACTORY_API}/{factory_id}").status_code == 404
    assert client.get(f"{MACHINE_API}/{machine_id}").status_code == 404


def test_cascade_delete_factory(client):
    """Deleting a factory cascades to its machines."""
    org = client.post(ORG_API + "/", json={"name": "Factory Cascade Org"})
    org_id = org.json()["id"]

    factory = client.post(
        f"{ORG_API}/{org_id}/factories",
        json={
            "name": "Delete Me Factory",
            "industry": "textile",
            "country_code": "IT",
            "city": "Milan",
            "postal_code": "20121",
        },
    )
    factory_id = factory.json()["id"]

    machine = client.post(
        f"{FACTORY_API}/{factory_id}/machines",
        json={"name": "Orphan Assembly", "machine_type": "assembly"},
    )
    machine_id = machine.json()["id"]

    # Delete factory
    assert client.delete(f"{FACTORY_API}/{factory_id}").status_code == 204

    # Machine should be gone, org should still exist
    assert client.get(f"{MACHINE_API}/{machine_id}").status_code == 404
    assert client.get(f"{ORG_API}/{org_id}").status_code == 200
