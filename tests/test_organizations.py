from uuid import uuid4

API = "/api/v1/organizations"


def test_create_organization(client):
    response = client.post(API + "/", json={"name": "Acme Corp"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Acme Corp"
    assert "id" in data
    assert "created_at" in data
    assert data["is_active"] is True


def test_get_organization(client, sample_organization):
    response = client.get(f"{API}/{sample_organization.id}")
    assert response.status_code == 200
    assert response.json()["name"] == sample_organization.name


def test_get_organization_not_found(client):
    response = client.get(f"{API}/{uuid4()}")
    assert response.status_code == 404


def test_list_organizations(client, sample_organization):
    response = client.get(API + "/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_update_organization(client, sample_organization):
    response = client.patch(
        f"{API}/{sample_organization.id}",
        json={"name": "Updated Org"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Org"


def test_update_organization_not_found(client):
    response = client.patch(f"{API}/{uuid4()}", json={"name": "Ghost"})
    assert response.status_code == 404


def test_delete_organization(client, sample_organization):
    response = client.delete(f"{API}/{sample_organization.id}")
    assert response.status_code == 204

    # Confirm it's gone
    response = client.get(f"{API}/{sample_organization.id}")
    assert response.status_code == 404
