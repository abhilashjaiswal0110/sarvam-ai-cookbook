"""Legal advisory service — Chat + Translate + TTS pipeline."""

from __future__ import annotations

from core.constants import SUPPORTED_LANGUAGES
from core.models import ChatMessage, ConversationSession
from core.sarvam_client import SarvamClient
from core.validators import sanitize_text
from usecases.legal_aid_bot.knowledge_base import format_topic_for_prompt


_SYSTEM_PROMPT = """\
You are a Legal Aid Assistant for Indian citizens. You explain legal rights in \
plain, simple {language_name}.

RULES:
- Speak in {language_name} ({language_code}).
- Use extremely simple language — assume the user has no legal background.
- Explain one concept at a time with a real-life example.
- Always mention the relevant helpline number if applicable.
- NEVER give specific legal advice — always recommend consulting a lawyer for their case.
- Include a disclaimer: "This is general information, not legal advice."
- Be empathetic and supportive.

KNOWLEDGE BASE CONTEXT:
{knowledge_context}
"""


class LegalAidService:
    """Explains legal rights in regional languages with voice output."""

    def __init__(self, client: SarvamClient) -> None:
        self._client = client

    def create_session(
        self,
        session_id: str,
        language_code: str = "hi-IN",
        topic_key: str = "",
    ) -> ConversationSession:
        language_name = SUPPORTED_LANGUAGES.get(language_code, "Hindi")
        knowledge = format_topic_for_prompt(topic_key) if topic_key else ""
        return ConversationSession(
            session_id=session_id,
            language_code=language_code,
            system_prompt=_SYSTEM_PROMPT.format(
                language_name=language_name,
                language_code=language_code,
                knowledge_context=knowledge or "No specific topic selected yet.",
            ),
            metadata={"topic": topic_key},
        )

    def set_topic(self, session: ConversationSession, topic_key: str) -> None:
        """Switch the knowledge base topic."""
        language_name = SUPPORTED_LANGUAGES.get(session.language_code, "Hindi")
        knowledge = format_topic_for_prompt(topic_key)
        session.system_prompt = _SYSTEM_PROMPT.format(
            language_name=language_name,
            language_code=session.language_code,
            knowledge_context=knowledge or "General legal guidance.",
        )
        session.metadata["topic"] = topic_key

    def ask(
        self,
        session: ConversationSession,
        question: str,
    ) -> tuple[str, str, list[bytes]]:
        """Answer a legal question.

        Returns (answer_in_regional, answer_in_english, audio_segments).
        """
        question = sanitize_text(question)
        session.add_user_message(question)

        # Get answer in user's language
        answer = self._client.chat(
            session.get_messages(),
            temperature=0.5,
            max_tokens=1024,
            wiki_grounding=True,
        )
        session.add_assistant_message(answer)

        # Translate to English for reference (if not already English)
        if session.language_code != "en-IN":
            answer_en = self._client.translate(answer, "en-IN", session.language_code)
        else:
            answer_en = answer

        # Generate voice in user's language
        audio = self._client.text_to_speech(answer, session.language_code)

        return answer, answer_en, audio
