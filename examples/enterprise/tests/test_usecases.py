"""Tests for use-case service layers (mocked API calls)."""

from __future__ import annotations

from unittest.mock import MagicMock


class TestOnboardingService:
    def test_create_session(self, mock_sarvam_client) -> None:
        from usecases.rural_bank_onboarding.service import OnboardingService

        svc = OnboardingService(mock_sarvam_client)
        session = svc.create_session("test-1", "hi-IN")
        assert session.session_id == "test-1"
        assert session.language_code == "hi-IN"
        assert "welcome" in svc.get_current_step(session)

    def test_step_advancement(self, mock_sarvam_client) -> None:
        from usecases.rural_bank_onboarding.service import OnboardingService

        svc = OnboardingService(mock_sarvam_client)
        session = svc.create_session("test-2", "hi-IN")
        assert svc.get_current_step(session) == "welcome"

        # Simulate advancing
        svc._maybe_advance_step(session, "next")
        assert svc.get_current_step(session) == "language_select"


class TestLearningService:
    def test_create_session(self, mock_sarvam_client) -> None:
        from usecases.anganwadi_learning.service import LearningService

        svc = LearningService(mock_sarvam_client)
        session = svc.create_session("test-3", "ta-IN")
        assert session.language_code == "ta-IN"


class TestBroadcastService:
    def test_broadcast_to_multiple(self, mock_sarvam_client) -> None:
        from usecases.flood_cyclone_broadcaster.service import BroadcastService

        # Mock translate and TTS
        mock_sarvam_client.translate = MagicMock(return_value="translated")
        mock_sarvam_client.text_to_speech = MagicMock(return_value=[b"audio"])

        svc = BroadcastService(mock_sarvam_client)
        result = svc.broadcast_alert(
            "Test alert", "en-IN", ["hi-IN", "ta-IN"]
        )
        assert len(result.broadcasts) == 2
        assert result.failed_languages == []


class TestRTIDraftingService:
    def test_create_session(self, mock_sarvam_client) -> None:
        from usecases.rti_drafter.service import RTIDraftingService

        svc = RTIDraftingService(mock_sarvam_client)
        session = svc.create_session("test-4")
        assert session.metadata["stage"] == "awaiting_input"


