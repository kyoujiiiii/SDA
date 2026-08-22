"""Swiss Data Airlock — FastAPI backend."""

import sys
import time
import uuid
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

# Ensure back/ is first on sys.path (avoids conflict with root-level services/)
_BACK_DIR = str(Path(__file__).resolve().parent)
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
for _p in (_BACK_DIR, _PROJECT_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from config import APP_HOST, APP_PORT
from database import init_db
from airlock.vault import vault
from airlock.llm import llm_service
from airlock.audit import audit_service

# Import core engine
from core import AirlockEngine


# ---- Pydantic models ----

class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Session ID (auto-generated if omitted)")
    prompt: str = Field(..., min_length=1, max_length=10000)
    role: str = Field("admin", description="'admin' sees real values, 'auditor' sees masked")
    model: Optional[str] = Field(None, description="Override LLM model")


class EntityOut(BaseModel):
    entity_type: str
    start: int
    end: int
    original_value: str
    token: str
    score: float


class ChatResponse(BaseModel):
    session_id: str
    original_prompt: str
    masked_payload: str
    llm_raw_response: str
    final_response: str
    latency_ms: int
    detected_entities: list[EntityOut]
    role: str
    llm_model: str
    token_usage: dict


# ---- App ----

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print(f"Vault backend: {vault.backend}")
    print(f"LLM mode: {'mock' if llm_service.use_mock else 'live'}")
    yield

app = FastAPI(title="Swiss Data Airlock", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (index.html lives here)
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Core engine (single instance, reused)
engine = AirlockEngine()


# ---- Routes ----

@app.get("/", response_class=HTMLResponse)
async def root():
    index = STATIC_DIR / "index.html"
    return HTMLResponse(content=index.read_text(encoding="utf-8"))


@app.get("/health")
async def health():
    return {"status": "ok", "vault": vault.backend, "llm": "mock" if llm_service.use_mock else "openai"}


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if req.role not in ("admin", "auditor"):
        raise HTTPException(400, "Role must be 'admin' or 'auditor'")

    session_id = req.session_id or str(uuid.uuid4())
    t0 = time.time()

    # 1. Mask
    result = engine.mask(req.prompt)

    # 2. Store mapping in vault
    for token, value in result.mapping.items():
        vault.store_mapping(session_id, token, value)
    vault.increment_request_count(session_id)

    # 3. Call LLM with masked text
    llm_resp = llm_service.chat(result.masked_text, model=req.model)

    # 4. Unmask based on role
    if req.role == "admin":
        final = engine.unmask(llm_resp.content, result.mapping)
    else:
        final = llm_resp.content

    ms = int((time.time() - t0) * 1000)

    # 5. Audit (masked only)
    audit_service.log_request(
        session_id=session_id,
        role=req.role,
        masked_prompt=result.masked_text,
        llm_response=llm_resp.content,
        detected_entities=[
            {"entity_type": e.entity_type, "token": e.token, "original_value": e.original_value}
            for e in result.entities
        ],
        llm_model=llm_resp.model,
        latency_ms=ms,
        token_usage=llm_resp.usage,
    )

    return ChatResponse(
        session_id=session_id,
        original_prompt=req.prompt,
        masked_payload=result.masked_text,
        llm_raw_response=llm_resp.content,
        final_response=final,
        latency_ms=ms,
        detected_entities=[EntityOut(**e.__dict__) for e in result.entities],
        role=req.role,
        llm_model=llm_resp.model,
        token_usage=llm_resp.usage,
    )


@app.get("/api/v1/vault/{session_id}")
async def get_vault(session_id: str):
    if not vault.session_exists(session_id):
        raise HTTPException(404, f"Session {session_id} not found")
    return {
        "session_id": session_id,
        "mappings": vault.get_all_mappings(session_id),
        "session_info": vault.get_session_info(session_id),
    }


@app.delete("/api/v1/vault/{session_id}")
async def delete_session(session_id: str):
    if not vault.delete_session(session_id):
        raise HTTPException(404, f"Session {session_id} not found")
    return {"deleted": True, "session_id": session_id}


@app.get("/api/v1/stats")
async def stats():
    return {"vault": vault.get_stats(), "llm": llm_service.get_stats(), "audit": audit_service.get_stats()}


@app.get("/api/v1/audit")
async def audit_log(limit: int = 20):
    return {"entries": audit_service.get_recent(limit=limit)}


@app.get("/api/v1/audit/{session_id}")
async def session_audit(session_id: str, limit: int = 50):
    return {"session_id": session_id, "entries": audit_service.get_session_history(session_id, limit)}


# ---- Run ----

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=APP_HOST, port=APP_PORT, reload=True)
