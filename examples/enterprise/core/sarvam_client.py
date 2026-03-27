"""Unified Sarvam AI API client with retry, error handling, and audit logging."""

from __future__ import annotations

import time
from typing import IO, Any

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from core.constants import (
    CHAT_COMPLETIONS_URL,
    CHAT_MODEL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    DEFAULT_TTS_SPEAKER,
    LANGUAGE_ID_URL,
    MAX_TRANSLATE_CHARS,
    MAX_TTS_CHARS,
    STT_MODEL,
    STT_URL,
    TRANSLATE_MODEL,
    TRANSLATE_URL,
    TRANSLITERATE_URL,
    TTS_MODEL,
    TTS_URL,
)
from core.exceptions import APIError, AuthenticationError, RateLimitError
from core.logging_config import get_logger
from core.middleware import AuditLogger, RateLimiter
from core.models import (
    ChatMessage,
    ChatResponse,
    LanguageDetectionResponse,
    STTResponse,
    TranslateResponse,
    TransliterateResponse,
    TTSResponse,
)
from core.utils import chunk_text
from core.validators import (
    sanitize_text,
    validate_language_code,
    validate_non_empty,
    validate_text_length,
)

logger = get_logger("sarvam_client")

_REQUEST_TIMEOUT = 30  # seconds


