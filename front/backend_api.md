# Swiss Data Airlock — Backend API Reference

Guide for connecting the frontend to the backend and PII-masking engine.

---

## Architecture

```
┌────────────┐      HTTP       ┌────────────┐     internal     ┌────────────┐
│            │  ─────────────►  │            │  ──────────────►  │            │
│  Frontend  │                  │  Backend   │                   │   Core     │
│  (SPA)     │  ◄─────────────  │  (FastAPI) │  ◄──────────────  │  Engine   │
│            │      JSON        │            │                   │ (Presidio) │
└────────────┘                  └─────┬──┬───┘                   └────────────┘
                                      │  │
                              ┌───────┘  └────────┐
                              ▼                    ▼
                        ┌──────────┐        ┌──────────┐
                        │  Redis   │        │ PostgreSQL│
                        │ (Vault)  │        │  / SQLite │
                        └──────────┘        └──────────┘
```

**Components:**
- **Frontend** — SPA (HTML/JS/CSS), served by the backend as static files
- **Backend** — FastAPI server, port `8000`
- **Core Engine** — `../core/` — Presidio + Swiss regex patterns for PII masking/unmasking
- **Redis** — token-to-value mapping storage (session vault), port `6379`
- **SQL Database** — audit log (masked payloads only), SQLite locally / PostgreSQL in Docker

---

## Ports and Connection

| Service | Port | URL |
|---------|------|-----|
| Backend API | `8000` | `http://localhost:8000` |
| Redis | `6379` | `redis://localhost:6379/0` |
| Frontend | — | served at `http://localhost:8000` |

**Startup:**
```bash
cd back/
cp .env.example .env      # configure API keys
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**CORS:** all origins are allowed (`*`). The frontend can call the API from any domain or port.

---

## Rules

1. **All requests** must use JSON (`Content-Type: application/json`).
2. **Sessions** — each conversation is tied to a `session_id` (UUID). If omitted, one is generated automatically.
3. **Roles** — two access levels:
   - `admin` (Data Owner) — receives the response with original values restored
   - `auditor` (Cloud View) — sees only tokens (`[PERSON_1]`, `[IBAN_1]`), originals are hidden
4. **Timeout** — LLM requests may take up to ~10 seconds. The frontend must display a loading indicator.
5. **Errors** — returned as HTTP `4xx/5xx` status with body `{"detail": "error description"}`.
6. **PII never leaves the backend** — only masked data is stored in the audit log and vault.

---

## Endpoints

### `GET /`

Serves the main page (`static/index.html`).

---

### `GET /health`

Health check.

**Response:**
```json
{
  "status": "ok",
  "vault": "redis",
  "llm": "live"
}
```

**Values:**
- `vault` — `"redis"` or `"memory"` (fallback when Redis is unavailable)
- `llm` — `"live"` (real LLM connected) or `"mock"` (no API key)

---

### `POST /api/v1/chat`

Main endpoint. Full cycle: mask → LLM → unmask.

**Request:**
```json
{
  "prompt": "Send CHF 50,000 to Hans Peter, IBAN CH9300000000000000000",
  "role": "admin",
  "session_id": "optional-uuid",
  "model": "optional-model-override"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | string | yes | Text containing potential sensitive data (1–10,000 chars) |
| `role` | string | no | `"admin"` (default) or `"auditor"` |
| `session_id` | string | no | Session UUID. If omitted, a new one is generated |
| `model` | string | no | Override the default LLM model |

**Response (200):**
```json
{
  "session_id": "a1b2c3d4-...",
  "original_prompt": "Send CHF 50,000 to Hans Peter, IBAN CH9300000000000000000",
  "masked_payload": "Send CHF 50,000 to [PERSON_1], IBAN [IBAN_1]",
  "llm_raw_response": "Based on [PERSON_1] and [IBAN_1], ...",
  "final_response": "Based on Hans Peter and CH9300000000000000000, ...",
  "latency_ms": 4257,
  "detected_entities": [
    {
      "entity_type": "PERSON",
      "start": 19,
      "end": 29,
      "original_value": "Hans Peter",
      "token": "[PERSON_1]",
      "score": 0.85
    },
    {
      "entity_type": "IBAN",
      "start": 36,
      "end": 57,
      "original_value": "CH9300000000000000000",
      "token": "[IBAN_1]",
      "score": 0.9
    }
  ],
  "role": "admin",
  "llm_model": "meta/llama-3.1-8b-instruct",
  "token_usage": {
    "prompt_tokens": 185,
    "completion_tokens": 270,
    "total_tokens": 455
  }
}
```

**Response fields:**

| Field | Description |
|-------|-------------|
| `session_id` | Session ID (pass in subsequent requests) |
| `original_prompt` | Original user input |
| `masked_payload` | Text with tokens (what the LLM sees) |
| `llm_raw_response` | Raw LLM output with tokens (no unmasking) |
| `final_response` | Final answer (unmasked for `admin`, still masked for `auditor`) |
| `latency_ms` | Total round-trip latency in milliseconds |
| `detected_entities` | List of detected PII entities |
| `role` | Role used for this request |
| `llm_model` | Model that generated the response |
| `token_usage` | Token counts: prompt / completion / total |

**Errors:**
- `400` — invalid role (not `admin`/`auditor`)
- `5xx` — LLM or internal error

---

### `GET /api/v1/vault/{session_id}`

View token mappings for a session (for debugging / demo).

**Response:**
```json
{
  "session_id": "a1b2c3d4-...",
  "mappings": {
    "[PERSON_1]": "Hans Peter",
    "[IBAN_1]": "CH9300000000000000000"
  },
  "session_info": {
    "session_id": "a1b2c3d4-...",
    "created_at": 1787363115.487,
    "last_accessed": 1787363150.292,
    "token_count": 2,
    "request_count": 1,
    "age_seconds": 34.8
  }
}
```

**Errors:** `404` if the session is not found or has expired (TTL = 1 hour).

---

### `DELETE /api/v1/vault/{session_id}`

Delete a session and all its token mappings.

**Response:**
```json
{
  "deleted": true,
  "session_id": "a1b2c3d4-..."
}
```

---

### `GET /api/v1/stats`

Statistics for all components.

**Response:**
```json
{
  "vault": {
    "backend": "redis",
    "active_sessions": 3,
    "total_mappings": 12,
    "total_stores": 15,
    "total_sessions": 5
  },
  "llm": {
    "mode": "live",
    "total_requests": 42,
    "total_errors": 1,
    "avg_latency_ms": 3200
  },
  "audit": {
    "total_requests": 42,
    "distinct_sessions": 8
  }
}
```

---

### `GET /api/v1/audit?limit=20`

Recent audit log entries (masked data only, no PII).

**Query params:**
- `limit` — number of entries (default: 20)

**Response:**
```json
{
  "entries": [
    {
      "id": 1,
      "session_id": "a1b2c3d4-...",
      "role": "admin",
      "created_at": 1787363115.487,
      "masked_prompt": "Send CHF 50,000 to [PERSON_1], IBAN [IBAN_1]",
      "llm_response": "Based on [PERSON_1] and [IBAN_1], ...",
      "entity_types": ["PERSON", "IBAN"],
      "entity_count": 2,
      "llm_model": "meta/llama-3.1-8b-instruct",
      "latency_ms": 4257,
      "token_usage": {"prompt_tokens": 185, "completion_tokens": 270, "total_tokens": 455}
    }
  ]
}
```

---

### `GET /api/v1/audit/{session_id}?limit=50`

Audit log for a specific session.

---

## Supported PII Types

| Type | Input Example | Token |
|------|--------------|-------|
| Person | `Hans Peter` | `[PERSON_1]` |
| Email | `hans@example.com` | `[EMAIL_1]` |
| Phone | `+41 79 123 45 67` | `[PHONE_1]` |
| Location | `Bahnhofstrasse 1, Zurich` | `[LOCATION_1]` |
| Swiss IBAN | `CH9300000000000000000` | `[IBAN_1]` |
| Swiss AHV | `756.1234.5678.90` | `[AHV_1]` |
| Credit Card | `4111 1111 1111 1111` | `[CARD_1]` |
| IP Address | `192.168.1.1` | `[IP_1]` |

---

## Frontend Integration Examples

### Basic Request

```javascript
const API_BASE = 'http://localhost:8000';

async function sendToAirlock(prompt, role = 'admin', sessionId = null) {
  const body = { prompt, role };
  if (sessionId) body.session_id = sessionId;

  const res = await fetch(`${API_BASE}/api/v1/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.json();
}
```

### Usage

```javascript
// First request — session_id is auto-generated
const result = await sendToAirlock(
  'Send CHF 50,000 to Hans Peter, IBAN CH9300000000000000000'
);

