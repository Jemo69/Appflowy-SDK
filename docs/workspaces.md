# Workspaces

Workspaces are the top-level organizational units in AppFlowy Cloud. Each workspace contains folders, pages, and databases.

## List Workspaces

Retrieve all workspaces accessible to the authenticated user.

```python
workspaces = client.get_workspaces()

for ws in workspaces:
    print(f"Name: {ws.workspace_name}")
    print(f"ID: {ws.workspace_id}")
    print(f"Owner: {ws.owner_name}")
```

### With Member Count and Role

```python
workspaces = client.get_workspaces(
    include_member_count=True,
    include_role=True,
)

for ws in workspaces:
    print(f"{ws.workspace_name}: {ws.member_count} members, role={ws.role}")
```

### Workspace Model

| Field | Type | Description |
|-------|------|-------------|
| `workspace_id` | `str` | UUID of the workspace |
| `workspace_name` | `str \| None` | Human-readable name |
| `database_storage_id` | `str \| None` | UUID of the database storage |
| `owner_uid` | `int \| None` | Numeric owner identifier |
| `owner_name` | `str \| None` | Owner's display name |
| `owner_email` | `str \| None` | Owner's email address |
| `workspace_type` | `int \| None` | Workspace type identifier |
| `created_at` | `datetime \| None` | Creation timestamp |
| `icon` | `str \| None` | Workspace icon |
| `member_count` | `int \| None` | Number of members (if requested) |
| `role` | `Role \| None` | Current user's role (if requested) |

## Get Workspace Folder

Retrieve the folder structure (page tree) of a workspace.

```python
folder = client.get_workspace_folder("workspace-uuid")

print(f"Root: {folder.name} ({folder.view_id})")
for child in folder.children:
    print(f"  - {child.name} ({child.layout})")
```

### Controlling Depth

By default, only the immediate children are returned. Increase `depth` for deeper trees.

```python
# Get 3 levels deep
folder = client.get_workspace_folder("workspace-uuid", depth=3)

def print_tree(view, indent=0):
    print("  " * indent + f"- {view.name}")
    for child in view.children:
        print_tree(child, indent + 1)

print_tree(folder)
```

### Subfolder Retrieval

Pass a `root_view_id` to get a specific subfolder instead of the workspace root.

```python
subfolder = client.get_workspace_folder(
    "workspace-uuid",
    root_view_id="some-page-uuid",
)
```

### FolderView Model

| Field | Type | Description |
|-------|------|-------------|
| `view_id` | `str` | UUID of the view/page |
| `name` | `str` | Page name |
| `icon` | `ViewIcon \| None` | Page icon |
| `is_space` | `bool \| None` | Whether the page is a space |
| `is_private` | `bool \| None` | Whether the space is private |
| `is_published` | `bool \| None` | Whether the page is published |
| `layout` | `ViewLayout \| None` | Page layout type |
| `created_at` | `datetime \| None` | Creation timestamp |
| `last_edited_time` | `datetime \| None` | Last edit timestamp |
| `is_locked` | `bool \| None` | Whether the page is locked |
| `extra` | `dict \| None` | Additional metadata |
| `children` | `list[FolderView]` | Child views |

### ViewLayout Enum

| Value | Name | Description |
|-------|------|-------------|
| 0 | `DOCUMENT` | Text document |
| 1 | `GRID` | Spreadsheet/grid view |
| 2 | `BOARD` | Kanban board |
| 3 | `CALENDAR` | Calendar view |
| 4 | `CHAT` | Chat view |
