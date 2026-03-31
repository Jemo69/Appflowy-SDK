# Error Handling

The SDK provides a structured exception hierarchy for precise error handling.

## Exception Hierarchy

```
AppFlowyError (base)
  ├── AuthenticationError
  │   ├── LoginError
  │   └── RefreshTokenError
  ├── APIError
  │   └── NotFoundError
  ├── ValidationError
  └── NetworkError
```

## Exception Classes

### AppFlowyError

Base exception for all SDK errors.

```python
class AppFlowyError(Exception):
    message: str          # Human-readable error message
    status_code: int | None  # HTTP status code (if applicable)
    body: Any             # Raw response body (if applicable)
```

### LoginError

Raised when password authentication fails.

```python
from src.exception import LoginError

try:
    client.login()
except LoginError as e:
    print(f"Login failed: {e.message}")
    print(f"HTTP status: {e.status_code}")
```

### RefreshTokenError

Raised when token refresh fails (expired refresh token, invalid token, etc.).

```python
from src.exception import RefreshTokenError

try:
    client.refresh_token()
except RefreshTokenError as e:
    print(f"Refresh failed: {e.message}")
    # Need to re-authenticate with login()
```

### APIError

Raised when any API request returns a non-2xx status code.

```python
from src.exception import APIError

try:
    workspaces = client.get_workspaces()
except APIError as e:
    print(f"API error: {e.message}")
    print(f"Status: {e.status_code}")
    print(f"Response: {e.body}")
```

### NotFoundError

Subclass of `APIError` for 404 responses.

```python
from src.exception import NotFoundError

try:
    folder = client.get_workspace_folder("invalid-uuid")
except NotFoundError as e:
    print("Workspace not found")
```

### ValidationError

Raised when SDK-side validation fails (before making a request).

```python
from src.exception import ValidationError

try:
    # Empty row_ids list is invalid
    client.get_database_row_details("ws", "db", row_ids=[])
except ValidationError as e:
    print(f"Validation error: {e.message}")
```

### NetworkError

Raised when a network-level error occurs (connection failure, timeout, DNS error).

```python
from src.exception import NetworkError

try:
    client.get_workspaces()
except NetworkError as e:
    print(f"Network error: {e.message}")
```

## Catching All SDK Errors

Use the base `AppFlowyError` to catch any SDK error:

```python
from src.exception import AppFlowyError

try:
    client.login()
    workspaces = client.get_workspaces()
except AppFlowyError as e:
    print(f"SDK error ({e.__class__.__name__}): {e.message}")
```

## Error Attributes

All exceptions carry useful context:

```python
try:
    client.login()
except AppFlowyError as e:
    print(e.message)      # "Login failed: Invalid credentials"
    print(e.status_code)  # 401
    print(e.body)         # {"code": 401, "message": "Invalid credentials"}
```
