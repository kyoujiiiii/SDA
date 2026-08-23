"""Tests for GET /health endpoint."""


def test_health_returns_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


def test_health_includes_vault_and_llm(client):
    resp = client.get("/health")
    data = resp.json()
    assert "vault" in data
    assert "llm" in data
    assert data["llm"] == "mock"
