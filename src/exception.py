from typing import Any


class AppFlowyError(Exception):
    """Base exception for all AppFlowy SDK errors."""

    def __init__(
        self, message: str, status_code: int | None = None, body: Any = None
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.body = body
        super().__init__(self.message)


class AuthenticationError(AppFlowyError):
    """Raised when authentication fails (login or token refresh)."""

    pass


class LoginError(AuthenticationError):
    """Raised when login fails."""

    pass


class RefreshTokenError(AuthenticationError):
    """Raised when token refresh fails."""

    pass


class APIError(AppFlowyError):
    """Raised when an API request returns a non-200 status code."""

    pass


class NotFoundError(APIError):
    """Raised when a resource is not found (404)."""

    pass


class ValidationError(AppFlowyError):
    """Raised when input validation fails."""

    pass


class NetworkError(AppFlowyError):
    """Raised when a network error occurs."""

    pass
