# AppFlowy SDK

Type-safe Python SDK for the [AppFlowy Cloud REST API](https://beta.appflowy.cloud).

## Installation

```bash
pip install appflowysdk 
## or
uv add appflowysdk
```

## Quick Start

```python
from appflowy import AppFlowy

with AppFlowy(email="user@example.com", password="password") as client:
    # Authenticate
    token = client.login()
    print(f"Logged in, token expires in {token.expires_in}s")

    # List workspaces
    workspaces = client.get_workspaces(include_member_count=True)
    for ws in workspaces:
        print(f"{ws.workspace_name} ({ws.workspace_id})")

    # Get folder structure
    folder = client.get_workspace_folder(workspaces[0].workspace_id)

    # List databases
    databases = client.get_databases(workspaces[0].workspace_id)

    # Get database fields
    fields = client.get_database_fields(
        workspaces[0].workspace_id, databases[0].id
    )

    # Get row IDs
    rows = client.get_database_row_ids(
        workspaces[0].workspace_id, databases[0].id
    )

    # Get row details
    if rows:
        details = client.get_database_row_details(
            workspaces[0].workspace_id,
            databases[0].id,
            [rows[0].id],
            with_doc=True,
        )

    # Create a row
    row_id = client.create_database_row(
        workspaces[0].workspace_id,
        databases[0].id,
        cells={"field_id": "value"},
    )

    # Upsert a row
    row_id = client.upsert_database_row(
        workspaces[0].workspace_id,
        databases[0].id,
        pre_hash="unique-key",
        cells={"field_id": "value"},
    )
```

## OAuth

```python
client = AppFlowy()
token = client.oauth_redirect_token(
    code="auth_code_from_redirect",
    grant_type="authorization_code",
)
```

## Error Handling

All SDK errors inherit from `AppFlowyError`:

```python
from src.exception import (
    AppFlowyError,
    LoginError,
    RefreshTokenError,
    APIError,
    ValidationError,
    NetworkError,
)
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `login()` | `POST /gotrue/token?grant_type=password` | Password auth |
| `refresh_token()` | `POST /gotrue/token?grant_type=refresh_token` | Refresh token |
| `oauth_redirect_token()` | `GET /web-api/oauth-redirect/token` | OAuth token exchange |
| `get_workspaces()` | `GET /api/workspace` | List workspaces |
| `get_workspace_folder()` | `GET /api/workspace/{id}/folder` | Get folder tree |
| `get_databases()` | `GET /api/workspace/{id}/database` | List databases |
| `get_database_fields()` | `GET /api/workspace/{id}/database/{id}/fields` | List fields |
| `get_database_row_ids()` | `GET /api/workspace/{id}/database/{id}/row` | List row IDs |
| `create_database_row()` | `POST /api/workspace/{id}/database/{id}/row` | Create row |
| `upsert_database_row()` | `PUT /api/workspace/{id}/database/{id}/row` | Upsert row |
| `get_database_row_ids_updated()` | `GET /api/workspace/{id}/database/{id}/row/updated` | Updated rows |
| `get_database_row_details()` | `GET /api/workspace/{id}/database/{id}/row/detail` | Row details |
