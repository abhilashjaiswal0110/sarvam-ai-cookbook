"""Unit tests for SarvamClient — all external HTTP calls are mocked."""

import sys
import os
import base64
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sarvam_client import SarvamClient, SarvamAPIError


@pytest.fixture
def client():
    return SarvamClient("test-api-key-12345")


def _mock_response(json_data: dict, status_code: int = 200) -> MagicMock:
    """Build a mock requests.Response."""
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data
    if status_code >= 400:
        from requests import HTTPError
        mock.raise_for_status.side_effect = HTTPError(f"HTTP {status_code}")
    else:
        mock.raise_for_status.return_value = None
    return mock


# ── detect_language ──────────────────────────────────────────────────────────

class TestDetectLanguage:
    def test_returns_language_code(self, client):
        mock_resp = _mock_response({"language_code": "hi-IN", "script_code": "Deva"})
        with patch("requests.post", return_value=mock_resp) as mock_post:
            result = client.detect_language("नमस्ते")
        assert result["language_code"] == "hi-IN"
        assert result["script_code"] == "Deva"
        mock_post.assert_called_once()

    def test_uses_correct_endpoint_and_header(self, client):
        mock_resp = _mock_response({"language_code": "en-IN"})
        with patch("requests.post", return_value=mock_resp) as mock_post:
            client.detect_language("hello")
        call_kwargs = mock_post.call_args
        assert "text-lid" in call_kwargs[0][0]
        assert call_kwargs[1]["headers"]["api-subscription-key"] == "test-api-key-12345"

    def test_raises_sarvam_api_error_on_http_failure(self, client):
        mock_resp = _mock_response({}, status_code=401)
        with patch("requests.post", return_value=mock_resp):
            with pytest.raises(SarvamAPIError):
                client.detect_language("hello")

    def test_raises_sarvam_api_error_on_network_failure(self, client):
        import requests as req_lib
        with patch("requests.post", side_effect=req_lib.ConnectionError("timeout")):
            with pytest.raises(SarvamAPIError):
                client.detect_language("hello")


# ── translate ────────────────────────────────────────────────────────────────

class TestTranslate:
    def test_same_language_returns_original(self, client):
        with patch("requests.post") as mock_post:
            result = client.translate("hello", source_lang="en-IN", target_lang="en-IN")
        assert result == "hello"
        mock_post.assert_not_called()

    def test_translates_to_english(self, client):
        mock_resp = _mock_response({"translated_text": "Hello, how are you?"})
        with patch("requests.post", return_value=mock_resp):
            result = client.translate("नमस्ते, कैसे हो?", source_lang="hi-IN", target_lang="en-IN")
        assert result == "Hello, how are you?"

    def test_raises_on_api_error(self, client):
        mock_resp = _mock_response({}, status_code=500)
        with patch("requests.post", return_value=mock_resp):
            with pytest.raises(SarvamAPIError):
                client.translate("text", source_lang="hi-IN")

    def test_payload_contains_correct_fields(self, client):
        mock_resp = _mock_response({"translated_text": "ok"})
        with patch("requests.post", return_value=mock_resp) as mock_post:
            client.translate("hello", "en-IN", "hi-IN")
        payload = mock_post.call_args[1]["json"]
        assert payload["input"] == "hello"
        assert payload["source_language_code"] == "en-IN"
        assert payload["target_language_code"] == "hi-IN"


# ── chat ─────────────────────────────────────────────────────────────────────

