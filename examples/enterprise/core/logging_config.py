"""Structured logging with PII masking and audit trail support."""

from __future__ import annotations

import logging
import re
import sys
from typing import Any

import structlog

# ── PII Masking ────────────────────────────────────────────────────
_PII_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # Aadhaar: 12-digit number (with optional spaces/dashes)
    (re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"), "****-****-****"),
    # PAN: 5 letters + 4 digits + 1 letter
    (re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b", re.IGNORECASE), "**********"),
    # Indian phone: +91 or 0 prefix, 10 digits
    (re.compile(r"(?:\+91[\s-]?|0)?\d{10}\b"), "****-****-**"),
    # Email
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b"), "***@***.***"),
]


def mask_pii(text: str) -> str:
    """Replace detectable PII patterns with masked placeholders."""
    for pattern, replacement in _PII_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


class PIIMaskingProcessor:
    """Structlog processor that masks PII in log event values."""

    def __call__(
        self, logger: Any, method_name: str, event_dict: dict[str, Any]
    ) -> dict[str, Any]:
        for key, value in event_dict.items():
            if isinstance(value, str):
                event_dict[key] = mask_pii(value)
        return event_dict


def configure_logging(
    level: str = "INFO",
    fmt: str = "json",
    mask_pii_enabled: bool = True,
) -> None:
    """Configure structured logging for the application."""
    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if mask_pii_enabled:
        processors.append(PIIMaskingProcessor())

    if fmt == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a named structured logger."""
    return structlog.get_logger(name)  # type: ignore[no-any-return]
