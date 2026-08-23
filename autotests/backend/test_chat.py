"""Tests for POST /api/v1/chat endpoint."""


def test_chat_basic(client):
    resp = client.post("/api/v1/chat", json={"prompt": "Hello world"})
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert "masked_payload" in data
    assert "final_response" in data
    assert "latency_ms" in data
    assert data["role"] == "admin"


def test_chat_masks_pii(client):
    resp = client.post("/api/v1/chat", json={
        "prompt": "Contact Hans Peter at hans@example.com"
    })
    data = resp.json()
    assert "hans@example.com" not in data["masked_payload"]
    assert len(data["detected_entities"]) > 0


def test_chat_admin_role_unmasks(client):
    resp = client.post("/api/v1/chat", json={
        "prompt": "Email hans@example.com",
        "role": "admin",
    })
    data = resp.json()
    # Admin sees original values restored in final_response
    assert "hans@example.com" in data["final_response"]


def test_chat_auditor_role_keeps_masked(client):
    resp = client.post("/api/v1/chat", json={
        "prompt": "Email hans@example.com",
        "role": "auditor",
    })
    data = resp.json()
    # Auditor sees tokens, not original
    assert "hans@example.com" not in data["final_response"]


def test_chat_invalid_role(client):
    resp = client.post("/api/v1/chat", json={
        "prompt": "test",
        "role": "hacker",
    })
    assert resp.status_code == 400


def test_chat_empty_prompt_rejected(client):
    resp = client.post("/api/v1/chat", json={"prompt": ""})
    assert resp.status_code == 422


def test_chat_returns_session_id(client):
    resp = client.post("/api/v1/chat", json={"prompt": "test"})
    data = resp.json()
    assert isinstance(data["session_id"], str)
    assert len(data["session_id"]) > 0


def test_chat_session_persists_mapping(client):
    resp1 = client.post("/api/v1/chat", json={
        "prompt": "Hans Peter IBAN CH9300762011623852957"
    })
    session_id = resp1.json()["session_id"]

    # Vault should have stored the mappings
    resp2 = client.get(f"/api/v1/vault/{session_id}")
    assert resp2.status_code == 200
    vault_data = resp2.json()
    assert len(vault_data["mappings"]) > 0
