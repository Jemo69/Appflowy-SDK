from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx

from src.consontant import BASE_URL
from src.exception import (
    APIError,
    AuthenticationError,
    LoginError,
    NetworkError,
    RefreshTokenError,
    ValidationError,
)
from src.logger import logger
from src.models import (
    AddDatabaseRowRequest,
    ApiResponse,
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
from src.tokenstore import TokenStore


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
        """Validate HTTP response and return parsed JSON body."""
        try:
            body: dict[str, Any] = response.json()
        except Exception:
            raise APIError(
                f"Failed to parse response body",
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
        """Make an authenticated HTTP request."""
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
        """Authenticate with email and password, obtaining access/refresh tokens.

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
        client_id: str | None = None,
        client_secret: str | None = None,
        redirect_uri: str | None = None,
        code_verifier: str | None = None,
    ) -> TokenResponse:
        """Exchange an OAuth authorization code for access/refresh tokens.

        Args:
            code: The authorization code received from the OAuth redirect.
            grant_type: Type of OAuth 2.0 flow.
            client_id: Optional client ID.
            client_secret: Optional client secret.
            redirect_uri: Optional redirect URI.
            code_verifier: Optional PKCE code verifier.

        Raises:
            APIError: If the token exchange fails.
            NetworkError: If a network error occurs.
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
        include_member_count: bool | None = None,
        include_role: bool | None = None,
    ) -> list[Workspace]:
        """Retrieve all workspaces for the authenticated user.

        Args:
            include_member_count: Include member count in the response.
            include_role: Include the user's role in the response.

        Raises:
            APIError: If the request fails.
        """
        params: dict[str, Any] = {}
        if include_member_count is not None:
            params["include_member_count"] = include_member_count
        if include_role is not None:
            params["include_role"] = include_role

        body = self._request("GET", "/api/workspace", params=params)
        response = WorkspacesResponse(**body)
        return response.data

    # ------------------------------------------------------------------
    # Workspace Folder
    # ------------------------------------------------------------------

    def get_workspace_folder(
        self,
        workspace_id: str,
        depth: int | None = None,
        root_view_id: str | None = None,
    ) -> FolderView:
        """Retrieve the folder structure of a workspace.

        Args:
            workspace_id: The workspace UUID.
            depth: Maximum depth of the folder tree. Defaults to 1.
            root_view_id: Root view ID for subfolder retrieval.

        Raises:
            APIError: If the request fails.
        """
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
        """Retrieve all databases in a workspace.

        Args:
            workspace_id: The workspace UUID.

        Raises:
            APIError: If the request fails.
        """
        body = self._request(
            "GET",
            f"/api/workspace/{workspace_id}/database",
        )
        response = DatabasesResponse(**body)
        return response.data

    # ------------------------------------------------------------------
    # Database Fields
    # ------------------------------------------------------------------

    def get_database_fields(
        self,
        workspace_id: str,
        database_id: str,
    ) -> list[DatabaseField]:
        """Retrieve all fields in a database.

        Args:
            workspace_id: The workspace UUID.
            database_id: The database UUID.

        Raises:
            APIError: If the request fails.
        """
        body = self._request(
            "GET",
            f"/api/workspace/{workspace_id}/database/{database_id}/fields",
        )
        response = DatabaseFieldsResponse(**body)
        return response.data

    # ------------------------------------------------------------------
    # Database Rows
    # ------------------------------------------------------------------

    def get_database_row_ids(
        self,
        workspace_id: str,
        database_id: str,
    ) -> list[DatabaseRow]:
        """Retrieve all row IDs in a database.

        Args:
            workspace_id: The workspace UUID.
            database_id: The database UUID.

        Raises:
            APIError: If the request fails.
        """
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
        cells: dict[str, Any] | None = None,
        document: str | None = None,
    ) -> str:
        """Create a new row in a database.

        Args:
            workspace_id: The workspace UUID.
            database_id: The database UUID.
            cells: Cell values keyed by field_id or field_name.
            document: Optional markdown document content for the row.

        Returns:
            The UUID of the newly created row.

        Raises:
            APIError: If the request fails.
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
        response = ApiResponse(**body)
        row_id: str = body.get("data", "")
        return row_id

    def upsert_database_row(
        self,
        workspace_id: str,
        database_id: str,
        pre_hash: str,
        cells: dict[str, Any] | None = None,
        document: str | None = None,
    ) -> str:
        """Update or insert a row in a database (upsert).

        The row is identified by a hash of `pre_hash`. If the row exists it is
        updated; otherwise a new row is created.

        Args:
            workspace_id: The workspace UUID.
            database_id: The database UUID.
            pre_hash: String used to compute the row's unique hash.
            cells: Cell values keyed by field_id or field_name.
            document: Optional markdown document content for the row.

        Returns:
            The UUID of the created or updated row.

        Raises:
            APIError: If the request fails.
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
        row_id: str = body.get("data", "")
        return row_id

    # ------------------------------------------------------------------
    # Database Row Updates
    # ------------------------------------------------------------------

    def get_database_row_ids_updated(
        self,
        workspace_id: str,
        database_id: str,
        after: datetime | str | None = None,
    ) -> list[DatabaseRowUpdated]:
        """Retrieve row IDs that have been updated after a given timestamp.

        Args:
            workspace_id: The workspace UUID.
            database_id: The database UUID.
            after: ISO 8601 datetime or string to filter rows updated after.

        Raises:
            APIError: If the request fails.
        """
        params: dict[str, Any] = {}
        if after is not None:
            if isinstance(after, datetime):
                params["after"] = after.isoformat()
            else:
                params["after"] = after

        body = self._request(
            "GET",
            f"/api/workspace/{workspace_id}/database/{database_id}/row/updated",
            params=params,
        )
        response = DatabaseRowsUpdatedResponse(**body)
        return response.data

    # ------------------------------------------------------------------
    # Database Row Details
    # ------------------------------------------------------------------

    def get_database_row_details(
        self,
        workspace_id: str,
        database_id: str,
        row_ids: list[str],
        with_doc: bool | None = None,
    ) -> list[DatabaseRowDetail]:
        """Retrieve detailed information for specific database rows.

        Args:
            workspace_id: The workspace UUID.
            database_id: The database UUID.
            row_ids: List of row UUIDs to retrieve.
            with_doc: Include document content for each row.

        Raises:
            APIError: If the request fails.
            ValidationError: If no row IDs are provided.
        """
        if not row_ids:
            raise ValidationError("At least one row ID is required.")

        params: dict[str, Any] = {
            "ids": ",".join(row_ids),
        }
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

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
