"""Anganwadi Learning Assistant — Streamlit Application.

Stories, rhymes, and early learning content narrated in local languages
for children aged 3-6 at Anganwadi centres.
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
from usecases.anganwadi_learning.service import ContentType, LearningService

configure_logging()


def _init_state() -> None:
    if "session" not in st.session_state:
        st.session_state.session = None
    if "messages" not in st.session_state:
        st.session_state.messages = []


def main() -> None:
    st.set_page_config(page_title="Anganwadi Learning", page_icon="📚", layout="centered")
    st.title("📚 Anganwadi Learning Assistant")
    st.caption("Stories, rhymes & fun learning in your child's mother tongue")

    _init_state()

    settings = get_settings()
    client = SarvamClient(settings.sarvam_api_key)
    service = LearningService(client)

    # ── Sidebar ────────────────────────────────────────────────────
    with st.sidebar:
        st.header("Settings")
        lang = st.selectbox(
            "Language",
            list(SUPPORTED_LANGUAGES.keys()),
            format_func=lambda c: f"{SUPPORTED_LANGUAGES[c]} ({c})",
            index=1,
        )
        content_type = st.selectbox(
            "Content Type",
            [ct.value for ct in ContentType],
            format_func=lambda v: v.replace("_", " ").title(),
        )
        topic = st.text_input("Topic (optional)", placeholder="e.g. elephants, mangoes")

        if st.button("🎨 Generate Content"):
            session_id = uuid.uuid4().hex[:8]
            st.session_state.session = service.create_session(session_id, lang)
            st.session_state.messages = []

            with st.spinner("Creating something fun..."):
                text, audio = service.generate_content(
                    st.session_state.session,
                    ContentType(content_type),
                    topic=topic,
                )
            st.session_state.messages.append(
                {"role": "assistant", "content": text, "audio": b"".join(audio)}
            )
            st.rerun()

        if st.button("Start Fresh"):
            st.session_state.session = None
            st.session_state.messages = []
            st.rerun()

    # ── Content Display ────────────────────────────────────────────
    if not st.session_state.messages:
        st.info("👈 Choose a language and content type, then click **Generate Content**!")
        return

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("audio"):
                st.audio(msg["audio"], format="audio/wav")

    # ── Interactive follow-up ──────────────────────────────────────
    if st.session_state.session:
        user_input = st.chat_input("Ask for more or say something...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    text, audio = service.interactive_chat(
                        st.session_state.session, user_input
                    )
                st.write(text)
                combined = b"".join(audio)
                if combined:
                    st.audio(combined, format="audio/wav")
                st.session_state.messages.append(
                    {"role": "assistant", "content": text, "audio": combined}
                )


if __name__ == "__main__":
    main()
