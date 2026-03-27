"""Mother Tongue Tutor — Streamlit Application.

Helps children learn in their home language before transitioning to Hindi/English,
using Translate + Transliterate + TTS.
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
from usecases.mother_tongue_tutor.service import TutorService

configure_logging()


def _init_state() -> None:
    for key in ("session", "messages", "last_result"):
        if key not in st.session_state:
            st.session_state[key] = None if key != "messages" else []


def main() -> None:
    st.set_page_config(page_title="Mother Tongue Tutor", page_icon="🗣️", layout="centered")
    st.title("🗣️ Mother Tongue Tutor")
    st.caption("Learn new words — starting from your home language")

    _init_state()

    settings = get_settings()
    client = SarvamClient(settings.sarvam_api_key)
    service = TutorService(client)

    # ── Sidebar ────────────────────────────────────────────────────
    with st.sidebar:
        st.header("Language Settings")
        home_lang = st.selectbox(
            "Child's Home Language",
            list(SUPPORTED_LANGUAGES.keys()),
            format_func=lambda c: SUPPORTED_LANGUAGES[c],
            index=3,  # Tamil
        )
        target_lang = st.selectbox(
            "Target Language",
            list(SUPPORTED_LANGUAGES.keys()),
            format_func=lambda c: SUPPORTED_LANGUAGES[c],
            index=1,  # Hindi
        )

        if st.button("Start Tutor Session"):
            sid = uuid.uuid4().hex[:8]
            st.session_state.session = service.create_session(sid, home_lang, target_lang)
            st.session_state.messages = []
            st.session_state.last_result = None
            st.rerun()

    if not st.session_state.session:
        st.info("👈 Select languages and click **Start Tutor Session**.")
        return

    # ── Word Teaching ──────────────────────────────────────────────
    st.subheader("Learn a New Word")
    word = st.text_input("Word or topic to learn", placeholder="e.g. apple, school, mother")
    if word and st.button("Teach Me!"):
        with st.spinner("Preparing lesson..."):
            result = service.teach_word(st.session_state.session, word)
        st.session_state.last_result = result

    if st.session_state.last_result:
        r = st.session_state.last_result
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Translation:** {r.translated_word}")
            st.markdown(f"**In your script:** {r.transliterated_word}")
        with col2:
            st.markdown("🔊 **Listen (target language):**")
            st.audio(b"".join(r.audio_target), format="audio/wav")

        st.markdown("**Explanation:**")
        st.write(r.explanation_text)
        st.markdown("🔊 **Listen (home language):**")
        st.audio(b"".join(r.audio_home), format="audio/wav")

    # ── Interactive Chat ───────────────────────────────────────────
    st.markdown("---")
    st.subheader("Chat with Tutor")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("audio"):
                st.audio(msg["audio"], format="audio/wav")

    user_input = st.chat_input("Ask your tutor anything...")
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
