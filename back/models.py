"""SQLAlchemy ORM models."""

import time
from sqlalchemy import Column, Integer, String, Text, Float, JSON

from database import Base


class AuditLog(Base):
    """Persistent audit record — stores only masked payloads, never raw PII."""

    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)
    created_at = Column(Float, nullable=False, default=time.time)
    masked_prompt = Column(Text, nullable=False)
    llm_response = Column(Text, nullable=False)
    entity_types = Column(JSON, nullable=False)
    entity_count = Column(Integer, nullable=False, default=0)
    llm_model = Column(String)
    latency_ms = Column(Integer)
    token_usage = Column(JSON)
