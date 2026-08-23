"""Tests for GET /api/v1/stats endpoint."""


def test_stats_returns_ok(client):
    resp = client.get("/api/v1/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "vault" in data
    assert "llm" in data
    assert "audit" in data


def test_stats_vault_has_backend(client):
    resp = client.get("/api/v1/stats")
    vault_stats = resp.json()["vault"]
    assert "backend" in vault_stats
    assert vault_stats["backend"] == "memory"


def test_stats_llm_is_mock(client):
    resp = client.get("/api/v1/stats")
    llm_stats = resp.json()["llm"]
    assert llm_stats["mode"] == "mock"


def test_stats_increments_after_chat(client):
    client.post("/api/v1/chat", json={"prompt": "test"})
    resp = client.get("/api/v1/stats")
    vault_stats = resp.json()["vault"]
    assert vault_stats["total_stores"] >= 1
