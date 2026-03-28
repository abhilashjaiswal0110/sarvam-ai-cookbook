"""Centralized configuration loaded from environment variables."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

# Load .env from the enterprise directory
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_PATH)


class Settings(BaseSettings):
    """Application-wide settings sourced from environment variables."""

    # ── Sarvam AI ──────────────────────────────────────────────────
    sarvam_api_key: str = Field(
        ...,
        description="Sarvam AI API key (from dashboard.sarvam.ai)",
    )

    # ── Application ────────────────────────────────────────────────
    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")

    # ── Rate Limiting ──────────────────────────────────────────────
    rate_limit_requests_per_minute: int = Field(default=60, ge=1)
    rate_limit_burst: int = Field(default=10, ge=1)

    # ── Server ─────────────────────────────────────────────────────
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000, ge=1024, le=65535)

    # ── Data Governance ────────────────────────────────────────────
    mask_pii_in_logs: bool = Field(default=True)
    audit_log_enabled: bool = Field(default=True)
    audit_log_file: str = Field(default="logs/audit.log")
    max_log_retention_days: int = Field(default=90, ge=1)

    @field_validator("sarvam_api_key")
    @classmethod
    def _api_key_not_placeholder(cls, v: str) -> str:
        if not v or v.startswith("your_"):
            raise ValueError(
                "SARVAM_API_KEY must be set to a valid key. "
                "Get one at https://dashboard.sarvam.ai/"
            )
        return v

    @field_validator("log_level")
    @classmethod
    def _log_level_valid(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v_upper

    model_config = {"env_prefix": "", "case_sensitive": False}


def get_settings() -> Settings:
    """Return validated settings; raises on missing/invalid config."""
    return Settings(
        sarvam_api_key=os.environ.get("SARVAM_API_KEY", ""),
    )