console.log(result.masked_payload);
// → "Send CHF 50,000 to [PERSON_1], IBAN [IBAN_1]"

console.log(result.final_response);
// → "Send CHF 50,000 to Hans Peter, IBAN CH9300000000000000000" (admin)
// → "Send CHF 50,000 to [PERSON_1], IBAN [IBAN_1]" (auditor)

// Subsequent requests — pass session_id to continue the conversation
const next = await sendToAirlock(
  'What are the terms?',
  'admin',
  result.session_id
);
```

### Role Switching

```javascript
// Admin sees real data
const adminResult = await sendToAirlock(text, 'admin');

// Auditor sees only tokens
const auditorResult = await sendToAirlock(text, 'auditor');

// Difference:
adminResult.final_response   // → "...Hans Peter...CH9300000..."
auditorResult.final_response // → "...[PERSON_1]...[IBAN_1]..."
```

### Error Handling

```javascript
try {
  const result = await sendToAirlock(userInput);
  updateUI(result);
} catch (err) {
  if (err.message.includes('400')) {
    showError('Invalid role. Use "admin" or "auditor".');
  } else if (err.message.includes('5')) {
    showError('Server error. Please try again.');
  } else {
    showError('Network error. Is the backend running?');
  }
}
```

---

## Error Format

All errors are returned as:

```json
{
  "detail": "Error description in English"
}
```

| HTTP Status | Reason |
|-------------|--------|
| `200` | Success |
| `400` | Invalid request (bad role, empty prompt) |
| `404` | Session not found (or TTL expired) |
| `422` | Pydantic validation error (wrong field type) |
| `500` | Internal error (LLM, database) |
| `502` | LLM API unavailable |

---

## Configuration (.env)

```bash
# LLM — NVIDIA NIM (current)
NVAPI_KEY=nvapi-...
LLM_BASE_URL=https://integrate.api.nvidia.com/v1
LLM_MODEL=meta/llama-3.1-8b-instruct

# Redis
REDIS_URL=redis://localhost:6379/0
SESSION_TTL=3600

# Database
DATABASE_URL=sqlite:///airlock_audit.db
# DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/airlock

# Server
APP_HOST=0.0.0.0
APP_PORT=8000
```

---

## Dependencies

```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
python-dotenv>=1.0.0
redis>=5.0.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
openai>=1.58.0
presidio-analyzer>=2.2.354
spacy>=3.8.0
```

Core engine: `../core/` (Presidio + Swiss regex patterns)
