"""Flood/Cyclone Alert Broadcaster — Streamlit Application.

Converts official disaster alerts into local language voice broadcasts
for rapid dissemination.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st

from core.config import get_settings
from core.constants import SUPPORTED_LANGUAGES
from core.logging_config import configure_logging
from core.sarvam_client import SarvamClient
from usecases.flood_cyclone_broadcaster.service import BroadcastService

configure_logging()

# Sample alerts for quick testing
_SAMPLE_ALERTS = {
    "Cyclone Warning": (
        "CYCLONE WARNING: Severe cyclonic storm expected to cross the coast of Odisha "
        "near Puri between 6 PM and 9 PM today. Wind speed 120-140 km/h with heavy "
        "rainfall. All residents within 5 km of the coastline must evacuate immediately "
        "to nearest cyclone shelters. Fishing is strictly prohibited. Emergency helpline: 1070."
    ),
    "Flood Alert": (
        "FLOOD ALERT: River Brahmaputra has crossed danger level at Dibrugarh. Water level "
        "is 1.2 metres above danger mark and rising. Low-lying areas in Dibrugarh and "
        "Dhemaji districts may be inundated within 12 hours. Residents are advised to move "
        "to higher ground. NDRF teams deployed. Emergency helpline: 1070."
    ),
    "Earthquake Advisory": (
        "EARTHQUAKE ADVISORY: An earthquake of magnitude 5.2 was recorded at 3:45 AM today "
        "with epicentre 40 km south of Dharamshala, Himachal Pradesh. Aftershocks possible. "
        "Do not re-enter damaged buildings. If indoors, take cover under sturdy furniture. "
        "Emergency helpline: 112."
    ),
}


def main() -> None:
    st.set_page_config(
        page_title="Alert Broadcaster",
        page_icon="🌊",
        layout="wide",
    )
    st.title("🌊 Flood/Cyclone Alert Broadcaster")
    st.caption("Official alerts → Translated voice broadcasts in all Indian languages")

    settings = get_settings()
    client = SarvamClient(settings.sarvam_api_key)
    service = BroadcastService(client)

    # ── Input ──────────────────────────────────────────────────────
    col_input, col_config = st.columns([2, 1])

    with col_config:
        st.subheader("Configuration")
        source_lang = st.selectbox(
            "Alert Language",
            list(SUPPORTED_LANGUAGES.keys()),
            format_func=lambda c: SUPPORTED_LANGUAGES[c],
            index=0,  # English
        )
        selected_targets = st.multiselect(
            "Broadcast to languages",
            list(SUPPORTED_LANGUAGES.keys()),
            default=["hi-IN", "bn-IN", "ta-IN", "te-IN", "od-IN"],
            format_func=lambda c: SUPPORTED_LANGUAGES[c],
        )
        broadcast_all = st.checkbox("Broadcast to ALL languages")

    with col_input:
        st.subheader("Alert Text")
        # Quick-fill from samples
        sample = st.selectbox(
            "Use sample alert",
            ["Custom"] + list(_SAMPLE_ALERTS.keys()),
        )
        if sample != "Custom":
            default_text = _SAMPLE_ALERTS[sample]
        else:
            default_text = ""

        alert_text = st.text_area(
            "Official alert message",
            value=default_text,
            height=200,
            placeholder="Enter the official disaster alert...",
        )

    # ── Broadcast ──────────────────────────────────────────────────
    if alert_text and st.button("📡 Broadcast Alert", type="primary"):
        targets = list(SUPPORTED_LANGUAGES.keys()) if broadcast_all else selected_targets

        if not targets:
            st.error("Select at least one target language.")
            return

        progress = st.progress(0, text="Broadcasting...")
        with st.spinner(f"Translating and generating audio for {len(targets)} languages..."):
            result = service.broadcast_alert(alert_text, source_lang, targets)
        progress.empty()

        # ── Results ────────────────────────────────────────────────
        st.markdown("---")
        st.header(f"📡 Broadcast Results — {len(result.broadcasts)} languages")

        if result.failed_languages:
            st.error(f"Failed for: {', '.join(result.failed_languages)}")

        for bc in result.broadcasts:
            with st.expander(f"🔊 {bc.language_name} ({bc.language_code})", expanded=False):
                st.write(bc.translated_alert)
                combined = b"".join(bc.audio_segments)
                if combined:
                    st.audio(combined, format="audio/wav")


if __name__ == "__main__":
    main()
