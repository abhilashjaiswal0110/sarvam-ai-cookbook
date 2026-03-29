"""IT Support Helpdesk — Streamlit Application.

Multilingual IT support with AI diagnostics, knowledge base, ticket management,
and voice input/output — built on the Sarvam Enterprise framework.
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

# Ensure enterprise root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st

from core.config import get_settings
from core.constants import SUPPORTED_LANGUAGES
from core.logging_config import configure_logging
from core.sarvam_client import SarvamClient
from usecases.it_support_helpdesk.knowledge_base import (
    ISSUE_CATEGORIES,
    PRIORITY_LEVELS,
    TICKET_STATUSES,
)
from usecases.it_support_helpdesk.service import ITHelpdeskService
from usecases.it_support_helpdesk.ticket_manager import TicketManager

configure_logging()

# ── Page config ─────────────────────────────────────────────────────────────

st.set_page_config(page_title="IT Support Helpdesk", page_icon="🖥️", layout="wide")

# ── Session state defaults ───────────────────────────────────────────────────

_DEFAULTS = {
    "session": None,
    "chat_history": [],
    "language": "en-IN",
    "user_name": "Employee",
    "pending_ticket": None,
    "last_response": "",
}
for key, val in _DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🖥️ IT Helpdesk")
    st.markdown("---")

    settings = get_settings()

    st.session_state.user_name = st.text_input(
        "Your Name", value=st.session_state.user_name
    )

    lang_display = {v: k for k, v in SUPPORTED_LANGUAGES.items()}
    selected_lang_name = st.selectbox(
        "Preferred Language",
        options=list(SUPPORTED_LANGUAGES.values()),
        index=list(SUPPORTED_LANGUAGES.keys()).index(st.session_state.language),
    )
    st.session_state.language = lang_display[selected_lang_name]

    reasoning = st.select_slider(
        "AI Reasoning Depth",
        options=["low", "medium", "high"],
        value="low",
        help="Higher = more thorough but slower responses.",
    )
    tts_enabled = st.checkbox("Read responses aloud (TTS)", value=False)

    if st.button("Start New Session"):
        sid = uuid.uuid4().hex[:8]
        client = SarvamClient(settings.sarvam_api_key)
        service = ITHelpdeskService(client)
        st.session_state.session = service.create_session(
            sid, st.session_state.language
        )
        st.session_state.chat_history = []
        st.session_state.pending_ticket = None
        st.rerun()

    st.markdown("---")
    st.markdown("**Quick Links**")
    st.markdown("- Password Reset Portal")
    st.markdown("- IT Service Catalog")
    st.markdown("- Company Intranet")

# ── Initialise services ──────────────────────────────────────────────────────

client = SarvamClient(settings.sarvam_api_key)
service = ITHelpdeskService(client)
tickets = TicketManager()

# ── Main tabs ────────────────────────────────────────────────────────────────

tab_report, tab_tickets, tab_kb, tab_dashboard = st.tabs(
    ["🆘 Report Issue", "🎫 My Tickets", "📚 Knowledge Base", "📊 Dashboard"]
)

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — Report Issue
# ════════════════════════════════════════════════════════════════════════════

with tab_report:
    st.header("Report an IT Issue")
    st.markdown(
        "Describe your problem below — in **any language**. "
        "The AI will diagnose the issue, suggest solutions, and offer to raise a support ticket."
    )

    if not st.session_state.session:
        sid = uuid.uuid4().hex[:8]
        st.session_state.session = service.create_session(
            sid, st.session_state.language
        )

    # ── Voice input ──────────────────────────────────────────────────────────
    with st.expander("🎙️ Upload audio to describe your issue"):
        audio_file = st.file_uploader("Upload WAV (max 10 MB)", type=["wav"])
        if audio_file and st.button("Transcribe Audio"):
            with st.spinner("Transcribing…"):
                try:
                    import io
                    stt_resp = client.speech_to_text(
                        io.BytesIO(audio_file.read()),
                        audio_file.name,
                        st.session_state.language,
                    )
                    st.success(f"Transcript: {stt_resp.transcript}")
                    st.session_state["_prefill"] = stt_resp.transcript
                except Exception as e:
                    st.error(f"Transcription error: {e}")

    # ── Chat interface ───────────────────────────────────────────────────────
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    prefill = st.session_state.pop("_prefill", "")
    user_input = st.chat_input(
        placeholder="Describe your IT issue here…",
        key="issue_input",
    ) or prefill

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Analysing your issue…"):
                result = service.diagnose(
                    st.session_state.session,
                    user_input,
                    reasoning_effort=reasoning,
                    tts_enabled=tts_enabled,
                )

            st.markdown(result["answer"])

            if tts_enabled and result["audio"]:
                combined = b"".join(result["audio"])
                if combined:
                    st.audio(combined, format="audio/wav")

        st.session_state.chat_history.append(
            {"role": "assistant", "content": result["answer"]}
        )
        st.session_state.last_response = result["answer"]

        # Show KB suggestions inline
        if result["kb_hits"]:
            with st.expander("📖 Related Knowledge Base Articles"):
                for hit in result["kb_hits"]:
                    st.markdown(f"**[{hit['id']}] {hit['title']}**")
                    st.markdown(hit["solution"])
                    st.markdown("---")

        # Auto-fill ticket creation form
        st.session_state.pending_ticket = {
            "title": user_input[:80],
            "description": user_input,
            "category": result["auto_category"],
            "priority": result["auto_priority"],
            "resolution_notes": result["answer"],
            "detected_lang": result["detected_lang"],
        }

    # ── Ticket creation from current conversation ────────────────────────────
    if st.session_state.pending_ticket and st.session_state.chat_history:
        st.divider()
        st.subheader("Create Support Ticket")
        pt = st.session_state.pending_ticket

        with st.form("create_ticket_form"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Issue Title", value=pt["title"])
                category = st.selectbox(
                    "Category",
                    ISSUE_CATEGORIES,
                    index=ISSUE_CATEGORIES.index(pt["category"]),
                )
            with col2:
                priority = st.selectbox(
                    "Priority",
                    PRIORITY_LEVELS,
                    index=PRIORITY_LEVELS.index(pt["priority"]),
                )
            description = st.text_area(
                "Description", value=pt["description"], height=100
            )

            submitted = st.form_submit_button("🎫 Raise Ticket")
            if submitted:
                ticket = tickets.create(
                    title=title,
                    description=description,
                    category=category,
                    priority=priority,
                    user_name=st.session_state.user_name,
                    user_language=pt.get(
                        "detected_lang", st.session_state.language
                    ),
                    resolution_notes=pt["resolution_notes"],
                )
                st.success(f"Ticket **{ticket['id']}** created successfully!")
                st.session_state.pending_ticket = None
                st.session_state.chat_history = []

    if st.session_state.chat_history:
        if st.button("🔄 Start New Conversation"):
            st.session_state.chat_history = []
            st.session_state.pending_ticket = None
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — My Tickets
# ════════════════════════════════════════════════════════════════════════════

with tab_tickets:
    st.header("Support Tickets")

    col1, col2, col3 = st.columns(3)
    with col1:
        filter_status = st.selectbox("Filter by Status", ["All"] + TICKET_STATUSES)
    with col2:
        filter_category = st.selectbox("Filter by Category", ["All"] + ISSUE_CATEGORIES)
    with col3:
        filter_priority = st.selectbox("Filter by Priority", ["All"] + PRIORITY_LEVELS)

    all_tickets = tickets.list_all(
        status=None if filter_status == "All" else filter_status,
        category=None if filter_category == "All" else filter_category,
        priority=None if filter_priority == "All" else filter_priority,
    )

    if not all_tickets:
        st.info("No tickets found matching the selected filters.")
    else:
        st.markdown(f"**{len(all_tickets)} ticket(s) found**")
        for ticket in all_tickets:
            priority_color = {
                "Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"
            }.get(ticket["priority"], "⚪")
            status_badge = {
                "Open": "🔓", "In Progress": "🔧", "Resolved": "✅", "Closed": "🔒"
            }.get(ticket["status"], "")

            with st.expander(
                f"{priority_color} **{ticket['id']}** — {ticket['title']} "
                f"{status_badge} *{ticket['status']}*"
            ):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**Category:** {ticket['category']}")
                    st.markdown(f"**Priority:** {ticket['priority']}")
                    st.markdown(f"**Reported by:** {ticket['user_name']}")
                with col_b:
                    st.markdown(f"**Status:** {ticket['status']}")
                    st.markdown(f"**Created:** {ticket['created_at'][:10]}")
                    st.markdown(
                        f"**Language:** "
                        f"{SUPPORTED_LANGUAGES.get(ticket['user_language'], ticket['user_language'])}"
                    )

                st.markdown("**Description:**")
                st.markdown(ticket["description"])

                if ticket["resolution_notes"]:
                    st.markdown("**AI Suggested Resolution:**")
                    st.markdown(ticket["resolution_notes"])

                new_status = st.selectbox(
                    "Update Status",
                    TICKET_STATUSES,
                    index=TICKET_STATUSES.index(ticket["status"]),
                    key=f"status_{ticket['id']}",
                )
                if st.button("Update", key=f"update_{ticket['id']}"):
                    tickets.update_status(ticket["id"], new_status)
                    st.success(f"Status updated to **{new_status}**")
                    st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — Knowledge Base
# ════════════════════════════════════════════════════════════════════════════

with tab_kb:
    st.header("IT Knowledge Base")
    st.markdown("Browse or search 20+ common IT issue resolutions.")

    kb = service._kb

    search_query = st.text_input(
        "🔍 Search knowledge base", placeholder="e.g., VPN, Outlook, printer…"
    )

    if search_query:
        results = kb.search(search_query, max_results=5)
        if results:
            st.markdown(f"**{len(results)} result(s) found:**")
            for entry in results:
                with st.expander(f"[{entry['id']}] {entry['title']}"):
                    st.markdown(f"**Category:** {entry['category']}")
                    st.markdown("**Solution:**")
                    st.markdown(entry["solution"])
                    st.markdown(f"*Escalate if: {entry['escalate_if']}*")
        else:
            st.info("No matching articles found. Try different keywords.")
    else:
        selected_cat = st.selectbox("Browse by Category", kb.get_all_categories())
        entries = kb.get_by_category(selected_cat)
        for entry in entries:
            with st.expander(f"[{entry['id']}] {entry['title']}"):
                st.markdown("**Solution:**")
                st.markdown(entry["solution"])
                st.markdown(f"*Escalate if: {entry['escalate_if']}*")

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — Dashboard
# ════════════════════════════════════════════════════════════════════════════

with tab_dashboard:
    st.header("Helpdesk Dashboard")

    stats = tickets.stats()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Tickets", stats["total"])
    col2.metric("Open", stats["by_status"].get("Open", 0))
    col3.metric("In Progress", stats["by_status"].get("In Progress", 0))
    col4.metric("Resolved", stats["by_status"].get("Resolved", 0))

    if stats["total"] > 0:
        import pandas as pd

        st.markdown("---")
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("Tickets by Category")
            cat_data = {k: v for k, v in stats["by_category"].items() if v > 0}
            if cat_data:
                st.bar_chart(pd.Series(cat_data))

        with col_right:
            st.subheader("Tickets by Priority")
            pri_data = {k: v for k, v in stats["by_priority"].items() if v > 0}
            if pri_data:
                st.bar_chart(pd.Series(pri_data))

        st.markdown("---")
        st.subheader("Recent Tickets")
        recent = tickets.list_all()[:5]
        if recent:
            rows = [
                {
                    "ID": t["id"],
                    "Title": t["title"][:50],
                    "Category": t["category"],
                    "Priority": t["priority"],
                    "Status": t["status"],
                    "Date": t["created_at"][:10],
                }
                for t in recent
            ]
            st.dataframe(
                pd.DataFrame(rows), use_container_width=True, hide_index=True
            )
    else:
        st.info("No tickets yet. Report an issue to get started!")

# ── Footer ───────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#888;'>"
    "Powered by <strong>Sarvam AI Enterprise</strong> · Multilingual IT Support Helpdesk"
    "</div>",
    unsafe_allow_html=True,
)
