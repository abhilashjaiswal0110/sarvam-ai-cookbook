"""Rate-limiting and audit-logging middleware."""

from __future__ import annotations

import time
import uuid
from collections import defaultdict
from threading import Lock
from typing import Any

from core.exceptions import RateLimitError
from core.logging_config import get_logger

_audit_logger = get_logger("audit")


# ── Rate Limiter (Token Bucket) ───────────────────────────────────

class RateLimiter:
    """Thread-safe token-bucket rate limiter.

    Each *client_id* gets its own bucket so multiple use-cases
    running in the same process don't starve each other.
    """

    def __init__(self, requests_per_minute: int = 60, burst: int = 10) -> None:
        self._rate = requests_per_minute / 60.0  # tokens per second
        self._burst = float(burst)
        self._buckets: dict[str, tuple[float, float]] = {}
        self._lock = Lock()

    def acquire(self, client_id: str = "default") -> None:
        """Consume one token or raise RateLimitError."""
        with self._lock:
            now = time.monotonic()
            tokens, last = self._buckets.get(client_id, (self._burst, now))
            elapsed = now - last
            tokens = min(self._burst, tokens + elapsed * self._rate)
            if tokens < 1.0:
                retry_after = (1.0 - tokens) / self._rate
                raise RateLimitError(retry_after=retry_after)
            self._buckets[client_id] = (tokens - 1.0, now)


# ── Audit Logger ──────────────────────────────────────────────────

class AuditLogger:
    """Structured audit trail for API interactions."""

    def __init__(self, enabled: bool = True) -> None:
        self._enabled = enabled
        self._stats: dict[str, int] = defaultdict(int)

    def log_request(
        self,
        *,
        usecase: str,
        action: str,
        language: str | None = None,
        request_id: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> str:
        """Log an API request and return the request_id."""
        request_id = request_id or uuid.uuid4().hex[:12]
        if self._enabled:
            _audit_logger.info(
                "api_request",
                usecase=usecase,
                action=action,
                language=language or "unknown",
                request_id=request_id,
                **(extra or {}),
            )
        self._stats[f"{usecase}.{action}"] += 1
        return request_id

    def log_response(
        self,
        *,
        request_id: str,
        status: str = "success",
        duration_ms: float | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        if self._enabled:
            _audit_logger.info(
                "api_response",
                request_id=request_id,
                status=status,
                duration_ms=round(duration_ms, 2) if duration_ms else None,
                **(extra or {}),
            )

    def log_error(
        self,
        *,
        request_id: str,
        error_code: str,
        message: str,
    ) -> None:
        if self._enabled:
            _audit_logger.error(
                "api_error",
                request_id=request_id,
                error_code=error_code,
                error_message=message,
            )

    def get_stats(self) -> dict[str, int]:
        return dict(self._stats)
