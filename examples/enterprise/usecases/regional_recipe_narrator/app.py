"""Regional Recipe Narrator — Streamlit Application.

Food bloggers and NGOs document indigenous recipes with voice narration
in regional languages.
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
from usecases.regional_recipe_narrator.service import RecipeService

configure_logging()


def _init_state() -> None:
    for key in ("session", "recipe_result", "messages"):
        if key not in st.session_state:
            st.session_state[key] = None if key != "messages" else []


def main() -> None:
    st.set_page_config(page_title="Recipe Narrator", page_icon="🍲", layout="centered")
    st.title("🍲 Regional Recipe Narrator")
    st.caption("Document indigenous recipes with voice narration in your language")

    _init_state()

    settings = get_settings()
    client = SarvamClient(settings.sarvam_api_key)
    service = RecipeService(client)

    # ── Sidebar ────────────────────────────────────────────────────
    with st.sidebar:
        st.header("Settings")
        lang = st.selectbox(
            "Narration Language",
            list(SUPPORTED_LANGUAGES.keys()),
            format_func=lambda c: SUPPORTED_LANGUAGES[c],
            index=1,
        )
        if st.button("New Recipe"):
            sid = uuid.uuid4().hex[:8]
            st.session_state.session = service.create_session(sid, lang)
            st.session_state.recipe_result = None
            st.session_state.messages = []
            st.rerun()

    # ── Recipe Input ───────────────────────────────────────────────
    if not st.session_state.session:
        st.session_state.session = service.create_session(uuid.uuid4().hex[:8], lang)

    if not st.session_state.recipe_result:
        st.subheader("Describe Your Recipe")
        description = st.text_area(
            "Tell us about the recipe — ingredient names, cooking method, regional origin",
            height=200,
            placeholder=(
                "e.g. My grandmother's Pongal recipe from Thanjavur — "
                "uses raw rice, moong dal, black pepper, ghee..."
            ),
        )
        if description and st.button("📖 Document & Narrate"):
            with st.spinner("Writing and narrating your recipe..."):
                result = service.document_recipe(st.session_state.session, description)
            st.session_state.recipe_result = result
            st.rerun()
        return

    # ── Display Recipe ─────────────────────────────────────────────
    r = st.session_state.recipe_result
    st.subheader("Your Documented Recipe")
    st.write(r.recipe_text)

    st.markdown("🔊 **Listen to narration:**")
    st.audio(b"".join(r.audio_segments), format="audio/wav")

    # ── Follow-ups ─────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Ask Follow-ups")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("audio"):
                st.audio(msg["audio"], format="audio/wav")

    user_input = st.chat_input("Ask about the recipe...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        with st.chat_message("assistant"):
            with st.spinner("Answering..."):
                text, audio = service.ask_followup(st.session_state.session, user_input)
            st.write(text)
            combined = b"".join(audio)
            if combined:
                st.audio(combined, format="audio/wav")
            st.session_state.messages.append(
                {"role": "assistant", "content": text, "audio": combined}
            )


if __name__ == "__main__":
    main()
