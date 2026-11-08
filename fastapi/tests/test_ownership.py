"""Testes do controle de acesso por ownership (BOLA) em /predictions.

O banco de teste e o fixture `client` vem de conftest.py.
Pressupoe o seed de sqlite_database.py: admin e dono das predictions 1-2; analista, das 3-5.
"""

import pytest
from fastapi.testclient import TestClient

ADMIN = ("admin", "Infnet@2025")
ANALISTA = ("analista", "Analista@2025")
ADMIN_IDS = {1, 2}
ANALISTA_IDS = {3, 4, 5}


def auth_header(client: TestClient, credentials: tuple[str, str]) -> dict[str, str]:
    username, password = credentials
    response = client.post("/auth/token", data={"username": username, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.mark.parametrize("credentials, own_ids", [(ADMIN, ADMIN_IDS), (ANALISTA, ANALISTA_IDS)])
def test_owner_can_read_own_predictions(client, credentials, own_ids):
    headers = auth_header(client, credentials)
    for prediction_id in own_ids:
        response = client.get(f"/predictions/{prediction_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == prediction_id


@pytest.mark.parametrize(
    "credentials, foreign_ids",
    [(ADMIN, ANALISTA_IDS), (ANALISTA, ADMIN_IDS)],
)
def test_user_cannot_read_predictions_of_others(client, credentials, foreign_ids):
    headers = auth_header(client, credentials)
    for prediction_id in foreign_ids:
        response = client.get(f"/predictions/{prediction_id}", headers=headers)
        assert response.status_code == 404
        assert "text" not in response.json()  # nenhum dado do recurso vaza


def test_foreign_and_nonexistent_ids_are_indistinguishable(client):
    headers = auth_header(client, ADMIN)
    foreign = client.get(f"/predictions/{min(ANALISTA_IDS)}", headers=headers)
    missing = client.get("/predictions/999999", headers=headers)
    assert foreign.status_code == missing.status_code == 404
    assert foreign.json() == missing.json()


def test_list_returns_only_own_predictions(client):
    for credentials, own_ids, foreign_ids in (
        (ADMIN, ADMIN_IDS, ANALISTA_IDS),
        (ANALISTA, ANALISTA_IDS, ADMIN_IDS),
    ):
        response = client.get("/predictions", headers=auth_header(client, credentials))
        assert response.status_code == 200
        returned_ids = {item["id"] for item in response.json()}
        assert own_ids <= returned_ids
        assert returned_ids.isdisjoint(foreign_ids)


def test_new_prediction_belongs_to_caller_only(client):
    headers = auth_header(client, ADMIN)
    assert client.post("/predict", json={"text": "Where is my invoice?"}, headers=headers).status_code == 200

    admin_ids = {item["id"] for item in client.get("/predictions", headers=headers).json()}
    analista_ids = {
        item["id"] for item in client.get("/predictions", headers=auth_header(client, ANALISTA)).json()
    }
    assert len(admin_ids) == len(ADMIN_IDS) + 1
    assert analista_ids == ANALISTA_IDS
    assert admin_ids.isdisjoint(analista_ids)


def test_owner_id_in_body_is_rejected(client):
    headers = auth_header(client, ADMIN)
    response = client.post("/predict", json={"text": "Where is my invoice?", "owner_id": 2}, headers=headers)
    assert response.status_code == 422


def test_requires_authentication(client):
    assert client.get("/predictions/1").status_code == 401
    assert client.get("/predictions").status_code == 401
