"""Tests for core validators."""

from __future__ import annotations

import pytest

from core.exceptions import ValidationError
from core.validators import (
    sanitize_text,
    validate_language_code,
    validate_non_empty,
    validate_text_length,
)


class TestSanitizeText:
    def test_strips_whitespace(self) -> None:
        assert sanitize_text("  hello  ") == "hello"

    def test_collapses_whitespace(self) -> None:
        assert sanitize_text("hello   world") == "hello world"

    def test_escapes_html(self) -> None:
        result = sanitize_text("<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result


class TestValidateLanguageCode:
    def test_valid_full_code(self) -> None:
        assert validate_language_code("hi-IN") == "hi-IN"

    def test_valid_short_code(self) -> None:
        assert validate_language_code("hi") == "hi-IN"

    def test_unknown(self) -> None:
        assert validate_language_code("unknown") == "unknown"

    def test_auto(self) -> None:
        assert validate_language_code("auto") == "unknown"

    def test_invalid_raises(self) -> None:
        with pytest.raises(ValidationError, match="Unsupported"):
            validate_language_code("xx-XX")


class TestValidateNonEmpty:
    def test_non_empty(self) -> None:
        assert validate_non_empty("hello") == "hello"

    def test_empty_raises(self) -> None:
        with pytest.raises(ValidationError, match="must not be empty"):
            validate_non_empty("   ")


class TestValidateTextLength:
    def test_within_limit(self) -> None:
        validate_text_length("short", 100)

    def test_exceeds_raises(self) -> None:
        with pytest.raises(ValidationError, match="exceeds maximum"):
            validate_text_length("x" * 101, 100)
