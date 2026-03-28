"""Pydantic data models for requests, responses, and domain objects."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

# ── Enums ──────────────────────────────────────────────────────────

class SpeakerGender(StrEnum):
    MALE = "Male"
    FEMALE = "Female"


class TranslationMode(StrEnum):
    FORMAL = "formal"
    CLASSIC_COLLOQUIAL = "classic-colloquial"


class ReasoningEffort(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ── Chat ───────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str = Field(..., pattern=r"^(system|user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1, le=8192)
    reasoning_effort: ReasoningEffort | None = None
    wiki_grounding: bool = False


class ChatChoice(BaseModel):
    message: ChatMessage
    finish_reason: str | None = None


class ChatResponse(BaseModel):
    choices: list[ChatChoice]
    usage: dict[str, int] | None = None


# ── Translation ────────────────────────────────────────────────────

class TranslateRequest(BaseModel):
    text: str
    source_language_code: str = "auto"
    target_language_code: str
    mode: TranslationMode = TranslationMode.FORMAL
    speaker_gender: SpeakerGender = SpeakerGender.FEMALE
    enable_preprocessing: bool = True


class TranslateResponse(BaseModel):
    translated_text: str


# ── TTS ────────────────────────────────────────────────────────────

class TTSRequest(BaseModel):
    text: str
    target_language_code: str
    speaker: str = "meera"
    model: str = "bulbul:v2"


class TTSResponse(BaseModel):
    audios: list[str]  # base64 encoded


# ── STT ────────────────────────────────────────────────────────────

class STTResponse(BaseModel):
    transcript: str
    language_code: str | None = None


# ── Language Detection ─────────────────────────────────────────────

class LanguageDetectionResponse(BaseModel):
    language_code: str
    script_code: str | None = None
    confidence: float | None = None


# ── Transliteration ───────────────────────────────────────────────

class TransliterateRequest(BaseModel):
    text: str
    target_script: str


class TransliterateResponse(BaseModel):
    transliterated_text: str


# ── Conversation Session ──────────────────────────────────────────

class ConversationSession(BaseModel):
    """Manages a multi-turn chat session with bounded history."""

    session_id: str
    language_code: str = "en-IN"
    system_prompt: str = ""
    history: list[ChatMessage] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    max_turns: int = 20

    def add_user_message(self, content: str) -> None:
        self.history.append(ChatMessage(role="user", content=content))
        self._trim_history()

    def add_assistant_message(self, content: str) -> None:
        self.history.append(ChatMessage(role="assistant", content=content))
        self._trim_history()

    def get_messages(self) -> list[ChatMessage]:
        """Return system prompt + conversation history."""
        messages: list[ChatMessage] = []
        if self.system_prompt:
            messages.append(ChatMessage(role="system", content=self.system_prompt))
        messages.extend(self.history)
        return messages

    def _trim_history(self) -> None:
        # Keep last N turns (user+assistant pairs)
        max_messages = self.max_turns * 2
        if len(self.history) > max_messages:
            self.history = self.history[-max_messages:]
