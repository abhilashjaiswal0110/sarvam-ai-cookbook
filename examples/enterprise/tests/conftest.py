"""Shared test fixtures for the enterprise test suite."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure enterprise root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture()
def mock_api_key() -> str:
    return "test_key_abc123"


@pytest.fixture()
def mock_settings(mock_api_key: str):
    """Patch environment so Settings can be created without a real API key."""
    with patch.dict(os.environ, {"SARVAM_API_KEY": mock_api_key}):
        from core.config import get_settings

        yield get_settings()


@pytest.fixture()
def mock_sarvam_client(mock_api_key: str):
    """Return a SarvamClient with a mocked _request method."""
    from core.sarvam_client import SarvamClient

    client = SarvamClient(mock_api_key, audit_enabled=False)
    client._request = MagicMock()  # type: ignore[assignment]
    return client
