# Databases

Databases in AppFlowy are structured data stores with fields (columns) and rows. The SDK provides full CRUD operations for databases, fields, and rows.

## List Databases

Get all databases in a workspace.

```python
databases = client.get_databases("workspace-uuid")

for db in databases:
    print(f"Database: {db.id}")
    for view in db.views:
        print(f"  View: {view.name} ({view.layout})")
```

### Database Model

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | UUID of the database |
| `views` | `list[FolderViewMin]` | Associated views |

## Get Database Fields

Retrieve the schema (fields/columns) of a database.

```python
fields = client.get_database_fields("workspace-uuid", "database-uuid")

for field in fields:
    print(f"Field: {field.name} ({field.field_type})")
    print(f"  Primary: {field.is_primary}")
    print(f"  ID: {field.id}")
```

### DatabaseField Model

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | UUID of the field |
| `name` | `str \| None` | Field display name |
| `field_type` | `str \| None` | Type identifier (e.g., "text", "number") |
| `type_option` | `dict \| None` | Type-specific configuration |
| `is_primary` | `bool \| None` | Whether this is the primary field |

## List Row IDs

Get all row identifiers in a database.

```python
rows = client.get_database_row_ids("workspace-uuid", "database-uuid")

for row in rows:
    print(f"Row ID: {row.id}")
```

## Get Row Details

Retrieve detailed information for specific rows, including cell values and optional document content.

```python
details = client.get_database_row_details(
    workspace_id="workspace-uuid",
    database_id="database-uuid",
    row_ids=["row-uuid-1", "row-uuid-2"],
    with_doc=True,
)

for detail in details:
    print(f"Row: {detail.id}")
    print(f"Cells: {detail.cells}")
    if detail.has_doc:
        print(f"Document: {detail.doc}")
```

### DatabaseRowDetail Model

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | UUID of the row |
| `cells` | `dict[str, Any]` | Cell values keyed by field ID |
| `has_doc` | `bool \| None` | Whether the row has an attached document |
| `doc` | `str \| None` | Document content (markdown), if `with_doc=True` |

## Create a Row

Add a new row to a database with cell values.

```python
row_id = client.create_database_row(
    workspace_id="workspace-uuid",
    database_id="database-uuid",
    cells={
        "field-uuid-1": "Task title",
        "field-uuid-2": "2025-01-15",
        "field-uuid-3": True,
    },
    document="# Task Notes\nDetailed description here.",
)

print(f"Created row: {row_id}")
```

### Cell Values

Cell keys can be either field UUIDs or field names. The server will attempt to convert values to the appropriate field type.

```python
# Using field names
cells = {
    "Title": "My Task",
    "Status": "In Progress",
    "Priority": 1,
}

# Using field UUIDs
cells = {
    "a1b2c3d4-uuid": "My Task",
    "e5f6g7h8-uuid": "In Progress",
}
```

## Upsert a Row

Update an existing row or create a new one based on a hash key.

```python
row_id = client.upsert_database_row(
    workspace_id="workspace-uuid",
    database_id="database-uuid",
    pre_hash="unique-identifier-string",
    cells={
        "Title": "Updated Task",
        "Status": "Done",
    },
)

print(f"Upserted row: {row_id}")
```

The `pre_hash` is used to compute a unique hash for the row. If a row with that hash already exists, it is updated. Otherwise, a new row is created.

## Get Updated Rows

Retrieve rows that have been modified after a specific timestamp.

```python
from datetime import datetime, timezone

updated = client.get_database_row_ids_updated(
    workspace_id="workspace-uuid",
    database_id="database-uuid",
    after=datetime(2025, 1, 1, tzinfo=timezone.utc),
)

for row in updated:
    print(f"Row {row.id} updated at {row.updated_at}")
```

You can also pass the timestamp as an ISO 8601 string:

```python
updated = client.get_database_row_ids_updated(
    workspace_id="workspace-uuid",
    database_id="database-uuid",
    after="2025-01-01T00:00:00Z",
)
```

### DatabaseRowUpdated Model

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | UUID of the row |
| `updated_at` | `datetime \| None` | Last update timestamp |
