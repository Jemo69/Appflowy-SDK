# Models Reference

All models are defined in `src/models.py` using Pydantic v2.

## Enums

### IconType

| Value | Name |
|-------|------|
| 0 | `EMOJI` |
| 1 | `URL` |
| 2 | `ICON` |

### ViewLayout

| Value | Name |
|-------|------|
| 0 | `DOCUMENT` |
| 1 | `GRID` |
| 2 | `BOARD` |
| 3 | `CALENDAR` |
| 4 | `CHAT` |

### Role

| Value | Name | Description |
|-------|------|-------------|
| 1 | `OWNER` | Full control over the workspace |
| 2 | `MEMBER` | Regular access |
| 3 | `GUEST` | Limited access |

## Token Models

### Token

Internal token storage model.

```python
class Token(BaseModel):
    access_token: str = ""
    refresh_token: str = ""
    expires_in: int = 0
```

### TokenResponse

Server response from authentication endpoints.

```python
class TokenResponse(BaseModel):
    access_token: str
    token_type: str | None = None
    expires_in: int
    expires_at: int | None = None
    refresh_token: str
    user: dict[str, Any] | None = None
    provider_access_token: str | None = None
    provider_refresh_token: str | None = None
```

## Workspace Models

### Workspace

```python
class Workspace(BaseModel):
    workspace_id: str
    database_storage_id: str | None = None
    owner_uid: int | None = None
    owner_name: str | None = None
    owner_email: str | None = None
    workspace_type: int | None = None
    workspace_name: str | None = None
    created_at: datetime | None = None
    icon: str | None = None
    member_count: int | None = None
    role: Role | None = None
```

## View / Folder Models

### ViewIcon

```python
class ViewIcon(BaseModel):
    ty: IconType | None = None
    value: str | None = None
```

### FolderViewMin

Minimal view representation used in database listings.

```python
class FolderViewMin(BaseModel):
    view_id: str
    name: str
    icon: ViewIcon | None = None
    layout: ViewLayout | None = None
```

### FolderView

Full view with recursive children.

```python
class FolderView(BaseModel):
    view_id: str
    name: str
    icon: ViewIcon | None = None
    is_space: bool | None = None
    is_private: bool | None = None
    is_published: bool | None = None
    layout: ViewLayout | None = None
    created_at: datetime | None = None
    last_edited_time: datetime | None = None
    is_locked: bool | None = None
    extra: dict[str, Any] | None = None
    children: list[FolderView] = Field(default_factory=list)
```

## Database Models

### Database

```python
class Database(BaseModel):
    id: str
    views: list[FolderViewMin] = Field(default_factory=list)
```

### DatabaseField

```python
class DatabaseField(BaseModel):
    id: str
    name: str | None = None
    field_type: str | None = None
    type_option: dict[str, Any] | None = None
    is_primary: bool | None = None
```

### DatabaseRow

```python
class DatabaseRow(BaseModel):
    id: str
```

### DatabaseRowUpdated

```python
class DatabaseRowUpdated(BaseModel):
    id: str
    updated_at: datetime | None = None
```

### DatabaseRowDetail

```python
class DatabaseRowDetail(BaseModel):
    id: str
    cells: dict[str, Any] = Field(default_factory=dict)
    has_doc: bool | None = None
    doc: str | None = None
```

## Request Models

### AddDatabaseRowRequest

```python
class AddDatabaseRowRequest(BaseModel):
    cells: dict[str, Any] = Field(default_factory=dict)
    document: str | None = None
```

### UpsertDatabaseRowRequest

```python
class UpsertDatabaseRowRequest(BaseModel):
    pre_hash: str
    cells: dict[str, Any] = Field(default_factory=dict)
    document: str | None = None
```

## Generic API Response

### ApiResponse

Base response wrapper used by the API.

```python
class ApiResponse(BaseModel):
    code: int
    message: str
```

## Typed Response Models

Each endpoint has a corresponding typed response model:

| Model | `data` Type |
|-------|-------------|
| `WorkspacesResponse` | `list[Workspace]` |
| `FolderResponse` | `FolderView \| None` |
| `DatabasesResponse` | `list[Database]` |
| `DatabaseFieldsResponse` | `list[DatabaseField]` |
| `DatabaseRowsResponse` | `list[DatabaseRow]` |
| `DatabaseRowsUpdatedResponse` | `list[DatabaseRowUpdated]` |
| `DatabaseRowDetailsResponse` | `list[DatabaseRowDetail]` |
| `CreateDatabaseRowResponse` | `str \| None` |
| `UpsertDatabaseRowResponse` | `str \| None` |
