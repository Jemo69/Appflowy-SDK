# Authentication

The AppFlowy SDK supports two authentication methods: password-based login and OAuth 2.0.

## Password Authentication

The most common way to authenticate. Use your AppFlowy Cloud email and password.

```python
from appflowy import AppFlowy

client = AppFlowy(email="user@example.com", password="your-password")
token = client.login()

# token.access_token  - JWT for API requests
# token.refresh_token - long-lived token for refreshing
# token.expires_in    - seconds until access token expires
```

### TokenResponse Fields

| Field | Type | Description |
|-------|------|-------------|
| `access_token` | `str` | JWT bearer token for API requests |
| `refresh_token` | `str` | Long-lived token for obtaining new access tokens |
| `expires_in` | `int` | Seconds until the access token expires |
| `expires_at` | `int \| None` | Unix timestamp when the token expires |
| `token_type` | `str \| None` | Always `"Bearer"` |
| `user` | `dict \| None` | Authenticated user information |
| `provider_access_token` | `str \| None` | OAuth provider access token |
| `provider_refresh_token` | `str \| None` | OAuth provider refresh token |

## Refreshing Tokens

Access tokens expire. Use `refresh_token()` to get a new one without re-entering credentials.

```python
# After initial login
token = client.login()

# Later, when the access token expires
new_token = client.refresh_token()
```

### Automatic Token Storage

The SDK automatically stores tokens after login or refresh. The stored token is used for all subsequent authenticated API calls.

```python
# Token is stored internally after login
client.login()

# All subsequent calls use the stored token automatically
workspaces = client.get_workspaces()
```

## OAuth 2.0 Authentication

For third-party integrations using AppFlowy OAuth.

```python
from appflowy import AppFlowy

client = AppFlowy()

token = client.oauth_redirect_token(
    code="authorization_code_from_redirect",
    grant_type="authorization_code",
    client_id="your-client-id",
    client_secret="your-client-secret",
    redirect_uri="https://your-app.com/callback",
)
```

### OAuth Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `code` | Yes | Authorization code from the OAuth redirect |
| `grant_type` | Yes | OAuth 2.0 grant type |
| `client_id` | No | Your application's client ID |
| `client_secret` | No | Client secret (for confidential clients) |
| `redirect_uri` | No | The redirect URI used in the auth request |
| `code_verifier` | No | PKCE code verifier for public clients |

## Error Handling

All authentication methods raise typed exceptions on failure.

```python
from src.exception import LoginError, RefreshTokenError

try:
    client.login()
except LoginError as e:
    print(f"Login failed: {e.message}")
    print(f"Status code: {e.status_code}")

try:
    client.refresh_token()
except RefreshTokenError as e:
    print(f"Token refresh failed: {e.message}")
    # User needs to login again
```

See [Error Handling](errors.md) for the complete exception hierarchy.
