"""Custom exception hierarchy for Sarvam Enterprise applications."""

from __future__ import annotations


class SarvamEnterpriseError(Exception):
    """Base exception for all enterprise use-case errors."""

    def __init__(self, message: str, *, code: str = "INTERNAL_ERROR") -> None:
        self.code = code
        super().__init__(message)


class ConfigurationError(SarvamEnterpriseError):
    """Missing or invalid configuration."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="CONFIG_ERROR")


class AuthenticationError(SarvamEnterpriseError):
    """API key missing, invalid, or expired."""

    def __init__(self, message: str = "Invalid or missing API key") -> None:
        super().__init__(message, code="AUTH_ERROR")


class RateLimitError(SarvamEnterpriseError):
    """Upstream rate limit exceeded."""

    def __init__(self, retry_after: float | None = None) -> None:
        self.retry_after = retry_after
        msg = "Rate limit exceeded"
        if retry_after:
            msg += f" — retry after {retry_after:.1f}s"
        super().__init__(msg, code="RATE_LIMIT")


class ValidationError(SarvamEnterpriseError):
    """Input validation failure."""

    def __init__(self, message: str, *, field: str | None = None) -> None:
        self.field = field
        super().__init__(message, code="VALIDATION_ERROR")


class APIError(SarvamEnterpriseError):
    """Upstream Sarvam API returned an error."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        upstream_code: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.upstream_code = upstream_code
        super().__init__(message, code="API_ERROR")


class ContentFilterError(SarvamEnterpriseError):
    """Input or output blocked by content safety filters."""

    def __init__(self, message: str = "Content blocked by safety filter") -> None:
        super().__init__(message, code="CONTENT_FILTER")
