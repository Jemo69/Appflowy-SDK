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
from appflowy import AppFlowy

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
from appflowy import AppFlowy

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

## Next Steps

- Learn about [Authentication](authentication.md) flows
- Explore [Workspaces](workspaces.md) and [Databases](databases.md)
- Understand [Error Handling](errors.md)