class TestITHelpdeskService:
    def test_create_session(self, mock_sarvam_client) -> None:
        from usecases.it_support_helpdesk.service import ITHelpdeskService

        svc = ITHelpdeskService(mock_sarvam_client)
        session = svc.create_session("helpdesk-1", "en-IN")
        assert session.session_id == "helpdesk-1"
        assert session.language_code == "en-IN"
        assert "HelpDesk AI" in session.system_prompt

    def test_create_session_hindi(self, mock_sarvam_client) -> None:
        from usecases.it_support_helpdesk.service import ITHelpdeskService

        svc = ITHelpdeskService(mock_sarvam_client)
        session = svc.create_session("helpdesk-2", "hi-IN")
        assert session.language_code == "hi-IN"
        assert "Hindi" in session.system_prompt

    def test_diagnose_english(self, mock_sarvam_client) -> None:
        from core.models import LanguageDetectionResponse
        from usecases.it_support_helpdesk.service import ITHelpdeskService

        # Setup mocks
        mock_sarvam_client.detect_language = MagicMock(
            return_value=LanguageDetectionResponse(language_code="en-IN", confidence=0.99)
        )
        mock_sarvam_client.chat = MagicMock(
            return_value="**Category:** Network\n**Steps:** 1. Restart VPN"
        )

        svc = ITHelpdeskService(mock_sarvam_client)
        session = svc.create_session("diag-1", "en-IN")
        result = svc.diagnose(session, "vpn not connecting", reasoning_effort="medium")

        assert result["detected_lang"] == "en-IN"
        assert result["answer"] == "**Category:** Network\n**Steps:** 1. Restart VPN"
        assert result["answer_en"] == result["answer"]  # English, no translation
        assert result["auto_category"] == "Network & Connectivity"
        assert len(result["kb_hits"]) > 0
        assert result["audio"] == []

        # Verify reasoning_effort was forwarded to chat
        mock_sarvam_client.chat.assert_called_once()
        call_kwargs = mock_sarvam_client.chat.call_args
        assert call_kwargs.kwargs.get("reasoning_effort") == "medium"

    def test_diagnose_hindi_with_translation(self, mock_sarvam_client) -> None:
        from core.models import LanguageDetectionResponse
        from usecases.it_support_helpdesk.service import ITHelpdeskService

        mock_sarvam_client.detect_language = MagicMock(
            return_value=LanguageDetectionResponse(language_code="hi-IN", confidence=0.95)
        )
        mock_sarvam_client.translate = MagicMock(side_effect=[
            "printer is not working",   # issue translated to English for KB
            "English version of reply",  # answer translated to English
        ])
        mock_sarvam_client.chat = MagicMock(
            return_value="प्रिंटर को रीस्टार्ट करें"
        )

        svc = ITHelpdeskService(mock_sarvam_client)
        session = svc.create_session("diag-2", "en-IN")
        result = svc.diagnose(session, "प्रिंटर काम नहीं कर रहा")

        assert result["detected_lang"] == "hi-IN"
        assert session.language_code == "hi-IN"  # Updated by detection
        assert result["answer_en"] == "English version of reply"
        assert "Hindi" in session.system_prompt

    def test_diagnose_with_tts(self, mock_sarvam_client) -> None:
        from core.models import LanguageDetectionResponse
        from usecases.it_support_helpdesk.service import ITHelpdeskService

        mock_sarvam_client.detect_language = MagicMock(
            return_value=LanguageDetectionResponse(language_code="en-IN", confidence=0.99)
        )
        mock_sarvam_client.chat = MagicMock(return_value="Restart your laptop.")
        mock_sarvam_client.text_to_speech = MagicMock(return_value=[b"audio_bytes"])

        svc = ITHelpdeskService(mock_sarvam_client)
        session = svc.create_session("diag-3", "en-IN")
        result = svc.diagnose(session, "laptop frozen", tts_enabled=True)

        assert result["audio"] == [b"audio_bytes"]
        mock_sarvam_client.text_to_speech.assert_called_once()

    def test_diagnose_detection_fallback(self, mock_sarvam_client) -> None:
        from usecases.it_support_helpdesk.service import ITHelpdeskService

        mock_sarvam_client.detect_language = MagicMock(side_effect=Exception("API down"))
        mock_sarvam_client.chat = MagicMock(return_value="Check your network settings.")

        svc = ITHelpdeskService(mock_sarvam_client)
        session = svc.create_session("diag-4", "en-IN")
        result = svc.diagnose(session, "internet not working")

        assert result["detected_lang"] == "en-IN"  # Falls back to session language
        assert result["answer"] == "Check your network settings."

    def test_auto_priority_critical(self) -> None:
        from usecases.it_support_helpdesk.service import ITHelpdeskService

        assert ITHelpdeskService._auto_priority("we have a ransomware attack") == "Critical"
        assert ITHelpdeskService._auto_priority("server down and data loss") == "Critical"

    def test_auto_priority_high(self) -> None:
        from usecases.it_support_helpdesk.service import ITHelpdeskService

        assert ITHelpdeskService._auto_priority("I'm locked out and cannot work") == "High"

    def test_auto_priority_medium(self) -> None:
        from usecases.it_support_helpdesk.service import ITHelpdeskService

        assert ITHelpdeskService._auto_priority("my printer is not working") == "Medium"

    def test_auto_category(self) -> None:
        from usecases.it_support_helpdesk.service import ITHelpdeskService

        assert ITHelpdeskService._auto_category("vpn not connecting") == "Network & Connectivity"
        assert ITHelpdeskService._auto_category("laptop screen broken") == "Hardware"
        assert ITHelpdeskService._auto_category("outlook not syncing") == "Email & Collaboration"
        assert ITHelpdeskService._auto_category("account locked out") == "Security & Access"
        assert ITHelpdeskService._auto_category("excel keeps crashing") == "Software & Applications"
        assert ITHelpdeskService._auto_category("something random") == "Other"


