"""IT Support Helpdesk service — Chat + Translate + TTS + KB pipeline."""

from __future__ import annotations

from core.constants import SUPPORTED_LANGUAGES
from core.models import ChatMessage, ConversationSession
from core.sarvam_client import SarvamClient
from core.validators import sanitize_text
from usecases.it_support_helpdesk.knowledge_base import (
    CRITICAL_KEYWORDS,
    HIGH_KEYWORDS,
    ITKnowledgeBase,
)

_SYSTEM_PROMPT = """\
You are HelpDesk AI, an expert IT support specialist for a large enterprise.
Your role is to help employees resolve technical issues quickly and professionally.
Respond in {language_name} ({language_code}).

You have expertise in:
- Network & Connectivity: VPN, Wi-Fi, internet, DNS, proxy issues
- Hardware: laptops, printers, monitors, keyboards, USB devices
- Software & Applications: Microsoft Office, browsers, OS, drivers, installations
- Security & Access: account lockouts, password resets, MFA, phishing, permissions
- Email & Collaboration: Outlook, Microsoft Teams, Zoom, SharePoint

When a user reports an issue:
1. Acknowledge their problem with empathy
2. Identify the issue category and assess urgency
3. Provide clear, numbered, step-by-step troubleshooting instructions
4. Indicate if the issue requires escalation to human IT support
5. Suggest creating a support ticket if the issue cannot be resolved immediately

Format your response as:
**Category:** [category]
**Priority:** [Critical/High/Medium/Low]
**Steps to resolve:**
1. [step]
2. [step]
...
**Escalation needed:** [Yes/No — reason]

{knowledge_context}

Always respond in the same language the user writes in. Keep responses concise but complete."""


class ITHelpdeskService:
    """Multilingual IT Support Helpdesk with KB search, chat and TTS."""

    def __init__(self, client: SarvamClient) -> None:
        self._client = client
        self._kb = ITKnowledgeBase()

    def create_session(
        self,
        session_id: str,
        language_code: str = "en-IN",
    ) -> ConversationSession:
        language_name = SUPPORTED_LANGUAGES.get(language_code, "English")
        return ConversationSession(
            session_id=session_id,
            language_code=language_code,
            system_prompt=_SYSTEM_PROMPT.format(
                language_name=language_name,
                language_code=language_code,
                knowledge_context="",
            ),
            metadata={"category": "", "priority": ""},
        )

    def diagnose(
        self,
        session: ConversationSession,
        issue_text: str,
        *,
        reasoning_effort: str = "low",
        tts_enabled: bool = False,
    ) -> dict:
        """Diagnose an IT issue and return structured results.

        Returns a dict with keys:
            - answer: str (assistant response in user's language)
            - answer_en: str (English translation, same as answer if already English)
            - detected_lang: str (detected language code)
            - kb_hits: list[dict] (matching knowledge base articles)
            - audio: list[bytes] (TTS audio segments, empty if tts_enabled=False)
            - auto_category: str
            - auto_priority: str
        """
        issue_text = sanitize_text(issue_text)

        # 1. Detect language
        try:
            lang_resp = self._client.detect_language(issue_text)
            detected_lang = lang_resp.language_code
        except Exception:
            detected_lang = session.language_code

        # 2. Translate to English for KB search if needed
        try:
            search_text = (
                self._client.translate(issue_text, "en-IN", detected_lang)
                if detected_lang != "en-IN"
                else issue_text
            )
        except Exception:
            search_text = issue_text

        # 3. Search knowledge base
        kb_hits = self._kb.search(search_text)
        kb_context = self._kb.format_for_prompt(search_text)

        # 4. Update system prompt with KB context
        language_name = SUPPORTED_LANGUAGES.get(session.language_code, "English")
        session.system_prompt = _SYSTEM_PROMPT.format(
            language_name=language_name,
            language_code=session.language_code,
            knowledge_context=kb_context,
        )

        # 5. Chat with the model
        session.add_user_message(issue_text)
        answer = self._client.chat(
            session.get_messages(),
            temperature=0.5,
            max_tokens=1024,
        )
        session.add_assistant_message(answer)

        # 6. Translate to English for reference
        if detected_lang != "en-IN":
            try:
                answer_en = self._client.translate(answer, "en-IN", detected_lang)
            except Exception:
                answer_en = answer
        else:
            answer_en = answer

        # 7. TTS if enabled
        audio: list[bytes] = []
        if tts_enabled:
            try:
                audio = self._client.text_to_speech(
                    answer[:500], session.language_code
                )
            except Exception:
                pass

        # 8. Auto-classify
        auto_category = self._auto_category(search_text)
        auto_priority = self._auto_priority(search_text)

        return {
            "answer": answer,
            "answer_en": answer_en,
            "detected_lang": detected_lang,
            "kb_hits": kb_hits,
            "audio": audio,
            "auto_category": auto_category,
            "auto_priority": auto_priority,
        }

    @staticmethod
    def _auto_priority(text: str) -> str:
        lower = text.lower()
        if any(kw in lower for kw in CRITICAL_KEYWORDS):
            return "Critical"
        if any(kw in lower for kw in HIGH_KEYWORDS):
            return "High"
        return "Medium"

    @staticmethod
    def _auto_category(text: str) -> str:
        mapping = {
            "Network & Connectivity": [
                "vpn", "wifi", "internet", "network", "dns", "slow connection", "bandwidth",
            ],
            "Hardware": [
                "laptop", "printer", "monitor", "keyboard", "mouse", "screen", "hardware",
            ],
            "Software & Applications": [
                "office", "word", "excel", "teams", "browser", "install", "crash", "software",
            ],
            "Security & Access": [
                "password", "locked", "phishing", "mfa", "hack", "account", "permissions",
            ],
            "Email & Collaboration": [
                "email", "outlook", "teams", "zoom", "sharepoint", "calendar", "meeting",
            ],
        }
        lower = text.lower()
        for category, keywords in mapping.items():
            if any(kw in lower for kw in keywords):
                return category
        return "Other"
