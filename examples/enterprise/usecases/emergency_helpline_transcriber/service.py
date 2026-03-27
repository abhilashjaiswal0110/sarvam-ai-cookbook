"""Emergency helpline transcription and call analytics service — STT + Chat analytics."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import IO

from core.constants import SUPPORTED_LANGUAGES
from core.models import ChatMessage
from core.sarvam_client import SarvamClient
from core.validators import sanitize_text


class EmergencyType(str, Enum):
    FIRE = "fire"
    MEDICAL = "medical"
    POLICE = "police"
    DISASTER = "disaster"
    UNKNOWN = "unknown"


class UrgencyLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class CallAnalysis:
    """Structured analysis of an emergency distress call."""

    transcript: str
    detected_language: str
    english_translation: str
    emergency_type: str
    urgency_level: str
    location_mentioned: str
    key_details: list[str]
    recommended_action: str
    caller_emotional_state: str


_ANALYSIS_PROMPT = """\
You are an Emergency Call Analyst for an Indian emergency helpline (112/100/101/108).

Analyze the following transcribed distress call and extract structured information \
for the dispatch team.

RULES:
- Be extremely precise — lives may depend on this analysis.
- Extract ALL location clues (landmarks, area names, pin codes).
- Classify the emergency type: fire, medical, police, disaster, or unknown.
- Assess urgency: critical (immediate life threat), high, medium, low.
- Identify the caller's emotional state to help dispatchers prepare.
- List key details the dispatch team needs (number of people, injuries, etc.).
- Recommend a specific action (which service to dispatch).
- Respond in structured English for the dispatch dashboard.

TRANSCRIBED CALL:
Language: {language}
Transcript: {transcript}

Respond in this EXACT format:
EMERGENCY_TYPE: [fire/medical/police/disaster/unknown]
URGENCY: [critical/high/medium/low]
LOCATION: [any location details mentioned]
KEY_DETAILS:
- [detail 1]
- [detail 2]
RECOMMENDED_ACTION: [what to dispatch]
CALLER_STATE: [emotional state assessment]
SUMMARY: [one-line summary for dispatch screen]
"""


class TranscriptionService:
    """Transcribes and analyzes emergency distress calls."""

    def __init__(self, client: SarvamClient) -> None:
        self._client = client

    def transcribe_call(
        self,
        audio_file: IO[bytes],
        filename: str,
    ) -> str:
        """Transcribe an audio file and return raw transcript."""
        result = self._client.speech_to_text(audio_file, filename, "unknown")
        return result.transcript

    def analyze_call(
        self,
        audio_file: IO[bytes],
        filename: str,
    ) -> CallAnalysis:
        """Full pipeline: transcribe → detect language → translate → analyze."""
        # Step 1: Transcribe
        stt_result = self._client.speech_to_text(audio_file, filename, "unknown")
        transcript = stt_result.transcript
        detected_lang = stt_result.language_code or "unknown"

        # Step 2: Translate to English for analysis
        if detected_lang and detected_lang != "en-IN":
            english_translation = self._client.translate(
                transcript, "en-IN", detected_lang
            )
        else:
            english_translation = transcript

        # Step 3: Analyze with Chat LLM
        language_name = SUPPORTED_LANGUAGES.get(detected_lang, detected_lang)
        analysis_text = self._client.chat(
            [
                ChatMessage(role="system", content="You are an emergency call analyst."),
                ChatMessage(
                    role="user",
                    content=_ANALYSIS_PROMPT.format(
                        language=language_name,
                        transcript=english_translation,
                    ),
                ),
            ],
            temperature=0.2,  # very low for precision
            max_tokens=1024,
        )

        # Step 4: Parse structured response
        return self._parse_analysis(
            transcript, detected_lang, english_translation, analysis_text
        )

    def analyze_text_call(self, transcript: str) -> CallAnalysis:
        """Analyze from text transcript directly (for testing/batch processing)."""
        transcript = sanitize_text(transcript)
        detected = self._client.detect_language(transcript)
        detected_lang = detected.language_code

        if detected_lang != "en-IN":
            english_translation = self._client.translate(
                transcript, "en-IN", detected_lang
            )
        else:
            english_translation = transcript

        language_name = SUPPORTED_LANGUAGES.get(detected_lang, detected_lang)
        analysis_text = self._client.chat(
            [
                ChatMessage(role="system", content="You are an emergency call analyst."),
                ChatMessage(
                    role="user",
                    content=_ANALYSIS_PROMPT.format(
                        language=language_name,
                        transcript=english_translation,
                    ),
                ),
            ],
            temperature=0.2,
            max_tokens=1024,
        )

        return self._parse_analysis(
            transcript, detected_lang, english_translation, analysis_text
        )

    @staticmethod
    def _parse_analysis(
        transcript: str,
        detected_lang: str,
        english_translation: str,
        analysis_text: str,
    ) -> CallAnalysis:
        """Parse the structured LLM output into a CallAnalysis object."""

        def _extract(label: str, text: str) -> str:
            for line in text.split("\n"):
                if line.strip().upper().startswith(label.upper()):
                    return line.split(":", 1)[-1].strip()
            return "unknown"

        def _extract_list(label: str, text: str) -> list[str]:
            items: list[str] = []
            in_section = False
            for line in text.split("\n"):
                if line.strip().upper().startswith(label.upper()):
                    in_section = True
                    continue
                if in_section:
                    stripped = line.strip()
                    if stripped.startswith("- "):
                        items.append(stripped[2:])
                    elif stripped and not stripped.endswith(":"):
                        break
            return items or ["No details extracted"]

        return CallAnalysis(
            transcript=transcript,
            detected_language=detected_lang,
            english_translation=english_translation,
            emergency_type=_extract("EMERGENCY_TYPE", analysis_text),
            urgency_level=_extract("URGENCY", analysis_text),
            location_mentioned=_extract("LOCATION", analysis_text),
            key_details=_extract_list("KEY_DETAILS", analysis_text),
            recommended_action=_extract("RECOMMENDED_ACTION", analysis_text),
            caller_emotional_state=_extract("CALLER_STATE", analysis_text),
        )
