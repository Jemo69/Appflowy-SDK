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

---

## Documents

### create_collab()

Create a document collab.

```python
client.create_collab(workspace_id: str, object_id: str, encoded_collab: str) -> None
```

| | |
|---|---|
| **Endpoint** | `POST /api/workspace/{workspace_id}/collab/{object_id}` |
| **Auth** | Bearer token |
| **Returns** | `None` |
| **Raises** | `APIError` |

---

### update_collab()

Update an existing collab.

```python
client.update_collab(workspace_id: str, object_id: str, encoded_collab: str) -> None
```

| | |
|---|---|
| **Endpoint** | `PUT /api/workspace/{workspace_id}/collab/{object_id}` |
| **Auth** | Bearer token |
| **Returns** | `None` |
| **Raises** | `APIError` |

---

### get_collab()

Get encoded collab data.

```python
collab = client.get_collab(workspace_id: str, object_id: str) -> CollabResponse
```

| | |
|---|---|
| **Endpoint** | `GET /api/workspace/{workspace_id}/collab/{object_id}` |
| **Auth** | Bearer token |
| **Returns** | `CollabResponse` |
| **Raises** | `APIError` |

---

### get_collab_json()

Get collab payload as JSON.

```python
collab = client.get_collab_json(workspace_id: str, object_id: str) -> CollabJsonResponse
```

| | |
|---|---|
| **Endpoint** | `GET /api/workspace/v1/{workspace_id}/collab/{object_id}/json` |
| **Auth** | Bearer token |
| **Returns** | `CollabJsonResponse` |
| **Raises** | `APIError` |

---

### batch_create_collab()

Create multiple collabs in one request.

```python
client.batch_create_collab(workspace_id: str, collabs: dict[str, str]) -> None
```

| | |
|---|---|
| **Endpoint** | `POST /api/workspace/{workspace_id}/batch/collab` |
| **Auth** | Bearer token |
| **Returns** | `None` |
| **Raises** | `APIError` |

---

### full_sync_collab()

Synchronize the full document state.

```python
content = client.full_sync_collab(workspace_id: str, object_id: str, doc_state: str) -> bytes
```

| | |
|---|---|
| **Endpoint** | `POST /api/workspace/v1/{workspace_id}/collab/{object_id}/full-sync` |
| **Auth** | Bearer token |
| **Returns** | `bytes` |
| **Raises** | `APIError` |

---

### web_update_collab()

Push an update from a web client.

```python
client.web_update_collab(workspace_id: str, object_id: str, update: str) -> None
```

| | |
|---|---|
| **Endpoint** | `POST /api/workspace/v1/{workspace_id}/collab/{object_id}/web-update` |
| **Auth** | Bearer token |
| **Returns** | `None` |
| **Raises** | `APIError` |

---

### create_page()

Create a new page view.

```python
page = client.create_page(
    workspace_id: str,
    parent_view_id: str,
    layout: ViewLayout = ViewLayout.DOCUMENT,
    name: str | None = None,
    page_data: dict[str, Any] | None = None,
) -> FolderView
```

| | |
|---|---|
| **Endpoint** | `POST /api/workspace/{workspace_id}/page-view` |
| **Auth** | Bearer token |
| **Returns** | `FolderView` |
| **Raises** | `APIError` |

---

### get_page()

Get page metadata and collab data.

```python
page = client.get_page(workspace_id: str, view_id: str) -> PageCollab
```

| | |
|---|---|
| **Endpoint** | `GET /api/workspace/{workspace_id}/page-view/{view_id}` |
| **Auth** | Bearer token |
| **Returns** | `PageCollab` |
| **Raises** | `APIError` |

---

### append_page_blocks()

Append blocks to a page.

```python
client.append_page_blocks(workspace_id: str, view_id: str, blocks: list[dict[str, Any]]) -> None
```

| | |
|---|---|
| **Endpoint** | `POST /api/workspace/{workspace_id}/page-view/{view_id}/append-block` |
| **Auth** | Bearer token |
| **Returns** | `None` |
| **Raises** | `APIError` |

---

### create_orphaned_view()

Create a page view without a parent.

```python
client.create_orphaned_view(
    workspace_id: str,
    layout: ViewLayout = ViewLayout.DOCUMENT,
    name: str | None = None,
) -> None
```

| | |
|---|---|
| **Endpoint** | `POST /api/workspace/{workspace_id}/orphaned-view` |
| **Auth** | Bearer token |
| **Returns** | `None` |
| **Raises** | `APIError` |

---

### duplicate_page()

Duplicate a page view.

```python
client.duplicate_page(workspace_id: str, view_id: str, parent_view_id: str | None = None) -> None
```

| | |
|---|---|
| **Endpoint** | `POST /api/workspace/{workspace_id}/page-view/{view_id}/duplicate` |
| **Auth** | Bearer token |
| **Returns** | `None` |
| **Raises** | `APIError` |

---

### create_quick_note()

Create a quick note.

```python
note = client.create_quick_note(workspace_id: str, title: str, content: str) -> QuickNote
```

| | |
|---|---|
| **Endpoint** | `POST /api/workspace/{workspace_id}/quick-note` |
| **Auth** | Bearer token |
| **Returns** | `QuickNote` |
| **Raises** | `APIError` |

---

### list_quick_notes()

List all quick notes.

```python
notes = client.list_quick_notes(workspace_id: str) -> QuickNotes
```

| | |
|---|---|
| **Endpoint** | `GET /api/workspace/{workspace_id}/quick-note` |
| **Auth** | Bearer token |
| **Returns** | `QuickNotes` |
| **Raises** | `APIError` |

---

### search_documents()

Search documents within a workspace.

```python
results = client.search_documents(workspace_id: str, query: str) -> list[SearchDocumentResponseItem]
```

| | |
|---|---|
| **Endpoint** | `GET /api/search/{workspace_id}` |
| **Auth** | Bearer token |
| **Returns** | `list[SearchDocumentResponseItem]` |
| **Raises** | `APIError` |

---

### publish_page()

Publish a page.

```python
client.publish_page(workspace_id: str, view_id: str) -> None
```

| | |
|---|---|
| **Endpoint** | `POST /api/workspace/{workspace_id}/page-view/{view_id}/publish` |
| **Auth** | Bearer token |
| **Returns** | `None` |
| **Raises** | `APIError` |

---

### unpublish_page()

Unpublish a page.

```python
client.unpublish_page(workspace_id: str, view_id: str) -> None
```

| | |
|---|---|
| **Endpoint** | `POST /api/workspace/{workspace_id}/page-view/{view_id}/unpublish` |
| **Auth** | Bearer token |
| **Returns** | `None` |
| **Raises** | `APIError` |

---

### import_zip()

Import a ZIP archive.

```python
client.import_zip(zip_content: bytes) -> None
```

| | |
|---|---|
| **Endpoint** | `POST /api/import` |
| **Auth** | Bearer token |
| **Returns** | `None` |
| **Raises** | `APIError` |

---

### create_import_task()

Create an import task.

```python
result = client.create_import_task(import_type: str, data: dict[str, Any]) -> CreateImportTaskResponse
```

| | |
|---|---|
| **Endpoint** | `POST /api/import/create` |
| **Auth** | Bearer token |
| **Returns** | `CreateImportTaskResponse` |
| **Raises** | `APIError` |
