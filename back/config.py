"""Application configuration loaded from environment / .env file."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from back/ directory
load_dotenv(Path(__file__).parent / ".env")


# ---- Redis ----
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
SESSION_TTL: int = int(os.getenv("SESSION_TTL", "3600"))

# ---- Database ----
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///airlock_audit.db")

# ---- LLM (OpenAI or NVIDIA NIM — both use OpenAI-compatible SDK) ----
LLM_API_KEY: str = os.getenv("OPENAI_API_KEY", "") or os.getenv("NVAPI_KEY", "")
LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "")  # e.g. https://integrate.api.nvidia.com/v1
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

# ---- Server ----
APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
