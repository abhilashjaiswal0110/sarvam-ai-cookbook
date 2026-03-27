"""Rural Bank Onboarding Assistant — Streamlit Application.

Guides first-time bank account holders through KYC in their local language
with voice output.
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

# Add enterprise root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st

from core.config import get_settings
from core.constants import SUPPORTED_LANGUAGES
from core.logging_config import configure_logging
from core.sarvam_client import SarvamClient
from usecases.rural_bank_onboarding.service import OnboardingService

configure_logging()


def _init_state() -> None:
    if "session" not in st.session_state:
        st.session_state.session = None
    if "messages" not in st.session_state:
        st.session_state.messages = []


def main() -> None:
    st.set_page_config(page_title="Rural Bank Onboarding", page_icon="🏦", layout="centered")
    st.title("🏦 Rural Bank Onboarding Assistant")
    st.caption("Helping first-time bank account holders through KYC — in your language")

    _init_state()

    settings = get_settings()
    client = SarvamClient(settings.sarvam_api_key)
    service = OnboardingService(client)

    # ── Language Selection Sidebar ─────────────────────────────────
    with st.sidebar:
        st.header("Settings")
        lang = st.selectbox(
            "Preferred Language",
            options=list(SUPPORTED_LANGUAGES.keys()),
            format_func=lambda c: f"{SUPPORTED_LANGUAGES[c]} ({c})",
            index=1,  # default Hindi
        )
        if st.button("Start New Session"):
            session_id = uuid.uuid4().hex[:8]
            st.session_state.session = service.create_session(session_id, lang)
            st.session_state.messages = []
            st.rerun()

        if st.session_state.session:
            step = service.get_current_step(st.session_state.session)
            st.info(f"Current step: **{step}**")

    # ── Conversation ───────────────────────────────────────────────
    if not st.session_state.session:
        st.info("👈 Select your language and click **Start New Session** to begin.")
        return

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("audio"):
                st.audio(msg["audio"], format="audio/wav")

    user_input = st.chat_input("Type your message...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                text, audio_segments = service.process_message(
                    st.session_state.session, user_input
                )
            st.write(text)
            combined_audio = b"".join(audio_segments)
            if combined_audio:
                st.audio(combined_audio, format="audio/wav")
            st.session_state.messages.append(
                {"role": "assistant", "content": text, "audio": combined_audio}
            )


if __name__ == "__main__":
    main()
