"""Alert broadcasting service — Translate → TTS pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from core.constants import SUPPORTED_LANGUAGES
from core.sarvam_client import SarvamClient
from core.validators import sanitize_text, validate_non_empty


@dataclass(frozen=True)
class BroadcastResult:
    """A single language broadcast."""

    language_code: str
    language_name: str
    translated_alert: str
    audio_segments: list[bytes]


@dataclass(frozen=True)
class MultiBroadcastResult:
    """Results from broadcasting to multiple languages."""

    original_alert: str
    source_language: str
    broadcasts: list[BroadcastResult]
    failed_languages: list[str]


class BroadcastService:
    """Converts official alerts into multi-language voice broadcasts."""

    def __init__(self, client: SarvamClient) -> None:
        self._client = client

    def broadcast_alert(
        self,
        alert_text: str,
        source_language: str,
        target_languages: list[str],
        *,
        speaker: str = "meera",
    ) -> MultiBroadcastResult:
        """Translate an official alert into multiple languages and generate audio.

        Args:
            alert_text: The official alert text.
            source_language: Source language code (e.g. "en-IN").
            target_languages: List of target language codes.
            speaker: TTS speaker voice.

        Returns:
            MultiBroadcastResult with translations and audio for each language.
        """
        alert_text = validate_non_empty(sanitize_text(alert_text), "alert_text")

        broadcasts: list[BroadcastResult] = []
        failed: list[str] = []

        for lang_code in target_languages:
            try:
                lang_name = SUPPORTED_LANGUAGES.get(lang_code, lang_code)

                # Translate (skip if same as source)
                if lang_code == source_language:
                    translated = alert_text
                else:
                    translated = self._client.translate(
                        alert_text, lang_code, source_language, mode="formal"
                    )

                # Generate speech
                audio = self._client.text_to_speech(
                    translated, lang_code, speaker=speaker
                )

                broadcasts.append(
                    BroadcastResult(
                        language_code=lang_code,
                        language_name=lang_name,
                        translated_alert=translated,
                        audio_segments=audio,
                    )
                )
            except Exception:
                failed.append(lang_code)

        return MultiBroadcastResult(
            original_alert=alert_text,
            source_language=source_language,
            broadcasts=broadcasts,
            failed_languages=failed,
        )

    def broadcast_to_all(
        self,
        alert_text: str,
        source_language: str = "en-IN",
    ) -> MultiBroadcastResult:
        """Broadcast to ALL supported languages."""
        all_langs = list(SUPPORTED_LANGUAGES.keys())
        return self.broadcast_alert(alert_text, source_language, all_langs)
