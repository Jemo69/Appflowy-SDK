---
name: appflowy-sdk
description: Helps answer AppFlowy SDK API usage questions, including authentication, workspaces, databases, row operations, and error handling.
---

# AppFlowy SDK

Use this skill when the user asks how to use the AppFlowy Python SDK or needs help mapping an AppFlowy task to the correct SDK method.

## What To Cover

- Authentication with `login()`, `refresh_token()`, and `oauth_redirect_token()`
- Workspace discovery with `get_workspaces()` and `get_workspace_folder()`
- Database access with `get_databases()` and `get_database_fields()`
- Row workflows with `get_database_row_ids()`, `get_database_row_details()`, `create_database_row()`, `upsert_database_row()`, and `get_database_row_ids_updated()`
- Exception handling with `AppFlowyError`, `LoginError`, `RefreshTokenError`, `APIError`, `ValidationError`, and `NetworkError`

## Core Rules

1. Prefer the public package export: `from appflowysdk import AppFlowy`
2. Do not invent method names or parameters; use the documented API surface
3. Login first before authenticated calls
4. Include the minimal working example that matches the user’s task
5. Mention required IDs explicitly: `workspace_id`, `database_id`, `row_ids`

## Typical Flow

```python
from appflowysdk import AppFlowy

with AppFlowy(email="user@example.com", password="password") as client:
    token = client.login()
    workspaces = client.get_workspaces()
```

## Common Mappings

- “List my workspaces” -> `get_workspaces()`
- “Get the page tree” -> `get_workspace_folder(workspace_id, depth=...)`
- “List databases in a workspace” -> `get_databases(workspace_id)`
- “Inspect table fields” -> `get_database_fields(workspace_id, database_id)`
- “Fetch rows” -> `get_database_row_ids(workspace_id, database_id)`
- “Read row content” -> `get_database_row_details(workspace_id, database_id, row_ids, with_doc=True)`
- “Create a record” -> `create_database_row(workspace_id, database_id, cells=..., document=...)`
- “Upsert a record” -> `upsert_database_row(workspace_id, database_id, pre_hash, cells=..., document=...)`
- “Find updated rows” -> `get_database_row_ids_updated(workspace_id, database_id, after=...)`

## Response Style

- Keep answers short and practical
- Show the exact import and method call
- Include a note about required auth or IDs when relevant
- If the user asks for troubleshooting, mention the most likely exception type first

## Reference Notes

- `create_database_row()` returns the created row UUID as a string
- `upsert_database_row()` returns the created or updated row UUID as a string
- `get_database_row_details()` requires at least one row ID
- `get_database_row_ids_updated()` accepts a `datetime` or ISO 8601 string
- `get_workspaces()` can optionally include `include_member_count` and `include_role`
