# Swiss Data Airlock — Autotests

Automated test suite for the SDA project covering core, backend, and frontend.

## Structure

```
autotests/
├── core/           # Python unit tests for the core PII detection/tokenization module
├── backend/        # API integration tests (FastAPI endpoints)
├── frontend/       # Frontend testing guidelines and E2E scenarios
├── conftest.py     # Shared pytest fixtures
└── requirements.txt
```

## Quick Start

```bash
# Install test dependencies
pip install -r autotests/requirements.txt

# Run all tests
pytest autotests/ -v

# Run only core tests
pytest autotests/core/ -v

# Run only backend tests (requires running backend or mock)
pytest autotests/backend/ -v

# Run with coverage
pytest autotests/ --cov=core --cov=back -v
```

## Test Categories

### Core Tests (`core/`)
Pure Python unit tests — no external services needed.
- Pattern matching (Swiss IBAN, AHV, emails, phones)
- PII detection via Presidio
- Tokenization / detokenization round-trip
- AirlockEngine facade

### Backend Tests (`backend/`)
FastAPI integration tests using `TestClient` with SQLite in-memory DB.
- Health check
- Chat endpoint (masking + LLM mock + role-based unmasking)
- Vault CRUD
- Stats and audit endpoints

### Frontend (`frontend/`)
Manual testing guidelines + E2E scenario descriptions.
See `frontend/README.md` for details.
