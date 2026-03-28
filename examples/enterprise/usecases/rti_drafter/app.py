"""RTI Application Drafter — Streamlit Application.

Citizen speaks (or types) a grievance → system drafts a formal RTI / complaint
in official language + regional translation.
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
from usecases.rti_drafter.service import RTIDraftingService

configure_logging()


def _init_state() -> None:
    for key in ("session", "draft_result"):
        if key not in st.session_state:
            st.session_state[key] = None


def main() -> None:
    st.set_page_config(page_title="RTI Drafter", page_icon="📝", layout="wide")
    st.title("📝 RTI Application Drafter")
    st.caption("Speak or type your grievance — get a formal RTI/complaint letter")

    _init_state()

    settings = get_settings()
    client = SarvamClient(settings.sarvam_api_key)
    service = RTIDraftingService(client)

    if not st.session_state.session:
        st.session_state.session = service.create_session(uuid.uuid4().hex[:8])

    # ── Input Modes ────────────────────────────────────────────────
    tab_voice, tab_text = st.tabs(["🎤 Voice Input", "⌨️ Text Input"])

    with tab_voice:
        audio_file = st.file_uploader(
            "Upload audio of your grievance",
            type=["wav", "mp3", "ogg", "m4a"],
            key="rti_audio",
        )
        if audio_file and st.button("Draft from Voice", key="btn_voice"):
            with st.spinner("Transcribing & drafting..."):
                result = service.draft_from_audio(
                    st.session_state.session, audio_file, audio_file.name
                )
            st.session_state.draft_result = result

    with tab_text:
        language = st.selectbox(
            "Your language",
            ["auto", *list(SUPPORTED_LANGUAGES.keys())],
            format_func=lambda c: "Auto-detect" if c == "auto" else SUPPORTED_LANGUAGES.get(c, c),
        )
        grievance = st.text_area(
            "Describe your grievance",
            height=150,
            placeholder="e.g. Our village road has not been repaired for 3 years...",
        )
        if grievance and st.button("Draft from Text", key="btn_text"):
            with st.spinner("Drafting..."):
                result = service.draft_from_text(
                    st.session_state.session, grievance, language
                )
            st.session_state.draft_result = result

    # ── Display Draft ──────────────────────────────────────────────
    if st.session_state.draft_result:
        r = st.session_state.draft_result
        st.markdown("---")

        st.subheader("Transcribed Grievance")
        st.info(r.transcribed_grievance)
        lang_name = SUPPORTED_LANGUAGES.get(r.detected_language, r.detected_language)
        st.caption(f"Detected language: **{lang_name}**")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Official Draft (Hindi/English)")
            st.text_area("", r.draft_official, height=400, key="official_draft", disabled=True)

        with col2:
            st.subheader(f"Regional Translation ({lang_name})")
            st.text_area("", r.draft_regional, height=400, key="regional_draft", disabled=True)

        # ── Refine ─────────────────────────────────────────────────
        st.markdown("---")
        st.subheader("Refine the Draft")
        feedback = st.text_input("Describe changes you want", placeholder="Make it more formal...")
        if feedback and st.button("Refine"):
            with st.spinner("Refining..."):
                refined = service.refine_draft(st.session_state.session, feedback)
            st.subheader("Refined Draft")
            st.text_area("", refined, height=400, key="refined", disabled=True)


if __name__ == "__main__":
    main()
