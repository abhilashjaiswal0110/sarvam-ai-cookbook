"""Sarvam AI API client for the IT Support Helpdesk."""

import base64
from typing import Optional
import requests

from config import (
    SARVAM_BASE_URL,
    SARVAM_CHAT_URL,
    CHAT_MODEL,
    SYSTEM_PROMPT,
    TTS_SPEAKER,
    TTS_MODEL,
    MAX_CHAT_HISTORY,
)


class SarvamAPIError(Exception):
    """Raised when a Sarvam AI API call fails."""


class SarvamClient:
    """Client for all Sarvam AI APIs used by the helpdesk."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._sub_headers = {
            "api-subscription-key": api_key,
            "Content-Type": "application/json",
        }
        self._bearer_headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def detect_language(self, text: str) -> dict:
        """Detect the language of the given text.

        Returns a dict with 'language_code' and 'script_code'.
        """
        url = f"{SARVAM_BASE_URL}/text-lid"
        try:
            response = requests.post(
                url, headers=self._sub_headers, json={"input": text}, timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            raise SarvamAPIError(f"Language detection failed: {exc}") from exc

    def translate(
        self, text: str, source_lang: str, target_lang: str = "en-IN"
    ) -> str:
        """Translate text from source_lang to target_lang.

        Returns the translated string. If source and target are the same,
        the original text is returned unchanged.
        """
        if source_lang == target_lang:
            return text

        url = f"{SARVAM_BASE_URL}/translate"
        payload = {
            "input": text,
            "source_language_code": source_lang,
            "target_language_code": target_lang,
        }
        try:
            response = requests.post(
                url, headers=self._sub_headers, json=payload, timeout=15
            )
            response.raise_for_status()
            return response.json().get("translated_text", text)
        except requests.RequestException as exc:
            raise SarvamAPIError(f"Translation failed: {exc}") from exc

    def chat(
        self,
        messages: list,
        reasoning_effort: str = "low",
        temperature: float = 0.5,
    ) -> str:
        """Send a conversation to the sarvam-m model and return the reply.

        Args:
            messages: List of {"role": ..., "content": ...} dicts.
                The system prompt is prepended automatically if not present.
            reasoning_effort: "low" | "medium" | "high"
            temperature: Sampling temperature (0–2).

        Returns:
            The assistant's reply as a plain string.
        """
        if not messages or messages[0].get("role") != "system":
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

        # Keep history within the configured window
        system_msg = messages[0]
        history = messages[1:][-MAX_CHAT_HISTORY:]
        messages = [system_msg] + history

        payload = {
            "model": CHAT_MODEL,
            "messages": messages,
            "temperature": temperature,
            "reasoning_effort": reasoning_effort,
        }
        url = f"{SARVAM_CHAT_URL}/chat/completions"
        try:
            response = requests.post(
                url, headers=self._bearer_headers, json=payload, timeout=30
            )
            response.raise_for_status()
            try:
                data = response.json()
            except ValueError as exc:
                raise SarvamAPIError(
                    "Chat completion returned invalid JSON"
                ) from exc

            choices = data.get("choices") if isinstance(data, dict) else None
            if not isinstance(choices, list) or not choices:
                raise SarvamAPIError(
                    "Chat completion response missing non-empty 'choices' list"
                )

            message = choices[0].get("message") if isinstance(choices[0], dict) else None
            if not isinstance(message, dict):
                raise SarvamAPIError(
                    "Chat completion response missing 'message' object in first choice"
                )

            content = message.get("content")
            if not isinstance(content, str):
                raise SarvamAPIError(
                    "Chat completion response missing 'message.content' string"
                )

            return content
        except requests.RequestException as exc:
            raise SarvamAPIError(f"Chat completion failed: {exc}") from exc

    def text_to_speech(self, text: str, language: str = "en-IN") -> Optional[bytes]:
        """Convert text to speech audio.

        Returns raw audio bytes, or None if TTS fails (non-fatal).
        """
        url = f"{SARVAM_BASE_URL}/text-to-speech"
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "inputs": [text[:500]],  # API limit per call
            "target_language_code": language,
            "speaker": TTS_SPEAKER,
            "model": TTS_MODEL,
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            response.raise_for_status()
            audios = response.json().get("audios", [])
            if audios:
                return base64.b64decode(audios[0])
        except (requests.RequestException, Exception):
            return None
        return None

    def speech_to_text(
        self, audio_bytes: bytes, language: str = "unknown", filename: str = "audio.wav"
    ) -> str:
        """Transcribe audio bytes to text.

        Returns the transcript string (possibly empty if the response has no
        transcript). Raises SarvamAPIError on request or HTTP failures.
        """
        url = f"{SARVAM_BASE_URL}/speech-to-text"
        headers = {"api-subscription-key": self.api_key}
        files = {"file": (filename, audio_bytes, "audio/wav")}
        data = {}
        if language != "unknown":
            data["language_code"] = language

        try:
            response = requests.post(
                url, headers=headers, files=files, data=data, timeout=30
            )
            response.raise_for_status()
            return response.json().get("transcript", "")
        except requests.RequestException as exc:
            raise SarvamAPIError(f"Speech-to-text failed: {exc}") from exc

    def analyze_sentiment(self, text: str) -> str:
        """Analyze the urgency level of an English IT support request.

        Returns one of "critical", "high", "medium", or "low".
        Defaults to "medium" if the service does not provide an answer or on failure.
        """
        import json

        url = f"{SARVAM_BASE_URL}/text-analytics"
        questions = [
            {
                "id": "sentiment",
                "text": "What is the overall sentiment or urgency of this IT support request?",
                "type": "enum",
                "properties": {"options": ["critical", "high", "medium", "low"]},
            }
        ]
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"text": text, "questions": json.dumps(questions)}
        try:
            response = requests.post(url, headers=headers, data=data, timeout=15)
            response.raise_for_status()
            answers = response.json().get("answers", [])
            if answers:
                return answers[0].get("response", "medium")
        except requests.RequestException:
            return "medium"
        return "medium"
