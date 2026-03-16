from __future__ import annotations

import hashlib
import threading
import time
from typing import Any


class Cache:
    def __init__(self, ttl_seconds: int = 1800) -> None:
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock = threading.Lock()
        self._ttl = ttl_seconds

    def _make_key(self, *args: Any) -> str:
        raw = repr(args)
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, *key_parts: Any) -> Any | None:
        key = self._make_key(*key_parts)
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if time.time() > expires_at:
                del self._store[key]
                return None
            return value

    def set(self, value: Any, *key_parts: Any) -> None:
        key = self._make_key(*key_parts)
        expires_at = time.time() + self._ttl
        with self._lock:
            self._store[key] = (value, expires_at)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


# Singleton instance
analysis_cache = Cache()
