"""Tests for /api/v1/audit endpoints."""


def test_audit_log_empty_initially(client):
    resp = client.get("/api/v1/audit")
    assert resp.status_code == 200
    data = resp.json()
    assert "entries" in data
    assert isinstance(data["entries"], list)


def test_audit_log_after_chat(client):
    client.post("/api/v1/chat", json={"prompt": "Email hans@example.com"})
    resp = client.get("/api/v1/audit")
    entries = resp.json()["entries"]
    assert len(entries) >= 1
    entry = entries[0]
    assert "session_id" in entry
    assert "role" in entry
    assert "masked_prompt" in entry
    assert "llm_response" in entry


def test_audit_session_history(client):
    resp = client.post("/api/v1/chat", json={"prompt": "Hans Peter"})
    sid = resp.json()["session_id"]

    resp2 = client.get(f"/api/v1/audit/{sid}")
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["session_id"] == sid
    assert len(data["entries"]) >= 1


def test_audit_log_limit(client):
    for _ in range(3):
        client.post("/api/v1/chat", json={"prompt": "test"})
    resp = client.get("/api/v1/audit?limit=2")
    entries = resp.json()["entries"]
    assert len(entries) <= 2
