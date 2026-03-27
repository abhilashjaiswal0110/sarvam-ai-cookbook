"""Recipe documentation and narration service — Chat + TTS pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from core.constants import SUPPORTED_LANGUAGES
from core.models import ChatMessage, ConversationSession
from core.sarvam_client import SarvamClient
from core.validators import sanitize_text


_SYSTEM_PROMPT = """\
You are a Regional Recipe Documentation Assistant. You help food bloggers, \
NGOs, and home cooks document indigenous Indian recipes with rich detail.

RULES:
- Respond in {language_name} ({language_code}).
- Structure every recipe with:
  1. Recipe name (in regional language + English transliteration)
  2. Region / community of origin
  3. Ingredients list with local names and approximate measurements
  4. Step-by-step cooking instructions (numbered, clear)
  5. Serving suggestions and traditional context
  6. Any cultural significance or festival association
- Use warm, storytelling language — these are heritage recipes.
- If the user gives a vague description, ask clarifying questions about ingredients or method.
- Mention traditional utensils / techniques where relevant.
- Keep the total recipe under 350 words.
"""


@dataclass(frozen=True)
class RecipeResult:
    """A documented recipe with narration."""

    recipe_text: str
    audio_segments: list[bytes]


class RecipeService:
    """Documents and narrates regional recipes."""

    def __init__(self, client: SarvamClient) -> None:
        self._client = client

    def create_session(
        self,
        session_id: str,
        language_code: str = "hi-IN",
    ) -> ConversationSession:
        language_name = SUPPORTED_LANGUAGES.get(language_code, "Hindi")
        return ConversationSession(
            session_id=session_id,
            language_code=language_code,
            system_prompt=_SYSTEM_PROMPT.format(
                language_name=language_name,
                language_code=language_code,
            ),
        )

    def document_recipe(
        self,
        session: ConversationSession,
        description: str,
    ) -> RecipeResult:
        """Generate a structured recipe from a user's description + narrate it."""
        description = sanitize_text(description)
        session.add_user_message(
            f"Please document this recipe in full detail:\n{description}"
        )

        recipe_text = self._client.chat(
            session.get_messages(),
            temperature=0.7,
            max_tokens=2048,
        )
        session.add_assistant_message(recipe_text)

        audio = self._client.text_to_speech(recipe_text, session.language_code)
        return RecipeResult(recipe_text=recipe_text, audio_segments=audio)

    def ask_followup(
        self,
        session: ConversationSession,
        question: str,
    ) -> tuple[str, list[bytes]]:
        """Handle follow-up questions about the recipe."""
        question = sanitize_text(question)
        session.add_user_message(question)

        answer = self._client.chat(
            session.get_messages(),
            temperature=0.6,
            max_tokens=512,
        )
        session.add_assistant_message(answer)

        audio = self._client.text_to_speech(answer, session.language_code)
        return answer, audio
