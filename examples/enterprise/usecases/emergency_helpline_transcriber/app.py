"""Emergency Helpline Transcriber — Streamlit Application.

Transcribes distress calls in real time and provides structured analysis
for faster dispatch.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st

from core.config import get_settings
from core.logging_config import configure_logging
from core.sarvam_client import SarvamClient
from usecases.emergency_helpline_transcriber.service import TranscriptionService

configure_logging()


def _urgency_color(level: str) -> str:
    return {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢",
    }.get(level.lower(), "⚪")


def main() -> None:
    st.set_page_config(
        page_title="Emergency Helpline Transcriber",
        page_icon="🚨",
        layout="wide",
    )
    st.title("🚨 Emergency Helpline Transcriber")
    st.caption("Transcribe and analyze distress calls for faster dispatch")

    settings = get_settings()
    client = SarvamClient(settings.sarvam_api_key)
    service = TranscriptionService(client)

    # ── Input ──────────────────────────────────────────────────────
    tab_audio, tab_text = st.tabs(["🎤 Audio Upload", "📝 Text Transcript"])

    analysis = None

    with tab_audio:
        audio_file = st.file_uploader(
            "Upload distress call recording",
            type=["wav", "mp3", "ogg", "m4a"],
        )
        if audio_file and st.button("Transcribe & Analyze", key="btn_audio"):
            with st.spinner("Transcribing and analyzing..."):
                analysis = service.analyze_call(audio_file, audio_file.name)

    with tab_text:
        transcript_text = st.text_area(
            "Paste call transcript",
            height=150,
            placeholder="e.g. 'मेरे घर में आग लग गई है, कृपया जल्दी आइए...'",
        )
        if transcript_text and st.button("Analyze Transcript", key="btn_text"):
            with st.spinner("Analyzing..."):
                analysis = service.analyze_text_call(transcript_text)

    # ── Dispatch Dashboard ─────────────────────────────────────────
    if analysis:
        st.markdown("---")
        st.header("📋 Dispatch Dashboard")

        # Urgency banner
        urg = analysis.urgency_level
        st.markdown(
            f"### {_urgency_color(urg)} Urgency: **{urg.upper()}** | "
            f"Type: **{analysis.emergency_type.upper()}**"
        )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Call Details")
            st.markdown(f"**Language:** {analysis.detected_language}")
            st.markdown("**Original Transcript:**")
            st.text_area("", analysis.transcript, height=120, disabled=True, key="orig")

            st.markdown("**English Translation:**")
            st.text_area("", analysis.english_translation, height=120, disabled=True, key="en")

        with col2:
            st.subheader("Analysis")
            st.markdown(f"📍 **Location:** {analysis.location_mentioned}")
            st.markdown(f"🧠 **Caller State:** {analysis.caller_emotional_state}")

            st.markdown("**Key Details:**")
            for detail in analysis.key_details:
                st.markdown(f"  - {detail}")

            st.markdown(f"🚑 **Recommended Action:** {analysis.recommended_action}")

        st.markdown("---")
        st.warning(
            "This analysis is AI-generated and should be verified by a trained dispatcher. "
            "Always follow standard emergency protocols."
        )


if __name__ == "__main__":
    main()