class TestITKnowledgeBase:
    def test_search_vpn(self) -> None:
        from usecases.it_support_helpdesk.knowledge_base import ITKnowledgeBase

        kb = ITKnowledgeBase()
        results = kb.search("vpn connection failing")
        assert len(results) > 0
        assert results[0]["id"] == "NET-001"

    def test_search_printer(self) -> None:
        from usecases.it_support_helpdesk.knowledge_base import ITKnowledgeBase

        kb = ITKnowledgeBase()
        results = kb.search("printer offline")
        assert len(results) > 0
        assert any(r["id"] == "HW-002" for r in results)

    def test_search_no_results(self) -> None:
        from usecases.it_support_helpdesk.knowledge_base import ITKnowledgeBase

        kb = ITKnowledgeBase()
        results = kb.search("xyznonexistent12345")
        assert results == []

    def test_get_all_categories(self) -> None:
        from usecases.it_support_helpdesk.knowledge_base import ITKnowledgeBase

        kb = ITKnowledgeBase()
        cats = kb.get_all_categories()
        assert "Network & Connectivity" in cats
        assert "Hardware" in cats
        assert "Security & Access" in cats

    def test_get_by_category(self) -> None:
        from usecases.it_support_helpdesk.knowledge_base import ITKnowledgeBase

        kb = ITKnowledgeBase()
        hw = kb.get_by_category("Hardware")
        assert len(hw) > 0
        assert all(e["category"] == "Hardware" for e in hw)

    def test_format_for_prompt(self) -> None:
        from usecases.it_support_helpdesk.knowledge_base import ITKnowledgeBase

        kb = ITKnowledgeBase()
        prompt = kb.format_for_prompt("vpn issues")
        assert "NET-001" in prompt
        assert "Relevant KB articles found" in prompt

    def test_format_for_prompt_no_match(self) -> None:
        from usecases.it_support_helpdesk.knowledge_base import ITKnowledgeBase

        kb = ITKnowledgeBase()
        prompt = kb.format_for_prompt("xyznonexistent12345")
        assert prompt == ""


class TestTicketManager:
    def test_create_and_get(self, tmp_path) -> None:
        from usecases.it_support_helpdesk.ticket_manager import TicketManager

        tm = TicketManager(storage_path=str(tmp_path / "tickets.json"))
        ticket = tm.create(
            title="VPN issue",
            description="Cannot connect to VPN",
            category="Network & Connectivity",
            priority="High",
            user_name="TestUser",
        )
        assert ticket["id"].startswith("TKT-")
        assert ticket["status"] == "Open"

        fetched = tm.get(ticket["id"])
        assert fetched["title"] == "VPN issue"

    def test_update_status(self, tmp_path) -> None:
        from usecases.it_support_helpdesk.ticket_manager import TicketManager

        tm = TicketManager(storage_path=str(tmp_path / "tickets.json"))
        ticket = tm.create(
            title="Test",
            description="Desc",
            category="Other",
            priority="Medium",
            user_name="User",
        )
        updated = tm.update_status(ticket["id"], "Resolved")
        assert updated["status"] == "Resolved"

    def test_list_and_filter(self, tmp_path) -> None:
        from usecases.it_support_helpdesk.ticket_manager import TicketManager

        tm = TicketManager(storage_path=str(tmp_path / "tickets.json"))
        tm.create("A", "d", "Hardware", "High", "U")
        tm.create("B", "d", "Other", "Low", "U")

        all_t = tm.list_all()
        assert len(all_t) == 2

        hw = tm.list_all(category="Hardware")
        assert len(hw) == 1
        assert hw[0]["title"] == "A"

    def test_stats(self, tmp_path) -> None:
        from usecases.it_support_helpdesk.ticket_manager import TicketManager

        tm = TicketManager(storage_path=str(tmp_path / "tickets.json"))
        tm.create("A", "d", "Hardware", "High", "U")
        tm.create("B", "d", "Other", "Low", "U")

        s = tm.stats()
        assert s["total"] == 2
        assert s["by_status"]["Open"] == 2

    def test_invalid_category_defaults(self, tmp_path) -> None:
        from usecases.it_support_helpdesk.ticket_manager import TicketManager

        tm = TicketManager(storage_path=str(tmp_path / "tickets.json"))
        ticket = tm.create("T", "D", "NonExistent", "SuperHigh", "U")
        assert ticket["category"] == "Other"
        assert ticket["priority"] == "Medium"

    def test_ticket_not_found(self, tmp_path) -> None:
        import pytest
        from usecases.it_support_helpdesk.ticket_manager import (
            TicketManager,
            TicketNotFoundError,
        )

        tm = TicketManager(storage_path=str(tmp_path / "tickets.json"))
        with pytest.raises(TicketNotFoundError):
            tm.get("TKT-NONEXISTENT")
