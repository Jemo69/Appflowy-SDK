# Getting Started

## Installation

### From PyPI

```bash
pip install appflowysdk
```

### From source

```bash
git clone https://github.com/your-org/appflowysdk.git
cd appflowysdk
pip install -e .
```

## Requirements

- Python 3.12+
- Dependencies: `httpx`, `pydantic`

## Basic Usage

```python
from appflowysdk import AppFlowy

# Create a client with credentials
client = AppFlowy(
    email="user@example.com",
    password="your-password",
    base_url="https://beta.appflowy.cloud",
)

# Login and get token
token = client.login()
print(f"Token expires in {token.expires_in} seconds")

# List workspaces
workspaces = client.get_workspaces()
for ws in workspaces:
    print(f"Workspace: {ws.workspace_name} ({ws.workspace_id})")

# Always close the client when done
client.close()
```

## Using as Context Manager

```python
from appflowysdk import AppFlowy

with AppFlowy(email="user@example.com", password="your-password") as client:
    token = client.login()
    workspaces = client.get_workspaces()
    # client.close() is called automatically
```

## Custom Base URL

If you're running a self-hosted AppFlowy Cloud instance:

```python
client = AppFlowy(
    email="user@example.com",
    password="your-password",
    base_url="https://my-appflowy-instance.com",
)
```

## Document Workflows

```python
from appflowysdk import AppFlowy

workspace_id = "workspace-uuid"
parent_view_id = "parent-view-uuid"

with AppFlowy(email="user@example.com", password="your-password") as client:
    client.login()
    page = client.create_page(workspace_id, parent_view_id, name="My Page")
    note = client.create_quick_note(workspace_id, "Idea", "Draft text")
    results = client.search_documents(workspace_id, "meeting notes")
```

## Next Steps

- Learn about [Authentication](authentication.md) flows
- Explore [Workspaces](workspaces.md), [Databases](databases.md), and [Documents](documents.md)
- Understand [Error Handling](errors.md)
