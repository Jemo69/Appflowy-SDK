"""In-memory token storage."""

from __future__ import annotations

from appflowysdk.models import Token


class TokenStore:
    def __init__(self) -> None:
        self._access_token: str = ""
        self._refresh_token: str = ""
        self._expires_in: int = 0

    def set_token_store(self, token: Token) -> None:
        self._access_token = token.access_token
        self._refresh_token = token.refresh_token
        self._expires_in = token.expires_in

    def set_access_token(self, access_token: str) -> None:
        self._access_token = access_token

    def set_refresh_token(self, refresh_token: str) -> None:
        self._refresh_token = refresh_token

    def set_expires_in(self, expires_in: int) -> None:
        self._expires_in = expires_in

    def get_access_token(self) -> str:
        return self._access_token

    def get_refresh_token(self) -> str:
        return self._refresh_token

    def get_expires_in(self) -> int:
        return self._expires_in

    def get_token_store(self) -> Token:
        return Token(
            access_token=self._access_token,
            refresh_token=self._refresh_token,
            expires_in=self._expires_in,
        )

    def clear(self) -> None:
        self._access_token = ""
        self._refresh_token = ""
        self._expires_in = 0
