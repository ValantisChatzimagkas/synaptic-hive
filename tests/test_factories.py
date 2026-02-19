from uuid import uuid4

API = "/api/v1/factories"

FACTORY_PAYLOAD = {
    "name": "Berlin Plant",
    "industry": "automotive",
    "country_code": "DE",
    "city": "Berlin",
    "postal_code": "10115",
}


def test_create_factory(client, sample_organization):
    payload = {**FACTORY_PAYLOAD, "organization_id": str(sample_organization.id)}
    response = client.post(API + "/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Berlin Plant"
    assert data["organization_id"] == str(sample_organization.id)


def test_create_factory_org_not_found(client):
    payload = {**FACTORY_PAYLOAD, "organization_id": str(uuid4())}
    response = client.post(API + "/", json=payload)
    assert response.status_code == 404


def test_get_factory(client, sample_factory):
    response = client.get(f"{API}/{sample_factory.id}")
    assert response.status_code == 200
    assert response.json()["name"] == sample_factory.name


def test_get_factory_not_found(client):
    response = client.get(f"{API}/{uuid4()}")
    assert response.status_code == 404


def test_list_factories(client, sample_factory):
    response = client.get(API + "/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_list_factories_by_organization(client, sample_factory):
    org_id = str(sample_factory.organization_id)
    response = client.get(API + "/", params={"organization_id": org_id})
    assert response.status_code == 200
    data = response.json()
    assert all(f["organization_id"] == org_id for f in data)


def test_update_factory(client, sample_factory):
    response = client.patch(
        f"{API}/{sample_factory.id}",
        json={"name": "Updated Factory"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Factory"


def test_delete_factory(client, sample_factory):
    response = client.delete(f"{API}/{sample_factory.id}")
    assert response.status_code == 204

    response = client.get(f"{API}/{sample_factory.id}")
    assert response.status_code == 404
