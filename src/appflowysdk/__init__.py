"""Type-safe Python SDK for the AppFlowy Cloud REST API."""

from appflowysdk.client import AppFlowy
from appflowysdk.constants import BASE_URL
from appflowysdk.exceptions import (
    APIError,
    AppFlowyError,
    AuthenticationError,
    LoginError,
    NetworkError,
    NotFoundError,
    RefreshTokenError,
    ValidationError,
)
from appflowysdk.models import (
    AddDatabaseRowRequest,
    ApiResponse,
    Database,
    DatabaseField,
    DatabaseRow,
    DatabaseRowDetail,
    DatabaseRowUpdated,
    FolderView,
    FolderViewMin,
    IconType,
    Role,
    Token,
    TokenResponse,
    UpsertDatabaseRowRequest,
    ViewIcon,
    ViewLayout,
    Workspace,
)

__version__ = "0.1.0"

__all__ = [
    # Client
    "AppFlowy",
    # Constants
    "BASE_URL",
    # Exceptions
    "AppFlowyError",
    "AuthenticationError",
    "LoginError",
    "RefreshTokenError",
    "APIError",
    "NotFoundError",
    "ValidationError",
    "NetworkError",
    # Models
    "Token",
    "TokenResponse",
    "ApiResponse",
    "Workspace",
    "ViewIcon",
    "FolderViewMin",
    "FolderView",
    "Database",
    "DatabaseField",
    "DatabaseRow",
    "DatabaseRowDetail",
    "DatabaseRowUpdated",
    "AddDatabaseRowRequest",
    "UpsertDatabaseRowRequest",
    # Enums
    "IconType",
    "ViewLayout",
    "Role",
]
