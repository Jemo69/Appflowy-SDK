"""AppFlowy SDK exception hierarchy."""

from __future__ import annotations

from typing import Any


class AppFlowyError(Exception):
    """Base exception for all AppFlowy SDK errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        body: Any = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.body = body
        super().__init__(self.message)


class AuthenticationError(AppFlowyError):
    """Raised when authentication fails (login or token refresh)."""


class LoginError(AuthenticationError):
    """Raised when login fails."""


class RefreshTokenError(AuthenticationError):
    """Raised when token refresh fails."""


class APIError(AppFlowyError):
    """Raised when an API request returns a non-2xx status code."""


class NotFoundError(APIError):
    """Raised when a resource is not found (404)."""


class ValidationError(AppFlowyError):
    """Raised when SDK-side input validation fails."""


class NetworkError(AppFlowyError):
    """Raised when a network-level error occurs."""
