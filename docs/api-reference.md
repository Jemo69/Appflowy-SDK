# API Reference

Complete reference for all SDK methods and their corresponding REST endpoints.

## Authentication

### login()

Authenticate with email and password.

```python
token = client.login() -> TokenResponse
```

| | |
|---|---|
| **Endpoint** | `POST /gotrue/token?grant_type=password` |
| **Requires** | `email`, `password` set on client |
| **Returns** | `TokenResponse` |
| **Raises** | `LoginError`, `NetworkError` |

---

### refresh_token()

Refresh the access token using the stored refresh token.

```python
token = client.refresh_token() -> TokenResponse
```

| | |
|---|---|
| **Endpoint** | `POST /gotrue/token?grant_type=refresh_token` |
| **Requires** | Prior successful `login()` |
| **Returns** | `TokenResponse` |
| **Raises** | `RefreshTokenError`, `NetworkError` |

---

### oauth_redirect_token()

Exchange an OAuth authorization code for tokens.

```python
token = client.oauth_redirect_token(
    code: str,
    grant_type: str,
    client_id: str | None = None,
    client_secret: str | None = None,
    redirect_uri: str | None = None,
    code_verifier: str | None = None,
) -> TokenResponse
```

| | |
|---|---|
| **Endpoint** | `GET /web-api/oauth-redirect/token` |
| **Requires** | Valid OAuth `code` |
| **Returns** | `TokenResponse` |
| **Raises** | `APIError`, `NetworkError` |

---

## Workspaces

### get_workspaces()

List all workspaces for the authenticated user.

```python
workspaces = client.get_workspaces(
    include_member_count: bool | None = None,
    include_role: bool | None = None,
) -> list[Workspace]
```

| | |
|---|---|
| **Endpoint** | `GET /api/workspace` |
| **Auth** | Bearer token |
| **Returns** | `list[Workspace]` |
| **Raises** | `APIError` |

---

### get_workspace_folder()

Get the folder/page tree for a workspace.

```python
folder = client.get_workspace_folder(
    workspace_id: str,
    depth: int | None = None,
    root_view_id: str | None = None,
) -> FolderView
```

| | |
|---|---|
| **Endpoint** | `GET /api/workspace/{workspace_id}/folder` |
| **Auth** | Bearer token |
| **Returns** | `FolderView` |
| **Raises** | `APIError` |

---

## Databases

### get_databases()

List all databases in a workspace.

```python
databases = client.get_databases(workspace_id: str) -> list[Database]
```

| | |
|---|---|
| **Endpoint** | `GET /api/workspace/{workspace_id}/database` |
| **Auth** | Bearer token |
| **Returns** | `list[Database]` |
| **Raises** | `APIError` |

---

### get_database_fields()

Get the field schema of a database.

```python
fields = client.get_database_fields(
    workspace_id: str,
    database_id: str,
) -> list[DatabaseField]
```

| | |
|---|---|
| **Endpoint** | `GET /api/workspace/{workspace_id}/database/{database_id}/fields` |
| **Auth** | Bearer token |
| **Returns** | `list[DatabaseField]` |
| **Raises** | `APIError` |

---

## Database Rows

### get_database_row_ids()

List all row IDs in a database.

```python
rows = client.get_database_row_ids(
    workspace_id: str,
    database_id: str,
) -> list[DatabaseRow]
```

| | |
|---|---|
| **Endpoint** | `GET /api/workspace/{workspace_id}/database/{database_id}/row` |
| **Auth** | Bearer token |
| **Returns** | `list[DatabaseRow]` |
| **Raises** | `APIError` |

---

### create_database_row()

Create a new row in a database.

```python
row_id = client.create_database_row(
    workspace_id: str,
    database_id: str,
    cells: dict[str, Any] | None = None,
    document: str | None = None,
) -> str
```

| | |
|---|---|
| **Endpoint** | `POST /api/workspace/{workspace_id}/database/{database_id}/row` |
| **Auth** | Bearer token |
| **Returns** | `str` (new row UUID) |
| **Raises** | `APIError` |

---

### upsert_database_row()

Update or insert a row based on a hash key.

```python
row_id = client.upsert_database_row(
    workspace_id: str,
    database_id: str,
    pre_hash: str,
    cells: dict[str, Any] | None = None,
    document: str | None = None,
) -> str
```

| | |
|---|---|
| **Endpoint** | `PUT /api/workspace/{workspace_id}/database/{database_id}/row` |
| **Auth** | Bearer token |
| **Returns** | `str` (row UUID) |
| **Raises** | `APIError` |

---

### get_database_row_ids_updated()

Get rows updated after a timestamp.

```python
rows = client.get_database_row_ids_updated(
    workspace_id: str,
    database_id: str,
    after: datetime | str | None = None,
) -> list[DatabaseRowUpdated]
```

| | |
|---|---|
| **Endpoint** | `GET /api/workspace/{workspace_id}/database/{database_id}/row/updated` |
| **Auth** | Bearer token |
| **Returns** | `list[DatabaseRowUpdated]` |
| **Raises** | `APIError` |

---

### get_database_row_details()

Get detailed row data including cells and documents.

```python
details = client.get_database_row_details(
    workspace_id: str,
    database_id: str,
    row_ids: list[str],
    with_doc: bool | None = None,
) -> list[DatabaseRowDetail]
```

| | |
|---|---|
| **Endpoint** | `GET /api/workspace/{workspace_id}/database/{database_id}/row/detail` |
| **Auth** | Bearer token |
| **Returns** | `list[DatabaseRowDetail]` |
| **Raises** | `APIError`, `ValidationError` |
