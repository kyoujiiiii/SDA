"""Redis-backed token vault with in-memory fallback."""

import time
import threading
from dataclasses import dataclass, field
from typing import Dict, Optional, List

try:
    import redis as redis_lib
except ImportError:
    redis_lib = None

from config import REDIS_URL, SESSION_TTL

PREFIX = "airlock:vault"


@dataclass
class _SessionRecord:
    mapping: Dict[str, str] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    request_count: int = 0


class TokenVault:
    def __init__(self, ttl: int = SESSION_TTL):
        self._ttl = ttl
        self._lock = threading.Lock()
        self._redis = self._connect()
        self._mem: Dict[str, _SessionRecord] = {}
        self._total_stores = 0
        self._total_retrievals = 0
        self._total_sessions = 0
        if self._redis is None:
            print("WARNING: Redis unavailable, vault falling back to in-memory.")
        else:
            print(f"TokenVault connected to Redis at {REDIS_URL}")

    @property
    def backend(self) -> str:
        return "redis" if self._redis else "memory"

    # ---- Redis helpers ----
    def _connect(self):
        if redis_lib is None:
            return None
        try:
            r = redis_lib.Redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=1)
            r.ping()
            return r
        except Exception:
            return None

    def _k_map(self, sid: str) -> str:
        return f"{PREFIX}:{sid}:map"

    def _k_meta(self, sid: str) -> str:
        return f"{PREFIX}:{sid}:meta"

    def _touch(self, sid: str) -> None:
        pipe = self._redis.pipeline()
        pipe.expire(self._k_map(sid), self._ttl)
        pipe.expire(self._k_meta(sid), self._ttl)
        pipe.execute()

    # ---- Public API ----
    def store_mapping(self, session_id: str, token: str, value: str) -> None:
        if self._redis:
            now = time.time()
            is_new = not self._redis.exists(self._k_meta(session_id))
            pipe = self._redis.pipeline()
            pipe.hset(self._k_map(session_id), token, value)
            if is_new:
                pipe.hset(self._k_meta(session_id), mapping={"created_at": now, "last_accessed": now, "request_count": 0})
                pipe.incr(f"{PREFIX}:stats:sessions")
            else:
                pipe.hset(self._k_meta(session_id), "last_accessed", now)
            pipe.incr(f"{PREFIX}:stats:stores")
            pipe.execute()
            self._touch(session_id)
            return

        with self._lock:
            if session_id not in self._mem:
                self._mem[session_id] = _SessionRecord()
                self._total_sessions += 1
            rec = self._mem[session_id]
            rec.mapping[token] = value
            rec.last_accessed = time.time()
            self._total_stores += 1

    def get_all_mappings(self, session_id: str) -> Dict[str, str]:
        if self._redis:
            if not self._redis.exists(self._k_meta(session_id)):
                return {}
            self._touch(session_id)
            return self._redis.hgetall(self._k_map(session_id))

        with self._lock:
            rec = self._mem.get(session_id)
            if not rec:
                return {}
            rec.last_accessed = time.time()
            return rec.mapping.copy()

    def session_exists(self, session_id: str) -> bool:
        if self._redis:
            return bool(self._redis.exists(self._k_meta(session_id)))
        return session_id in self._mem

    def delete_session(self, session_id: str) -> bool:
        if self._redis:
            existed = bool(self._redis.exists(self._k_meta(session_id)))
            self._redis.delete(self._k_map(session_id), self._k_meta(session_id))
            return existed

        with self._lock:
            if session_id in self._mem:
                del self._mem[session_id]
                return True
            return False

    def get_session_info(self, session_id: str) -> Optional[Dict]:
        if self._redis:
            meta = self._redis.hgetall(self._k_meta(session_id))
            if not meta:
                return None
            created = float(meta.get("created_at", 0))
            return {
                "session_id": session_id,
                "created_at": created,
                "last_accessed": float(meta.get("last_accessed", 0)),
                "token_count": self._redis.hlen(self._k_map(session_id)),
                "request_count": int(meta.get("request_count", 0)),
                "age_seconds": time.time() - created,
            }

        with self._lock:
            rec = self._mem.get(session_id)
            if not rec:
                return None
            return {
                "session_id": session_id,
                "created_at": rec.created_at,
                "last_accessed": rec.last_accessed,
                "token_count": len(rec.mapping),
                "request_count": rec.request_count,
                "age_seconds": time.time() - rec.created_at,
            }

    def increment_request_count(self, session_id: str) -> None:
        if self._redis:
            if self._redis.exists(self._k_meta(session_id)):
                self._redis.hincrby(self._k_meta(session_id), "request_count", 1)
                self._touch(session_id)
            return

        with self._lock:
            rec = self._mem.get(session_id)
            if rec:
                rec.request_count += 1

    def cleanup_expired(self) -> int:
        if self._redis:
            return 0

        with self._lock:
            now = time.time()
            expired = [sid for sid, rec in self._mem.items()
                       if now - rec.last_accessed > self._ttl]
            for sid in expired:
                del self._mem[sid]
            return len(expired)

    def get_stats(self) -> Dict:
        if self._redis:
            active = len(self._redis.keys(f"{PREFIX}:*:meta"))
            mappings = sum(self._redis.hlen(k) for k in self._redis.keys(f"{PREFIX}:*:map"))
            return {
                "backend": "redis",
                "active_sessions": active,
                "total_mappings": mappings,
                "total_stores": int(self._redis.get(f"{PREFIX}:stats:stores") or 0),
                "total_sessions": int(self._redis.get(f"{PREFIX}:stats:sessions") or 0),
            }

        with self._lock:
            return {
                "backend": "memory",
                "active_sessions": len(self._mem),
                "total_mappings": sum(len(r.mapping) for r in self._mem.values()),
                "total_stores": self._total_stores,
                "total_sessions": self._total_sessions,
            }


vault = TokenVault()
