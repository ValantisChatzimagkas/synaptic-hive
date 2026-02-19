from uuid import uuid4

API = "/api/v1/machines"

MACHINE_PAYLOAD = {
    "name": "Press Unit A",
    "machine_type": "press",
    "manufacturer": "Schuler",
    "model": "MSD 200",
}


def test_create_machine(client, sample_factory):
    payload = {**MACHINE_PAYLOAD, "factory_id": str(sample_factory.id)}
    response = client.post(API + "/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Press Unit A"
    assert data["factory_id"] == str(sample_factory.id)
    # organization_id should be denormalized from factory
    assert data["organization_id"] == str(sample_factory.organization_id)


def test_create_machine_factory_not_found(client):
    payload = {**MACHINE_PAYLOAD, "factory_id": str(uuid4())}
    response = client.post(API + "/", json=payload)
    assert response.status_code == 404


def test_get_machine(client, sample_machine):
    response = client.get(f"{API}/{sample_machine.id}")
    assert response.status_code == 200
    assert response.json()["name"] == sample_machine.name


def test_get_machine_not_found(client):
    response = client.get(f"{API}/{uuid4()}")
    assert response.status_code == 404


def test_list_machines(client, sample_machine):
    response = client.get(API + "/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_list_machines_by_factory(client, sample_machine):
    factory_id = str(sample_machine.factory_id)
    response = client.get(API + "/", params={"factory_id": factory_id})
    assert response.status_code == 200
    data = response.json()
    assert all(m["factory_id"] == factory_id for m in data)


def test_update_machine(client, sample_machine):
    response = client.patch(
        f"{API}/{sample_machine.id}",
        json={"name": "Updated Machine"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Machine"


def test_delete_machine(client, sample_machine):
    response = client.delete(f"{API}/{sample_machine.id}")
    assert response.status_code == 204

    response = client.get(f"{API}/{sample_machine.id}")
    assert response.status_code == 404
