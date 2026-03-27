"""Legal Aid Bot — Streamlit Application.

Explains FIR filing, land rights, consumer rights, and more in plain
regional language with voice output.
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st

from core.config import get_settings
from core.constants import SUPPORTED_LANGUAGES
from core.logging_config import configure_logging
from core.sarvam_client import SarvamClient
from usecases.legal_aid_bot.knowledge_base import LEGAL_TOPICS, get_topic_names
from usecases.legal_aid_bot.service import LegalAidService

configure_logging()


def _init_state() -> None:
    for key in ("session", "messages"):
        if key not in st.session_state:
            st.session_state[key] = None if key != "messages" else []


def main() -> None:
    st.set_page_config(page_title="Legal Aid Bot", page_icon="⚖️", layout="wide")
    st.title("⚖️ Legal Aid Bot")
    st.caption("Understand your legal rights — in your language, in plain words")

    _init_state()

    settings = get_settings()
    client = SarvamClient(settings.sarvam_api_key)
    service = LegalAidService(client)

    # ── Sidebar ────────────────────────────────────────────────────
    with st.sidebar:
        st.header("Settings")
        lang = st.selectbox(
            "Your Language",
            list(SUPPORTED_LANGUAGES.keys()),
            format_func=lambda c: SUPPORTED_LANGUAGES[c],
            index=1,
        )
        topic = st.selectbox(
            "Legal Topic",
            [""] + get_topic_names(),
            format_func=lambda t: LEGAL_TOPICS[t]["title"] if t else "General / Ask anything",
        )

        if st.button("Start Session"):
            sid = uuid.uuid4().hex[:8]
            st.session_state.session = service.create_session(sid, lang, topic)
            st.session_state.messages = []
            st.rerun()

        if st.session_state.session and topic:
            if topic != st.session_state.session.metadata.get("topic"):
                service.set_topic(st.session_state.session, topic)

        st.markdown("---")
        st.warning(
            "**Disclaimer:** This provides general legal information, not professional "
            "legal advice. Consult a qualified lawyer for your specific situation."
        )

    if not st.session_state.session:
        st.info("👈 Select your language and topic, then click **Start Session**.")

        # Show available topics
        st.subheader("Available Topics")
        for key, info in LEGAL_TOPICS.items():
            with st.expander(info["title"]):
                st.write(info["summary"])
        return

    # ── Conversation ───────────────────────────────────────────────
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("english"):
                with st.expander("English translation"):
                    st.write(msg["english"])
            if msg.get("audio"):
                st.audio(msg["audio"], format="audio/wav")

    user_input = st.chat_input("Ask your legal question...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Researching..."):
                answer, answer_en, audio = service.ask(
                    st.session_state.session, user_input
                )
            st.write(answer)
            with st.expander("English translation"):
                st.write(answer_en)
            combined = b"".join(audio)
            if combined:
                st.audio(combined, format="audio/wav")
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "english": answer_en,
                    "audio": combined,
                }
            )


if __name__ == "__main__":
    main()
