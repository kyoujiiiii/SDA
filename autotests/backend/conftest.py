"""Backend test fixtures — FastAPI TestClient with in-memory SQLite."""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure back/ and project root are importable
BACK_DIR = str(Path(__file__).resolve().parent.parent.parent / "back")
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
for p in (BACK_DIR, PROJECT_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)


@pytest.fixture(autouse=True)
def _override_db(monkeypatch):
    """Point SQLAlchemy at an in-memory SQLite DB for every test."""
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    # Force config reload
    import config
    config.DATABASE_URL = "sqlite:///:memory:"
    # Re-init DB tables
    import database
    database.engine = database.create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False,
    )
    database.SessionLocal = database.sessionmaker(bind=database.engine)
    database.Base.metadata.create_all(bind=database.engine)
    yield


@pytest.fixture(autouse=True)
def _mock_vault():
    """Use in-memory vault (no Redis needed)."""
    import airlock.vault as vault_mod
    vault_mod.vault._redis = None
    vault_mod.vault._mem.clear()
    yield


@pytest.fixture(autouse=True)
def _mock_llm():
    """Force mock LLM mode (no API key needed)."""
    import airlock.llm as llm_mod
    llm_mod.llm_service.use_mock = True
    llm_mod.llm_service._client = None
    yield


@pytest.fixture
def client():
    """FastAPI TestClient ready to use."""
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)
