"""Tests for /api/v1/vault endpoints."""


def _create_session(client, prompt="Hans Peter"):
    resp = client.post("/api/v1/chat", json={"prompt": prompt})
    return resp.json()["session_id"]


def test_get_vault(client):
    sid = _create_session(client)
    resp = client.get(f"/api/v1/vault/{sid}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["session_id"] == sid
    assert "mappings" in data
    assert "session_info" in data


def test_get_vault_not_found(client):
    resp = client.get("/api/v1/vault/nonexistent-id")
    assert resp.status_code == 404


def test_delete_vault(client):
    sid = _create_session(client)
    resp = client.delete(f"/api/v1/vault/{sid}")
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True

    # Gone now
    resp2 = client.get(f"/api/v1/vault/{sid}")
    assert resp2.status_code == 404


def test_delete_vault_not_found(client):
    resp = client.delete("/api/v1/vault/nonexistent-id")
    assert resp.status_code == 404


def test_vault_session_info(client):
    sid = _create_session(client, prompt="Email test@example.com")
    resp = client.get(f"/api/v1/vault/{sid}")
    info = resp.json()["session_info"]
    assert info["session_id"] == sid
    assert info["request_count"] >= 1
    assert info["token_count"] >= 1
