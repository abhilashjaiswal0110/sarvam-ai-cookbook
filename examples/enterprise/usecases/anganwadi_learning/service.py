"""Early-learning content generation and narration service for Anganwadi centres."""

from __future__ import annotations

from enum import StrEnum

from core.models import ConversationSession
from core.sarvam_client import SarvamClient
from core.validators import sanitize_text


class ContentType(StrEnum):
    STORY = "story"
    RHYME = "rhyme"
    ALPHABET = "alphabet"
    NUMBERS = "numbers"
    COLOURS = "colours"
    ANIMALS = "animals"
    GOOD_HABITS = "good_habits"


_SYSTEM_PROMPT = """\
You are a warm, cheerful Anganwadi Learning Assistant for children aged 3-6.

RULES:
- Respond ONLY in {language_name} ({language_code}).
- Use extremely simple vocabulary appropriate for young children.
- Make content fun, musical, and engaging.
- Include onomatopoeia and repetition — children love patterns.
- Keep stories under 150 words. Keep rhymes under 8 lines.
- For alphabet/numbers, teach only 2-3 at a time with fun associations.
- Always include a positive moral or healthy habit where natural.
- Never include scary, violent, or inappropriate content.
- Use culturally familiar examples (local fruits, animals, festivals).

CONTENT TYPE REQUESTED: {content_type}
"""


class LearningService:
    """Generates and narrates early-learning content for Anganwadi children."""

    def __init__(self, client: SarvamClient) -> None:
        self._client = client

    def create_session(
        self,
        session_id: str,
        language_code: str = "hi-IN",
    ) -> ConversationSession:
        from core.constants import SUPPORTED_LANGUAGES

        language_name = SUPPORTED_LANGUAGES.get(language_code, "Hindi")
        return ConversationSession(
            session_id=session_id,
            language_code=language_code,
            system_prompt=_SYSTEM_PROMPT.format(
                language_name=language_name,
                language_code=language_code,
                content_type=ContentType.STORY.value,
            ),
            metadata={"content_type": ContentType.STORY.value},
        )

    def generate_content(
        self,
        session: ConversationSession,
        content_type: ContentType,
        *,
        topic: str = "",
    ) -> tuple[str, list[bytes]]:
        """Generate learning content and narrate it.

        Returns (text_content, audio_segments).
        """
        from core.constants import SUPPORTED_LANGUAGES

        language_name = SUPPORTED_LANGUAGES.get(session.language_code, "Hindi")
        session.system_prompt = _SYSTEM_PROMPT.format(
            language_name=language_name,
            language_code=session.language_code,
            content_type=content_type.value,
        )
        session.metadata["content_type"] = content_type.value

        prompt = self._build_prompt(content_type, topic)
        session.add_user_message(prompt)

        text = self._client.chat(
            session.get_messages(),
            temperature=0.8,  # creative content
            max_tokens=1024,
        )
        session.add_assistant_message(text)

        audio = self._client.text_to_speech(text, session.language_code)
        return text, audio

    def interactive_chat(
        self,
        session: ConversationSession,
        user_input: str,
    ) -> tuple[str, list[bytes]]:
        """Free-form interactive chat with the learning assistant."""
        user_input = sanitize_text(user_input)
        session.add_user_message(user_input)

        text = self._client.chat(
            session.get_messages(),
            temperature=0.7,
            max_tokens=512,
        )
        session.add_assistant_message(text)

        audio = self._client.text_to_speech(text, session.language_code)
        return text, audio

    @staticmethod
    def _build_prompt(content_type: ContentType, topic: str) -> str:
        base = {
            ContentType.STORY: "Tell a short, fun story for young children",
            ContentType.RHYME: "Sing a nursery rhyme for young children",
            ContentType.ALPHABET: "Teach a few letters of the alphabet with fun examples",
            ContentType.NUMBERS: "Teach counting with a small fun activity",
            ContentType.COLOURS: "Teach colours using everyday objects children know",
            ContentType.ANIMALS: "Tell about an animal in a fun way children will love",
            ContentType.GOOD_HABITS: "Teach a good habit through a tiny story or song",
        }
        prompt = base.get(content_type, "Tell something fun for children")
        if topic:
            prompt += f" about {sanitize_text(topic)}"
        return prompt
