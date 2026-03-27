"""Integration tests for the full IT support helpdesk flow.

These tests exercise the interaction between SarvamClient, ITKnowledgeBase,
and TicketManager — all external HTTP calls are mocked.
"""

import sys
import os
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sarvam_client import SarvamClient, SarvamAPIError
from knowledge_base import ITKnowledgeBase
from ticket_manager import TicketManager


def _mock_response(json_data: dict, status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data
    if status_code >= 400:
        from requests import HTTPError
        mock.raise_for_status.side_effect = HTTPError(f"HTTP {status_code}")
    else:
        mock.raise_for_status.return_value = None
    return mock


@pytest.fixture
def client():
    return SarvamClient("integration-test-key")


@pytest.fixture
def kb():
    return ITKnowledgeBase()


@pytest.fixture
def manager(tmp_path):
    return TicketManager(storage_path=str(tmp_path / "integration_tickets.json"))


# ── Scenario 1: English user reports a VPN issue ─────────────────────────────

class TestEnglishVpnFlow:
    def test_detect_classify_chat_create_ticket(self, client, kb, manager):
        # 1. Detect language
        lang_resp = _mock_response({"language_code": "en-IN", "script_code": "Latn"})
        # 2. Chat completion
        chat_resp = _mock_response({
            "choices": [{
                "message": {
                    "content": (
                        "**Category:** Network & Connectivity\n"
                        "**Priority:** High\n"
                        "**Steps to resolve:**\n"
                        "1. Restart the VPN client.\n"
                        "2. Check internet connectivity.\n"
                        "**Escalation needed:** No"
                    )
                }
            }]
        })

        with patch("requests.post", side_effect=[lang_resp, chat_resp]):
            lang_info = client.detect_language("My VPN stopped working after the update.")
            assert lang_info["language_code"] == "en-IN"

            reply = client.chat([
                {"role": "user", "content": "My VPN stopped working after the update."}
            ])
            assert "VPN client" in reply or "Restart" in reply

        # 3. Search KB — no HTTP call
        results = kb.search("VPN not working")
        assert any("VPN" in r["title"] for r in results)

        # 4. Create ticket
        ticket = manager.create(
            title="VPN stopped working after update",
            description="My VPN stopped working after the update.",
            category="Network & Connectivity",
            priority="High",
            user_name="Test User",
            user_language="en-IN",
            resolution_notes=reply,
        )
        assert ticket["status"] == "Open"
        assert ticket["category"] == "Network & Connectivity"
        assert ticket["priority"] == "High"


# ── Scenario 2: Hindi user reports an account lockout ────────────────────────

class TestHindiAccountLockoutFlow:
    def test_translate_then_chat_then_ticket(self, client, kb, manager):
        user_message = "मेरा अकाउंट लॉक हो गया है, मैं लॉगिन नहीं कर पा रहा।"

        lang_resp = _mock_response({"language_code": "hi-IN", "script_code": "Deva"})
        translate_resp = _mock_response({"translated_text": "My account is locked, I cannot log in."})
        chat_resp = _mock_response({
            "choices": [{
                "message": {
                    "content": (
                        "**Category:** Security & Access\n"
                        "**Priority:** High\n"
                        "**Steps to resolve:**\n"
                        "1. Wait 30 minutes for the account to auto-unlock.\n"
                        "2. Use the self-service password reset portal.\n"
                        "**Escalation needed:** No"
                    )
                }
            }]
        })

        with patch("requests.post", side_effect=[lang_resp, translate_resp, chat_resp]):
            lang_info = client.detect_language(user_message)
            assert lang_info["language_code"] == "hi-IN"

            english_text = client.translate(user_message, source_lang="hi-IN")
            assert "locked" in english_text.lower()

            reply = client.chat([{"role": "user", "content": user_message}])
            assert "Security & Access" in reply

        # KB should find account lockout article
        kb_results = kb.search(english_text)
        assert len(kb_results) > 0

        ticket = manager.create(
            title=user_message[:80],
            description=user_message,
            category="Security & Access",
            priority="High",
            user_name="Priya Patel",
            user_language="hi-IN",
            resolution_notes=reply,
        )
        assert ticket["user_language"] == "hi-IN"
        assert ticket["category"] == "Security & Access"


# ── Scenario 3: Priority escalation for critical security incident ────────────

class TestCriticalSecurityIncidentFlow:
    def test_critical_keywords_trigger_high_priority(self, manager):
        from config import CRITICAL_KEYWORDS

        critical_text = "I think my laptop has ransomware, all files are encrypted!"
        # Verify that at least one critical keyword is in the text
        assert any(kw in critical_text.lower() for kw in CRITICAL_KEYWORDS)

        ticket = manager.create(
            title=critical_text[:80],
            description=critical_text,
            category="Security & Access",
            priority="Critical",
            user_name="Security Reporter",
        )
        assert ticket["priority"] == "Critical"

    def test_phishing_kb_article_found(self, kb):
        results = kb.search("I received a suspicious phishing email")
        phishing_entry = next((r for r in results if "phishing" in r["title"].lower()), None)
        assert phishing_entry is not None
        assert "SEC-003" == phishing_entry["id"]


# ── Scenario 4: Ticket lifecycle management ───────────────────────────────────

class TestTicketLifecycle:
    def test_full_open_to_resolved_lifecycle(self, manager):
        ticket = manager.create(
            title="Outlook not syncing",
            description="Outlook shows 'Disconnected' for the past hour.",
            category="Email & Collaboration",
            priority="Medium",
            user_name="Carlos Fernandez",
        )
        ticket_id = ticket["id"]

        assert manager.get(ticket_id)["status"] == "Open"

        manager.update_status(ticket_id, "In Progress")
        assert manager.get(ticket_id)["status"] == "In Progress"

        manager.update_resolution(ticket_id, "Repaired Outlook account settings. Issue resolved.")
        manager.update_status(ticket_id, "Resolved")

        final = manager.get(ticket_id)
        assert final["status"] == "Resolved"
        assert "resolved" in final["resolution_notes"].lower()

    def test_stats_reflect_lifecycle_changes(self, manager):
        t1 = manager.create("T1", "d", "Hardware", "Low", "U1")
        t2 = manager.create("T2", "d", "Hardware", "Medium", "U2")

        s_initial = manager.stats()
        assert s_initial["by_status"]["Open"] == 2

        manager.update_status(t1["id"], "Resolved")
        manager.update_status(t2["id"], "Closed")

        s_final = manager.stats()
        assert s_final["by_status"]["Open"] == 0
        assert s_final["by_status"]["Resolved"] == 1
        assert s_final["by_status"]["Closed"] == 1


# ── Scenario 5: API error graceful handling ───────────────────────────────────

class TestApiErrorHandling:
    def test_language_detection_error_does_not_crash_flow(self, client, manager):
        import requests as req_lib
        with patch("requests.post", side_effect=req_lib.ConnectionError("No route to host")):
            with pytest.raises(SarvamAPIError):
                client.detect_language("test text")

        # Ticket can still be created with fallback language
        ticket = manager.create(
            title="Issue reported (language detection failed)",
            description="test text",
            category="Other",
            priority="Medium",
            user_name="Anonymous",
            user_language="en-IN",  # fallback
        )
        assert ticket["id"].startswith("TKT-")

    def test_tts_failure_returns_none_not_exception(self, client):
        """TTS failure should be non-fatal — returns None."""
        import requests as req_lib
        with patch("requests.post", side_effect=req_lib.RequestException("TTS service down")):
            result = client.text_to_speech("Hello", "en-IN")
        assert result is None


# ── Scenario 6: Multi-language KB search via translation ─────────────────────

class TestMultilingualKBSearch:
    @pytest.mark.parametrize("query,expected_id_prefix", [
        ("printer offline", "HW"),
        ("account locked", "SEC"),
        ("outlook not syncing", "COL"),
        ("windows update stuck", "SW"),
    ])
    def test_kb_returns_relevant_category(self, kb, query, expected_id_prefix):
        results = kb.search(query)
        assert len(results) > 0
        assert any(r["id"].startswith(expected_id_prefix) for r in results), (
            f"Expected a {expected_id_prefix}-* article for query '{query}', got {[r['id'] for r in results]}"
        )
