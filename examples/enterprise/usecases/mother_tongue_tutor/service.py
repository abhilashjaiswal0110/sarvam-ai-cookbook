"""Language bridge tutor — helps children transition from mother tongue to Hindi/English."""

from __future__ import annotations

from dataclasses import dataclass

from core.constants import LANGUAGE_SCRIPTS, SUPPORTED_LANGUAGES
from core.models import ConversationSession
from core.sarvam_client import SarvamClient
from core.validators import sanitize_text

_SYSTEM_PROMPT = """\
You are a Mother Tongue Tutor helping children (ages 5-10) learn through their \
home language before transitioning to {target_name}.

RULES:
- The child's mother tongue is {home_name} ({home_code}).
- The target language is {target_name} ({target_code}).
- Start every explanation in the child's home language.
- Introduce new {target_name} words ONE at a time, with:
  1. The word in the home language
  2. The translation in {target_name}
  3. A fun example sentence in both languages
- Use phonetic romanization in parentheses so the child can read the new word.
- Be patient, encouraging, and celebrate every correct attempt.
- Keep responses under 120 words.
- Use topics like: greetings, family, food, animals, school.
"""


@dataclass(frozen=True)
class TutorResult:
    """Result of a tutoring interaction."""

    explanation_text: str
    translated_word: str
    transliterated_word: str
    audio_home: list[bytes]
    audio_target: list[bytes]


class TutorService:
    """Bilingual tutoring service using translate + transliterate + TTS."""

    def __init__(self, client: SarvamClient) -> None:
        self._client = client

    def create_session(
        self,
        session_id: str,
        home_language: str = "ta-IN",
        target_language: str = "hi-IN",
    ) -> ConversationSession:
        home_name = SUPPORTED_LANGUAGES.get(home_language, home_language)
        target_name = SUPPORTED_LANGUAGES.get(target_language, target_language)
        return ConversationSession(
            session_id=session_id,
            language_code=home_language,
            system_prompt=_SYSTEM_PROMPT.format(
                home_name=home_name,
                home_code=home_language,
                target_name=target_name,
                target_code=target_language,
            ),
            metadata={
                "home_language": home_language,
                "target_language": target_language,
            },
        )

    def teach_word(
        self,
        session: ConversationSession,
        word_or_topic: str,
    ) -> TutorResult:
        """Teach a word/topic using translate + transliterate + TTS pipeline."""
        word_or_topic = sanitize_text(word_or_topic)
        home_lang = session.metadata["home_language"]
        target_lang = session.metadata["target_language"]

        # Step 1: Get a teaching explanation from the chat model
        session.add_user_message(f"Teach me about: {word_or_topic}")
        explanation = self._client.chat(
            session.get_messages(),
            temperature=0.7,
            max_tokens=512,
        )
        session.add_assistant_message(explanation)

        # Step 2: Translate the key word to target language
        translated = self._client.translate(
            word_or_topic, target_lang, home_lang, mode="classic-colloquial"
        )

        # Step 3: Transliterate to help the child read in their script
        target_script = LANGUAGE_SCRIPTS.get(home_lang, "Devanagari")
        transliterated = self._client.transliterate(translated, target_script)

        # Step 4: Generate audio in both languages
        audio_home = self._client.text_to_speech(explanation, home_lang)
        audio_target = self._client.text_to_speech(translated, target_lang)

        return TutorResult(
            explanation_text=explanation,
            translated_word=translated,
            transliterated_word=transliterated,
            audio_home=audio_home,
            audio_target=audio_target,
        )

    def interactive_chat(
        self,
        session: ConversationSession,
        user_input: str,
    ) -> tuple[str, list[bytes]]:
        """Free-form chat with the tutor."""
        user_input = sanitize_text(user_input)
        session.add_user_message(user_input)

        text = self._client.chat(
            session.get_messages(),
            temperature=0.7,
            max_tokens=512,
        )
        session.add_assistant_message(text)

        home_lang = session.metadata["home_language"]
        audio = self._client.text_to_speech(text, home_lang)
        return text, audio
