"""Tests for the PII masking module."""

from __future__ import annotations

from core.logging_config import mask_pii


class TestPIIMasking:
    def test_masks_aadhaar(self) -> None:
        text = "My Aadhaar is 1234 5678 9012"
        masked = mask_pii(text)
        assert "1234" not in masked
        assert "****" in masked

    def test_masks_pan(self) -> None:
        text = "PAN: ABCDE1234F"
        masked = mask_pii(text)
        assert "ABCDE1234F" not in masked

    def test_masks_phone(self) -> None:
        text = "Call me at +91 9876543210"
        masked = mask_pii(text)
        assert "9876543210" not in masked

    def test_masks_email(self) -> None:
        text = "Email: user@example.com"
        masked = mask_pii(text)
        assert "user@example.com" not in masked
        assert "***@***.***" in masked

    def test_preserves_normal_text(self) -> None:
        text = "Hello, how are you today?"
        assert mask_pii(text) == text
