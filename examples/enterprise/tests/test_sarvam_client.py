"""Tests for the SarvamClient — focused on logic, not live API calls."""

from __future__ import annotations

import pytest

from core.exceptions import AuthenticationError, ValidationError
from core.models import ChatMessage


class TestSarvamClientInit:
    def test_empty_key_raises(self) -> None:
        from core.sarvam_client import SarvamClient

        with pytest.raises(AuthenticationError):
            SarvamClient("")


class TestSarvamClientChat:
    def test_chat_returns_text(self, mock_sarvam_client) -> None:
        mock_sarvam_client._request.return_value = {
            "choices": [
                {"message": {"role": "assistant", "content": "Hello!"}, "finish_reason": "stop"}
            ],
            "usage": {"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
        }
        result = mock_sarvam_client.chat(
            [ChatMessage(role="user", content="Hi")]
        )
        assert result == "Hello!"
        mock_sarvam_client._request.assert_called_once()


class TestSarvamClientTranslate:
    def test_translate_validates_language(self, mock_sarvam_client) -> None:
        with pytest.raises(ValidationError, match="Unsupported"):
            mock_sarvam_client.translate("hello", "xx-XX")

    def test_translate_validates_non_empty(self, mock_sarvam_client) -> None:
        with pytest.raises(ValidationError, match="must not be empty"):
            mock_sarvam_client.translate("", "hi-IN")


class TestSarvamClientTTS:
    def test_tts_validates_language(self, mock_sarvam_client) -> None:
        with pytest.raises(ValidationError, match="Unsupported"):
            mock_sarvam_client.text_to_speech("hello", "xx-XX")


class TestSarvamClientDetectLanguage:
    def test_detect_returns_model(self, mock_sarvam_client) -> None:
        mock_sarvam_client._request.return_value = {
            "language_code": "hi-IN",
            "script_code": "Devanagari",
            "confidence": 0.95,
        }
        result = mock_sarvam_client.detect_language("नमस्ते")
        assert result.language_code == "hi-IN"
