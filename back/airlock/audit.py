"""Audit service — SQLAlchemy-backed persistent log of masked requests."""

import time
from typing import Dict, List

from sqlalchemy.orm import Session

from database import SessionLocal
from models import AuditLog


class AuditService:
    def log_request(
        self,
        session_id: str,
        role: str,
        masked_prompt: str,
        llm_response: str,
        detected_entities: List[Dict],
        llm_model: str,
        latency_ms: int,
        token_usage: Dict,
    ) -> None:
        db: Session = SessionLocal()
        try:
            entry = AuditLog(
                session_id=session_id,
                role=role,
                created_at=time.time(),
                masked_prompt=masked_prompt,
                llm_response=llm_response,
                entity_types=[e["entity_type"] for e in detected_entities],
                entity_count=len(detected_entities),
                llm_model=llm_model,
                latency_ms=latency_ms,
                token_usage=token_usage,
            )
            db.add(entry)
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def get_recent(self, limit: int = 20) -> List[Dict]:
        db: Session = SessionLocal()
        try:
            rows = (
                db.query(AuditLog)
                .order_by(AuditLog.id.desc())
                .limit(limit)
                .all()
            )
            return [self._to_dict(r) for r in rows]
        finally:
            db.close()

    def get_session_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        db: Session = SessionLocal()
        try:
            rows = (
                db.query(AuditLog)
                .filter(AuditLog.session_id == session_id)
                .order_by(AuditLog.id.desc())
                .limit(limit)
                .all()
            )
            return [self._to_dict(r) for r in rows]
        finally:
            db.close()

    def get_stats(self) -> Dict:
        db: Session = SessionLocal()
        try:
            total = db.query(AuditLog).count()
            sessions = db.query(AuditLog.session_id).distinct().count()
            return {"total_requests": total, "distinct_sessions": sessions}
        finally:
            db.close()

    @staticmethod
    def _to_dict(row: AuditLog) -> Dict:
        return {
            "id": row.id,
            "session_id": row.session_id,
            "role": row.role,
            "created_at": row.created_at,
            "masked_prompt": row.masked_prompt,
            "llm_response": row.llm_response,
            "entity_types": row.entity_types,
            "entity_count": row.entity_count,
            "llm_model": row.llm_model,
            "latency_ms": row.latency_ms,
            "token_usage": row.token_usage,
        }


audit_service = AuditService()
