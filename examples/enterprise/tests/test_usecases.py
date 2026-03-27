"""Tests for use-case service layers (mocked API calls)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


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
