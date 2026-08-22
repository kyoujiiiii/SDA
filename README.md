# Swiss Data Airlock

> **BärnHäckt 2026** — Hackathon project for Natron.io challenge

A protective proxy layer that intercepts outgoing data, detects sensitive entities (PII, financial data, secrets), and replaces them with tokens before sending to external LLMs. Authorized users get the original data back; everyone else sees only placeholders.

## Architecture

```
User Request → [Airlock Proxy] → Masked Text → External LLM
                    ↓                              ↓
              Token Vault                    LLM Response
                    ↓                              ↓
User Response ← [Airlock Proxy] ← Unmasked Text ←┘
```

## Project Structure

```
BernHack/
├── core/           # PII detection engine (Python library)
├── back/           # FastAPI backend + detection API
├── front/          # React + Vite + Tailwind frontend
├── docker-compose.yml
└── .env.example
```

`core/` is a Python library imported directly by `back/`. Both must be present in the correct directory structure.

## Quick Start (Docker)

### 1. Clone

```bash
git clone https://github.com/kostiakova/BernHack.git
cd BernHack
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and add your API key (see Environment Variables below)
```

### 3. Run

```bash
docker compose up --build
```

That's it. The app builds and starts automatically.

### 4. Open

| Service | URL |
|---------|-----|
| Frontend UI | http://localhost:8081 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

### Docker Services

| Service | Port | Description |
|---------|------|-------------|
| `redis` | 6380 | Token vault storage |
| `back` | 8000 | FastAPI proxy + detection engine |
| `front` | 8081 | React UI (Vite build -> nginx) |

### Useful Commands

```bash
# Start in background
docker compose up -d --build

# View logs
docker compose logs -f back

# Stop
docker compose down

# Rebuild from scratch
docker compose down --rmi local && docker compose up --build
```

---

## Option B: Run manually (development)

### Prerequisites

- Python 3.11+
- Node.js 18+
- Redis (optional — falls back to in-memory vault)

### Backend

```bash
# From project root
pip install -r back/requirements.txt
python -m spacy download en_core_web_lg

cd back
python main.py
```

`back/main.py` adds `../core` to `sys.path` at startup, so `core/` must exist as a sibling directory.

### Frontend

```bash
cd front
npm install
npm run dev
```

Dev server runs at http://localhost:5173 and proxies API requests to http://localhost:8000.

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NVAPI_KEY` | NVIDIA NIM API key | — |
| `LLM_BASE_URL` | Custom LLM endpoint | — |
| `LLM_MODEL` | LLM model name | `gpt-4o-mini` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `SESSION_TTL` | Session timeout in seconds | `3600` |
| `DATABASE_URL` | SQLite/PostgreSQL connection | `sqlite:///airlock_audit.db` |

Without an API key, the backend runs in **mock mode** — it will return placeholder LLM responses but full PII masking/demasking still works.

## How It Works

1. **Detection**: Hybrid regex + NER models detect PII (names, emails, phones, Swiss IBAN, AHV numbers)
2. **Tokenization**: Detected entities replaced with `[PERSON_1]`, `[IBAN_1]`, etc.
3. **Vault**: Token-to-value mapping stored locally (Redis or in-memory)
4. **LLM Call**: Only masked text reaches the external LLM
5. **Detokenization**: Authorized users get original values restored

## License

Internal hackathon project — not for production use.
