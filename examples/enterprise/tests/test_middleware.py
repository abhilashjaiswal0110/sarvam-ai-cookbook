"""Tests for the middleware module (rate limiter, audit logger)."""

from __future__ import annotations

import pytest

from core.exceptions import RateLimitError
from core.middleware import AuditLogger, RateLimiter


class TestRateLimiter:
    def test_allows_within_limit(self) -> None:
        limiter = RateLimiter(requests_per_minute=600, burst=10)
        for _ in range(10):
            limiter.acquire("test")

    def test_raises_on_burst_exceeded(self) -> None:
        limiter = RateLimiter(requests_per_minute=60, burst=2)
        limiter.acquire("test")
        limiter.acquire("test")
        with pytest.raises(RateLimitError):
            limiter.acquire("test")

    def test_separate_client_ids(self) -> None:
        limiter = RateLimiter(requests_per_minute=60, burst=1)
        limiter.acquire("client_a")
        limiter.acquire("client_b")  # different bucket — should succeed


class TestAuditLogger:
    def test_log_request_returns_id(self) -> None:
        logger = AuditLogger(enabled=False)
        rid = logger.log_request(usecase="test", action="test_action")
        assert isinstance(rid, str)
        assert len(rid) > 0

    def test_stats_increment(self) -> None:
        logger = AuditLogger(enabled=False)
        logger.log_request(usecase="chat", action="send")
        logger.log_request(usecase="chat", action="send")
        assert logger.get_stats()["chat.send"] == 2
