"""AppFlowy Cloud REST API client."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx

from appflowysdk.constants import BASE_URL
from appflowysdk.exceptions import (
    APIError,
    AuthenticationError,
    LoginError,
    NetworkError,
    RefreshTokenError,
    ValidationError,
)
from appflowysdk.logger import logger
from appflowysdk.models import (
    AddDatabaseRowRequest,
    Database,
    DatabaseField,
    DatabaseFieldsResponse,
    DatabaseRow,
    DatabaseRowDetail,
    DatabaseRowDetailsResponse,
    DatabaseRowsResponse,
    DatabaseRowsUpdatedResponse,
    DatabaseRowUpdated,
    DatabasesResponse,
    FolderResponse,
    FolderView,
    Token,
    TokenResponse,
    UpsertDatabaseRowRequest,
    Workspace,
    WorkspacesResponse,
)
from appflowysdk.tokenstore import TokenStore


class AppFlowy:
    """Type-safe Python SDK for the AppFlowy Cloud REST API."""

    def __init__(
        self,
        email: str | None = None,
        password: str | None = None,
        base_url: str = BASE_URL,
    ) -> None:
        self.email = email
        self.password = password
        self.base_url = base_url.rstrip("/")
        self.token_store = TokenStore()
        self._http_client = httpx.Client(timeout=30.0)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        access_token = self.token_store.get_access_token()
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        return headers

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        try:
            body: dict[str, Any] = response.json()
        except Exception:
            raise APIError(
                "Failed to parse response body",
                status_code=response.status_code,
                body=response.text,
            )

        if response.status_code >= 400:
            message = body.get("message", f"HTTP {response.status_code}")
            raise APIError(
                message=message,
                status_code=response.status_code,
                body=body,
            )

        return body

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            response = self._http_client.request(
                method=method,
                url=url,
                headers=self._headers(),
                params=params,
                json=json_body,
            )
            return self._handle_response(response)
        except (APIError, AuthenticationError):
            raise
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {e}") from e
        except httpx.TimeoutException as e:
            raise NetworkError(f"Request timed out: {e}") from e
        except Exception as e:
            raise APIError(f"Unexpected error: {e}") from e

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def login(self) -> TokenResponse:
        """Authenticate with email and password.

        Returns:
            TokenResponse with access and refresh tokens.

        Raises:
            LoginError: If credentials are missing or login fails.
            NetworkError: If a network error occurs.
        """
        if not self.email or not self.password:
            raise LoginError("Email and password are required for login.")

        logger.info("Logging in as %s", self.email)
        try:
            body = self._request(
                "POST",
                "/gotrue/token?grant_type=password",
                json_body={
                    "email": self.email,
                    "password": self.password,
                },
            )
            token_response = TokenResponse(**body)
            self.token_store.set_token_store(
                Token(
                    access_token=token_response.access_token,
                    refresh_token=token_response.refresh_token,
                    expires_in=token_response.expires_in,
                )
            )
            logger.info("Login successful")
            return token_response
        except APIError as e:
            raise LoginError(
                f"Login failed: {e.message}",
                status_code=e.status_code,
                body=e.body,
            ) from e

    def refresh_token(self) -> TokenResponse:
        """Refresh the access token using the stored refresh token.

        Returns:
            TokenResponse with new access and refresh tokens.

        Raises:
            RefreshTokenError: If no refresh token is stored or refresh fails.
            NetworkError: If a network error occurs.
        """
        stored_refresh = self.token_store.get_refresh_token()
        if not stored_refresh:
            raise RefreshTokenError("No refresh token available. Please login first.")

        logger.info("Refreshing access token")
        try:
            body = self._request(
                "POST",
                "/gotrue/token?grant_type=refresh_token",
                json_body={"refresh_token": stored_refresh},
            )
            token_response = TokenResponse(**body)
            self.token_store.set_token_store(
                Token(
                    access_token=token_response.access_token,
                    refresh_token=token_response.refresh_token,
                    expires_in=token_response.expires_in,
                )
            )
            logger.info("Token refreshed successfully")
            return token_response
        except APIError as e:
            raise RefreshTokenError(
                f"Token refresh failed: {e.message}",
                status_code=e.status_code,
                body=e.body,
            ) from e

    def oauth_redirect_token(
        self,
        code: str,
        grant_type: str,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        redirect_uri: str | None = None,
        code_verifier: str | None = None,
    ) -> TokenResponse:
        """Exchange an OAuth authorization code for tokens.

        Returns:
            TokenResponse with access and refresh tokens.
        """
        params: dict[str, Any] = {
            "code": code,
            "grant_type": grant_type,
        }
        if client_id is not None:
            params["client_id"] = client_id
        if client_secret is not None:
            params["client_secret"] = client_secret
        if redirect_uri is not None:
            params["redirect_uri"] = redirect_uri
        if code_verifier is not None:
            params["code_verifier"] = code_verifier

        logger.info("Exchanging OAuth code for token")
        body = self._request("GET", "/web-api/oauth-redirect/token", params=params)
        token_response = TokenResponse(**body)
        self.token_store.set_token_store(
            Token(
                access_token=token_response.access_token,
                refresh_token=token_response.refresh_token,
                expires_in=token_response.expires_in,
            )
        )
        return token_response

    # ------------------------------------------------------------------
    # Workspaces
    # ------------------------------------------------------------------

    def get_workspaces(
        self,
        *,
        include_member_count: bool | None = None,
        include_role: bool | None = None,
    ) -> list[Workspace]:
        """Retrieve all workspaces for the authenticated user."""
        params: dict[str, Any] = {}
        if include_member_count is not None:
            params["include_member_count"] = include_member_count
        if include_role is not None:
            params["include_role"] = include_role

        body = self._request("GET", "/api/workspace", params=params)
        response = WorkspacesResponse(**body)
        return response.data

    # ------------------------------------------------------------------
    # Workspace folder
    # ------------------------------------------------------------------

    def get_workspace_folder(
        self,
        workspace_id: str,
        *,
        depth: int | None = None,
        root_view_id: str | None = None,
    ) -> FolderView:
        """Retrieve the folder structure of a workspace."""
        params: dict[str, Any] = {}
        if depth is not None:
            params["depth"] = depth
        if root_view_id is not None:
            params["root_view_id"] = root_view_id

        body = self._request(
            "GET",
            f"/api/workspace/{workspace_id}/folder",
            params=params,
        )
        response = FolderResponse(**body)
        if response.data is None:
            raise APIError("Server returned null folder data")
        return response.data

    # ------------------------------------------------------------------
    # Databases
    # ------------------------------------------------------------------

    def get_databases(self, workspace_id: str) -> list[Database]:
        """Retrieve all databases in a workspace."""
        body = self._request(
            "GET",
            f"/api/workspace/{workspace_id}/database",
        )
        response = DatabasesResponse(**body)
        return response.data

    def get_database_fields(
        self,
        workspace_id: str,
        database_id: str,
    ) -> list[DatabaseField]:
        """Retrieve all fields in a database."""
        body = self._request(
            "GET",
            f"/api/workspace/{workspace_id}/database/{database_id}/fields",
        )
        response = DatabaseFieldsResponse(**body)
        return response.data

    # ------------------------------------------------------------------
    # Database rows
    # ------------------------------------------------------------------

    def get_database_row_ids(
        self,
        workspace_id: str,
        database_id: str,
    ) -> list[DatabaseRow]:
        """Retrieve all row IDs in a database."""
        body = self._request(
            "GET",
            f"/api/workspace/{workspace_id}/database/{database_id}/row",
        )
        response = DatabaseRowsResponse(**body)
        return response.data

    def create_database_row(
        self,
        workspace_id: str,
        database_id: str,
        *,
        cells: dict[str, Any] | None = None,
        document: str | None = None,
    ) -> str:
        """Create a new row in a database.

        Returns:
            UUID of the newly created row.
        """
        request = AddDatabaseRowRequest(
            cells=cells or {},
            document=document,
        )
        body = self._request(
            "POST",
            f"/api/workspace/{workspace_id}/database/{database_id}/row",
            json_body=request.model_dump(exclude_none=True),
        )
        return str(body.get("data", ""))

    def upsert_database_row(
        self,
        workspace_id: str,
        database_id: str,
        pre_hash: str,
        *,
        cells: dict[str, Any] | None = None,
        document: str | None = None,
    ) -> str:
        """Update or insert a row identified by ``pre_hash``.

        Returns:
            UUID of the created or updated row.
        """
        request = UpsertDatabaseRowRequest(
            pre_hash=pre_hash,
            cells=cells or {},
            document=document,
        )
        body = self._request(
            "PUT",
            f"/api/workspace/{workspace_id}/database/{database_id}/row",
            json_body=request.model_dump(exclude_none=True),
        )
        return str(body.get("data", ""))

    # ------------------------------------------------------------------
    # Row updates
    # ------------------------------------------------------------------

    def get_database_row_ids_updated(
        self,
        workspace_id: str,
        database_id: str,
        *,
        after: datetime | str | None = None,
    ) -> list[DatabaseRowUpdated]:
        """Retrieve row IDs updated after a given timestamp."""
        params: dict[str, Any] = {}
        if after is not None:
            params["after"] = (
                after.isoformat() if isinstance(after, datetime) else after
            )

        body = self._request(
            "GET",
            f"/api/workspace/{workspace_id}/database/{database_id}/row/updated",
            params=params,
        )
        response = DatabaseRowsUpdatedResponse(**body)
        return response.data

    # ------------------------------------------------------------------
    # Row details
    # ------------------------------------------------------------------

    def get_database_row_details(
        self,
        workspace_id: str,
        database_id: str,
        row_ids: list[str],
        *,
        with_doc: bool | None = None,
    ) -> list[DatabaseRowDetail]:
        """Retrieve detailed information for specific database rows.

        Raises:
            ValidationError: If no row IDs are provided.
        """
        if not row_ids:
            raise ValidationError("At least one row ID is required.")

        params: dict[str, Any] = {"ids": ",".join(row_ids)}
        if with_doc is not None:
            params["with_doc"] = with_doc

        body = self._request(
            "GET",
            f"/api/workspace/{workspace_id}/database/{database_id}/row/detail",
            params=params,
        )
        response = DatabaseRowDetailsResponse(**body)
        return response.data

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._http_client.close()

    def __enter__(self) -> AppFlowy:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        self.close()