class TestChat:
    def test_returns_assistant_reply(self, client):
        mock_resp = _mock_response({
            "choices": [{"message": {"content": "Restart your VPN client."}}]
        })
        with patch("requests.post", return_value=mock_resp):
            reply = client.chat([{"role": "user", "content": "VPN not working"}])
        assert reply == "Restart your VPN client."

    def test_system_prompt_prepended_automatically(self, client):
        mock_resp = _mock_response({
            "choices": [{"message": {"content": "reply"}}]
        })
        with patch("requests.post", return_value=mock_resp) as mock_post:
            client.chat([{"role": "user", "content": "hi"}])
        payload = mock_post.call_args[1]["json"]
        assert payload["messages"][0]["role"] == "system"

    def test_system_prompt_not_duplicated_when_present(self, client):
        mock_resp = _mock_response({
            "choices": [{"message": {"content": "reply"}}]
        })
        messages = [
            {"role": "system", "content": "Custom system prompt"},
            {"role": "user", "content": "hi"},
        ]
        with patch("requests.post", return_value=mock_resp) as mock_post:
            client.chat(messages)
        payload = mock_post.call_args[1]["json"]
        system_messages = [m for m in payload["messages"] if m["role"] == "system"]
        assert len(system_messages) == 1
        assert system_messages[0]["content"] == "Custom system prompt"

    def test_reasoning_effort_forwarded(self, client):
        mock_resp = _mock_response({
            "choices": [{"message": {"content": "reply"}}]
        })
        with patch("requests.post", return_value=mock_resp) as mock_post:
            client.chat([{"role": "user", "content": "hi"}], reasoning_effort="high")
        payload = mock_post.call_args[1]["json"]
        assert payload["reasoning_effort"] == "high"

    def test_history_trimmed_to_max(self, client):
        """Conversation history beyond MAX_CHAT_HISTORY should be trimmed."""
        mock_resp = _mock_response({
            "choices": [{"message": {"content": "reply"}}]
        })
        # Build 20 user messages (exceeds MAX_CHAT_HISTORY=10)
        messages = [{"role": "user", "content": f"msg {i}"} for i in range(20)]
        with patch("requests.post", return_value=mock_resp) as mock_post:
            client.chat(messages)
        payload = mock_post.call_args[1]["json"]
        # system + at most MAX_CHAT_HISTORY messages
        assert len(payload["messages"]) <= 11  # 1 system + 10 history

    def test_raises_on_api_error(self, client):
        mock_resp = _mock_response({}, status_code=429)
        with patch("requests.post", return_value=mock_resp):
            with pytest.raises(SarvamAPIError):
                client.chat([{"role": "user", "content": "hi"}])


# ── text_to_speech ────────────────────────────────────────────────────────────

class TestTextToSpeech:
    def test_returns_audio_bytes(self, client):
        fake_audio = base64.b64encode(b"FAKE_AUDIO_DATA").decode()
        mock_resp = _mock_response({"audios": [fake_audio]})
        with patch("requests.post", return_value=mock_resp):
            result = client.text_to_speech("Hello", "en-IN")
        assert result == b"FAKE_AUDIO_DATA"

    def test_returns_none_on_api_error(self, client):
        import requests as req_lib
        with patch("requests.post", side_effect=req_lib.RequestException("error")):
            result = client.text_to_speech("Hello", "en-IN")
        assert result is None

    def test_returns_none_when_no_audios(self, client):
        mock_resp = _mock_response({"audios": []})
        with patch("requests.post", return_value=mock_resp):
            result = client.text_to_speech("Hello", "en-IN")
        assert result is None


# ── speech_to_text ────────────────────────────────────────────────────────────

class TestSpeechToText:
    def test_returns_transcript(self, client):
        mock_resp = _mock_response({"transcript": "My laptop won't turn on."})
        with patch("requests.post", return_value=mock_resp):
            result = client.speech_to_text(b"AUDIO", "en-IN")
        assert result == "My laptop won't turn on."

    def test_raises_on_api_error(self, client):
        mock_resp = _mock_response({}, status_code=422)
        with patch("requests.post", return_value=mock_resp):
            with pytest.raises(SarvamAPIError):
                client.speech_to_text(b"AUDIO", "en-IN")

    def test_language_unknown_omits_language_field(self, client):
        mock_resp = _mock_response({"transcript": "text"})
        with patch("requests.post", return_value=mock_resp) as mock_post:
            client.speech_to_text(b"AUDIO", language="unknown")
        data = mock_post.call_args[1]["data"]
        assert "language_code" not in data
