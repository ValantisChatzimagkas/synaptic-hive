from uuid import uuid4

FACTORY_API = "/api/v1/factories"
MACHINE_API = "/api/v1/machines"

MACHINE_PAYLOAD = {
    "name": "Press Unit A",
    "machine_type": "press",
    "manufacturer": "Schuler",
    "model": "MSD 200",
}


def test_create_machine(client, sample_factory):
    response = client.post(f"{FACTORY_API}/{sample_factory.id}/machines", json=MACHINE_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Press Unit A"
    assert data["factory_id"] == str(sample_factory.id)
    assert data["organization_id"] == str(sample_factory.organization_id)


def test_create_machine_factory_not_found(client):
    response = client.post(f"{FACTORY_API}/{uuid4()}/machines", json=MACHINE_PAYLOAD)
    assert response.status_code == 404


def test_get_machine(client, sample_machine):
    response = client.get(f"{MACHINE_API}/{sample_machine.id}")
    assert response.status_code == 200
    assert response.json()["name"] == sample_machine.name


def test_get_machine_not_found(client):
    response = client.get(f"{MACHINE_API}/{uuid4()}")
    assert response.status_code == 404


def test_list_machines(client, sample_machine):
    response = client.get(f"{FACTORY_API}/{sample_machine.factory_id}/machines")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert all(m["factory_id"] == str(sample_machine.factory_id) for m in data)


def test_update_machine(client, sample_machine):
    response = client.patch(f"{MACHINE_API}/{sample_machine.id}", json={"name": "Updated Machine"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Machine"


def test_delete_machine(client, sample_machine):
    response = client.delete(f"{MACHINE_API}/{sample_machine.id}")
    assert response.status_code == 204

    response = client.get(f"{MACHINE_API}/{sample_machine.id}")
    assert response.status_code == 404
