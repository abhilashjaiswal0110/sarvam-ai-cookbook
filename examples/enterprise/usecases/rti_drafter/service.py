"""RTI / grievance drafting service — STT → Chat → Translate pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import IO

from core.constants import SUPPORTED_LANGUAGES
from core.models import ChatMessage, ConversationSession
from core.sarvam_client import SarvamClient
from core.validators import sanitize_text


_DRAFTER_PROMPT = """\
You are an expert RTI (Right to Information) and formal complaint drafter for Indian citizens.

RULES:
- The citizen has described their grievance in {language_name}.
- Draft a FORMAL RTI application or complaint letter that is legally appropriate.
- Structure:
  1. Subject line (clear, specific)
  2. To: [Public Authority / Department]
  3. From: [Applicant — use placeholder "___" for name/address]
  4. Date: [Today's date placeholder]
  5. Body: State the information sought or grievance clearly, citing the \
     RTI Act, 2005 (Section 6) where applicable.
  6. Closing: Polite, firm request with deadline mention.
- Use formal Hindi or English as the output language.
- Keep the draft under 300 words.
- Do NOT include any actual personal data of the user.
- If the grievance is unclear, ask ONE clarifying question.

GRIEVANCE (transcribed from voice):
{grievance}
"""

_REFINE_PROMPT = """\
The citizen wants to refine the RTI draft. Apply the following feedback \
while keeping the letter formal and legally sound:
{feedback}
"""


@dataclass(frozen=True)
class DraftResult:
    """Result of the RTI drafting pipeline."""

    transcribed_grievance: str
    detected_language: str
    draft_official: str          # in Hindi/English
    draft_regional: str          # translated back to user's language


class RTIDraftingService:
    """Voice-to-formal-document pipeline: STT → Chat → Translate."""

    def __init__(self, client: SarvamClient) -> None:
        self._client = client

    def create_session(self, session_id: str) -> ConversationSession:
        return ConversationSession(
            session_id=session_id,
            language_code="hi-IN",
            system_prompt="",
            metadata={"stage": "awaiting_input"},
        )

    def draft_from_audio(
        self,
        session: ConversationSession,
        audio_file: IO[bytes],
        filename: str,
    ) -> DraftResult:
        """Full pipeline: transcribe → draft → translate."""
        # Step 1: Speech-to-Text
        stt_result = self._client.speech_to_text(audio_file, filename)
        grievance = stt_result.transcript
        detected_lang = stt_result.language_code or "hi-IN"
        session.language_code = detected_lang

        return self._generate_draft(session, grievance, detected_lang)

    def draft_from_text(
        self,
        session: ConversationSession,
        grievance_text: str,
        language_code: str = "auto",
    ) -> DraftResult:
        """Draft from typed text instead of audio."""
        grievance_text = sanitize_text(grievance_text)

        if language_code == "auto":
            detected = self._client.detect_language(grievance_text)
            detected_lang = detected.language_code
        else:
            detected_lang = language_code

        session.language_code = detected_lang
        return self._generate_draft(session, grievance_text, detected_lang)

    def refine_draft(
        self,
        session: ConversationSession,
        feedback: str,
    ) -> str:
        """Refine the existing draft based on user feedback."""
        feedback = sanitize_text(feedback)
        session.add_user_message(
            _REFINE_PROMPT.format(feedback=feedback)
        )
        refined = self._client.chat(
            session.get_messages(),
            temperature=0.4,
            max_tokens=2048,
        )
        session.add_assistant_message(refined)
        return refined

    def _generate_draft(
        self,
        session: ConversationSession,
        grievance: str,
        detected_lang: str,
    ) -> DraftResult:
        language_name = SUPPORTED_LANGUAGES.get(detected_lang, "Hindi")

        # Step 2: Generate formal draft via Chat
        session.system_prompt = _DRAFTER_PROMPT.format(
            language_name=language_name, grievance=grievance
        )
        session.add_user_message(grievance)

        draft_official = self._client.chat(
            session.get_messages(),
            temperature=0.3,  # low creativity for formal documents
            max_tokens=2048,
        )
        session.add_assistant_message(draft_official)
        session.metadata["stage"] = "draft_ready"

        # Step 3: Translate to user's regional language
        if detected_lang in ("en-IN", "hi-IN"):
            draft_regional = draft_official
        else:
            draft_regional = self._client.translate(
                draft_official, detected_lang, "hi-IN", mode="formal"
            )

        return DraftResult(
            transcribed_grievance=grievance,
            detected_language=detected_lang,
            draft_official=draft_official,
            draft_regional=draft_regional,
        )