class SarvamClient:
    """Production-grade wrapper around Sarvam AI REST APIs.

    Features:
    - Automatic retry with exponential backoff on transient errors
    - Rate limiting (token-bucket, configurable)
    - Audit logging for every request/response
    - Input validation and sanitization
    - Long-text chunking for translate/TTS
    """

    def __init__(
        self,
        api_key: str,
        *,
        rate_limit_rpm: int = 60,
        rate_limit_burst: int = 10,
        audit_enabled: bool = True,
    ) -> None:
        if not api_key:
            raise AuthenticationError()
        self._api_key = api_key
        self._rate_limiter = RateLimiter(rate_limit_rpm, rate_limit_burst)
        self._audit = AuditLogger(enabled=audit_enabled)

    # ── Header helpers ─────────────────────────────────────────────

    def _bearer_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def _subscription_headers(self) -> dict[str, str]:
        return {
            "api-subscription-key": self._api_key,
            "Content-Type": "application/json",
        }

    def _subscription_headers_no_ct(self) -> dict[str, str]:
        return {"api-subscription-key": self._api_key}

    # ── Low-level request with error mapping ───────────────────────

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        stop=stop_after_attempt(4),
        reraise=True,
    )
    def _request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        usecase: str = "core",
        action: str = "request",
    ) -> dict[str, Any]:
        self._rate_limiter.acquire(usecase)
        request_id = self._audit.log_request(usecase=usecase, action=action)
        start = time.monotonic()

        try:
            resp = requests.request(
                method,
                url,
                headers=headers,
                json=json,
                data=data,
                files=files,
                timeout=_REQUEST_TIMEOUT,
            )
        except requests.exceptions.Timeout as exc:
            self._audit.log_error(
                request_id=request_id,
                error_code="TIMEOUT",
                message=str(exc),
            )
            raise APIError("Request timed out", status_code=408) from exc
        except requests.exceptions.ConnectionError as exc:
            self._audit.log_error(
                request_id=request_id,
                error_code="CONNECTION",
                message=str(exc),
            )
            raise APIError("Connection failed", status_code=503) from exc

        elapsed_ms = (time.monotonic() - start) * 1000

        if resp.status_code == 403:
            raise AuthenticationError()
        if resp.status_code == 429:
            raise RateLimitError()
        if resp.status_code >= 400:
            body = resp.text[:500]
            self._audit.log_error(
                request_id=request_id,
                error_code=f"HTTP_{resp.status_code}",
                message=body,
            )
            raise APIError(
                f"API error {resp.status_code}: {body}",
                status_code=resp.status_code,
            )

        result = resp.json()
        self._audit.log_response(
            request_id=request_id,
            status="success",
            duration_ms=elapsed_ms,
        )
        return result

    # ── Chat Completions ───────────────────────────────────────────

    def chat(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        reasoning_effort: str | None = None,
        wiki_grounding: bool = False,
    ) -> str:
        """Send a chat completion request and return the assistant's reply."""
        payload: dict[str, Any] = {
            "model": CHAT_MODEL,
            "messages": [m.model_dump() for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if reasoning_effort:
            payload["reasoning_effort"] = reasoning_effort
        if wiki_grounding:
            payload["wiki_grounding"] = True

        result = self._request(
            "POST",
            CHAT_COMPLETIONS_URL,
            headers=self._bearer_headers(),
            json=payload,
            usecase="chat",
            action="completions",
        )
        parsed = ChatResponse.model_validate(result)
        return parsed.choices[0].message.content

    # ── Text-to-Speech ─────────────────────────────────────────────

    def text_to_speech(
        self,
        text: str,
        target_language_code: str,
        *,
        speaker: str = DEFAULT_TTS_SPEAKER,
    ) -> list[bytes]:
        """Convert text to speech; auto-chunks if text exceeds limit.

        Returns a list of raw audio byte segments.
        """
        target_language_code = validate_language_code(target_language_code)
        text = validate_non_empty(text, "tts_text")

        chunks = chunk_text(text, MAX_TTS_CHARS)
        audio_segments: list[bytes] = []

        for chunk in chunks:
            result = self._request(
                "POST",
                TTS_URL,
                headers=self._subscription_headers(),
                json={
                    "inputs": [chunk],
                    "target_language_code": target_language_code,
                    "speaker": speaker,
                    "model": TTS_MODEL,
                },
                usecase="tts",
                action="synthesize",
            )
            parsed = TTSResponse.model_validate(result)
            import base64

            for b64 in parsed.audios:
                audio_segments.append(base64.b64decode(b64))

        return audio_segments

    # ── Speech-to-Text ─────────────────────────────────────────────

    def speech_to_text(
        self,
        audio_file: IO[bytes],
        filename: str,
        language_code: str = "unknown",
    ) -> STTResponse:
        """Transcribe an audio file."""
        if language_code != "unknown":
            language_code = validate_language_code(language_code)

        content_type = "audio/wav"
        if filename.endswith(".mp3"):
            content_type = "audio/mpeg"
        elif filename.endswith(".ogg"):
            content_type = "audio/ogg"

        result = self._request(
            "POST",
            STT_URL,
            headers=self._subscription_headers_no_ct(),
            files={"file": (filename, audio_file, content_type)},
            data={"language_code": language_code, "model": STT_MODEL},
            usecase="stt",
            action="transcribe",
        )
        return STTResponse(
            transcript=result.get("transcript", ""),
            language_code=result.get("language_code"),
        )

    # ── Translation ────────────────────────────────────────────────

    def translate(
        self,
        text: str,
        target_language_code: str,
        source_language_code: str = "auto",
        *,
        mode: str = "formal",
    ) -> str:
        """Translate text; auto-chunks for long content."""
        target_language_code = validate_language_code(target_language_code)
        text = validate_non_empty(text, "translate_text")

        chunks = chunk_text(text, MAX_TRANSLATE_CHARS)
        translated_parts: list[str] = []

        for chunk in chunks:
            result = self._request(
                "POST",
                TRANSLATE_URL,
                headers=self._subscription_headers(),
                json={
                    "input": chunk,
                    "source_language_code": source_language_code,
                    "target_language_code": target_language_code,
                    "mode": mode,
                    "model": TRANSLATE_MODEL,
                    "enable_preprocessing": True,
                },
                usecase="translate",
                action="translate",
            )
            parsed = TranslateResponse.model_validate(result)
            translated_parts.append(parsed.translated_text)

        return " ".join(translated_parts)

    # ── Transliteration ────────────────────────────────────────────

    def transliterate(self, text: str, target_script: str) -> str:
        """Transliterate text to the target script."""
        text = validate_non_empty(text, "transliterate_text")
        validate_text_length(text, 5000, "transliterate_text")

        result = self._request(
            "POST",
            TRANSLITERATE_URL,
            headers=self._bearer_headers(),
            json={"text": text, "target_script": target_script},
            usecase="transliterate",
            action="transliterate",
        )
        parsed = TransliterateResponse.model_validate(result)
        return parsed.transliterated_text

    # ── Language Detection ─────────────────────────────────────────

    def detect_language(self, text: str) -> LanguageDetectionResponse:
        """Detect the language of the given text."""
        text = validate_non_empty(text, "detect_text")
        validate_text_length(text, 5000, "detect_text")

        result = self._request(
            "POST",
            LANGUAGE_ID_URL,
            headers=self._subscription_headers(),
            json={"input": text},
            usecase="language_id",
            action="detect",
        )
        return LanguageDetectionResponse.model_validate(result)

    # ── Convenience: Combined Pipelines ────────────────────────────

    def translate_and_speak(
        self,
        text: str,
        target_language_code: str,
        source_language_code: str = "auto",
        *,
        speaker: str = DEFAULT_TTS_SPEAKER,
    ) -> tuple[str, list[bytes]]:
        """Translate text then synthesize speech.

        Returns (translated_text, list_of_audio_segments).
        """
        translated = self.translate(
            text, target_language_code, source_language_code
        )
        audio = self.text_to_speech(
            translated, target_language_code, speaker=speaker
        )
        return translated, audio

    def get_audit_stats(self) -> dict[str, int]:
        """Return aggregated request statistics."""
        return self._audit.get_stats()
