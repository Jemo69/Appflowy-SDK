# Documents

The SDK now includes helpers for AppFlowy document workflows: collabs, pages, quick notes, search, publishing, and imports.

## Collabs

Use collab helpers when you need direct document state access.

```python
workspace_id = "workspace-uuid"
object_id = "object-uuid"
encoded_collab = "encoded-collab"
doc_state = "doc-state"
update = "web-update"

client.create_collab(workspace_id, object_id, encoded_collab)
client.update_collab(workspace_id, object_id, encoded_collab)
collab = client.get_collab(workspace_id, object_id)
collab_json = client.get_collab_json(workspace_id, object_id)
client.batch_create_collab(workspace_id, {"object-id": "encoded"})
client.full_sync_collab(workspace_id, object_id, doc_state)
client.web_update_collab(workspace_id, object_id, update)
```

## Pages & Views

```python
parent_view_id = "parent-view-uuid"
blocks = [{"ty": "text", "data": "Hello"}]

page = client.create_page(workspace_id, parent_view_id, name="My Page")
page_data = client.get_page(workspace_id, page.view_id)
client.append_page_blocks(workspace_id, page.view_id, blocks)
client.create_orphaned_view(workspace_id, name="Untitled")
client.duplicate_page(workspace_id, page.view_id)
```

## Quick Notes

```python
note = client.create_quick_note(workspace_id, "Idea", "Draft text")
notes = client.list_quick_notes(workspace_id)
```

## Search

```python
results = client.search_documents(workspace_id, "meeting notes")
```

## Publishing

```python
client.publish_page(workspace_id, page.view_id)
client.unpublish_page(workspace_id, page.view_id)
```

## Import

```python
zip_bytes = b"..."

client.import_zip(zip_bytes)
client.create_import_task("notion", {"source": "export"})
```
