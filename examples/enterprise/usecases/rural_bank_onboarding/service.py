"""KYC onboarding service — guides first-time bank account holders step by step."""

from __future__ import annotations

from enum import StrEnum

from core.models import ConversationSession
from core.sarvam_client import SarvamClient
from core.validators import sanitize_text


class KYCStep(StrEnum):
    WELCOME = "welcome"
    LANGUAGE_SELECT = "language_select"
    PERSONAL_INFO = "personal_info"
    DOCUMENT_GUIDANCE = "document_guidance"
    ACCOUNT_TYPE = "account_type"
    SUMMARY = "summary"
    COMPLETE = "complete"


# Ordered flow
_STEP_ORDER = list(KYCStep)

_SYSTEM_PROMPT = """\
You are a friendly, patient Rural Bank Onboarding Assistant helping first-time bank \
account holders in India complete their Know-Your-Customer (KYC) process.

RULES:
- Speak in the user's chosen language. Use simple, non-technical words.
- Guide the user ONE step at a time. Do not overwhelm with information.
- Current KYC step: {step}
- If the user is confused, re-explain patiently with an example.
- Never ask for or store actual Aadhaar/PAN numbers — only explain what documents are needed.
- For document guidance, list exactly which documents are accepted (Aadhaar, Voter ID, PAN, \
  Passport, Driving License) and explain where to get them if needed.
- Always end your message with a clear next-action for the user.
- Be culturally sensitive and respectful.

STEP CONTEXT:
- welcome: Greet the user warmly, explain what a bank account is and why it is useful.
- language_select: Ask which language they prefer to continue in.
- personal_info: Ask for their name and explain why the bank needs it (no actual data collection).
- document_guidance: Explain which ID documents are accepted for KYC and how to get them.
- account_type: Explain Savings vs Jan Dhan Yojana accounts in simple terms.
- summary: Summarize what they need to bring to the bank and what will happen.
- complete: Congratulate them and wish them well.
"""


class OnboardingService:
    """Manages KYC onboarding flow with voice output."""

    def __init__(self, client: SarvamClient) -> None:
        self._client = client

    def create_session(self, session_id: str, language_code: str = "hi-IN") -> ConversationSession:
        return ConversationSession(
            session_id=session_id,
            language_code=language_code,
            system_prompt=_SYSTEM_PROMPT.format(step=KYCStep.WELCOME.value),
            metadata={"current_step": KYCStep.WELCOME.value, "step_index": 0},
        )

    def process_message(
        self,
        session: ConversationSession,
        user_input: str,
    ) -> tuple[str, list[bytes]]:
        """Process user input, return (text_response, audio_segments)."""
        user_input = sanitize_text(user_input)
        session.add_user_message(user_input)

        # Advance step on confirmation-like inputs
        self._maybe_advance_step(session, user_input)

        # Update system prompt with current step
        current_step = session.metadata.get("current_step", KYCStep.WELCOME.value)
        session.system_prompt = _SYSTEM_PROMPT.format(step=current_step)

        # Get chat response
        text_response = self._client.chat(
            session.get_messages(),
            temperature=0.6,
            max_tokens=1024,
        )
        session.add_assistant_message(text_response)

        # Generate voice output
        audio = self._client.text_to_speech(
            text_response,
            session.language_code,
        )

        return text_response, audio

    def get_current_step(self, session: ConversationSession) -> str:
        return session.metadata.get("current_step", KYCStep.WELCOME.value)

    def _maybe_advance_step(
        self, session: ConversationSession, user_input: str
    ) -> None:
        """Advance to next KYC step when user signals readiness."""
        advance_signals = {"next", "continue", "ok", "yes", "haan", "aage", "theek", "agla"}
        words = set(user_input.lower().split())
        if words & advance_signals:
            idx = session.metadata.get("step_index", 0)
            if idx < len(_STEP_ORDER) - 1:
                idx += 1
                session.metadata["step_index"] = idx
                session.metadata["current_step"] = _STEP_ORDER[idx].value
