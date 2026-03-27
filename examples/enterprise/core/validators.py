"""Input validation and sanitization utilities."""

from __future__ import annotations

import html
import re

from core.constants import SUPPORTED_AUDIO_FORMATS, SUPPORTED_LANGUAGES
from core.exceptions import ValidationError


def sanitize_text(text: str) -> str:
    """Sanitize user-supplied text: strip, escape HTML, limit length."""
    text = text.strip()
    text = html.escape(text, quote=True)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return text


def validate_language_code(code: str) -> str:
    """Validate and return a canonical language code."""
    code = code.strip().lower()
    # Allow 'unknown' / 'auto' for auto-detection
    if code in {"unknown", "auto"}:
        return "unknown"
    # Try exact match
    for supported in SUPPORTED_LANGUAGES:
        if code == supported.lower():
            return supported
    # Try short code (e.g. "hi" → "hi-IN")
    for supported in SUPPORTED_LANGUAGES:
        if supported.lower().startswith(code):
            return supported
    raise ValidationError(
        f"Unsupported language code: {code!r}. "
        f"Supported: {list(SUPPORTED_LANGUAGES.keys())}",
        field="language_code",
    )


def validate_audio_format(filename: str) -> str:
    """Validate file extension is a supported audio format."""
    ext = filename.rsplit(".", maxsplit=1)[-1].lower() if "." in filename else ""
    if ext not in SUPPORTED_AUDIO_FORMATS:
        raise ValidationError(
            f"Unsupported audio format: .{ext}. Supported: {SUPPORTED_AUDIO_FORMATS}",
            field="audio_format",
        )
    return ext


def validate_text_length(text: str, max_length: int, field_name: str = "text") -> None:
    """Raise if text exceeds maximum allowed length."""
    if len(text) > max_length:
        raise ValidationError(
            f"{field_name} exceeds maximum length of {max_length} characters "
            f"(got {len(text)})",
            field=field_name,
        )


def validate_non_empty(value: str, field_name: str = "input") -> str:
    """Raise if value is empty after stripping."""
    value = value.strip()
    if not value:
        raise ValidationError(f"{field_name} must not be empty", field=field_name)
    return value
