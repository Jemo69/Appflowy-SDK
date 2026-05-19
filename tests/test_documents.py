import pytest
import respx
from httpx import Response
from appflowysdk import AppFlowy
from appflowysdk.models import ViewLayout

@respx.mock
def test_collab_endpoints():
    client = AppFlowy(email="test@example.com", password="password")
    workspace_id = "ws1"
    object_id = "obj1"

    # Test create_collab
    respx.post(f"https://beta.appflowy.cloud/api/workspace/{workspace_id}/collab/{object_id}").mock(return_value=Response(200, json={"code": 0, "message": "ok"}))
    client.create_collab(workspace_id, object_id, "encoded_data")

    # Test update_collab
    respx.put(f"https://beta.appflowy.cloud/api/workspace/{workspace_id}/collab/{object_id}").mock(return_value=Response(200, json={"code": 0, "message": "ok"}))
    client.update_collab(workspace_id, object_id, "updated_data")

    # Test get_collab
    respx.get(f"https://beta.appflowy.cloud/api/workspace/{workspace_id}/collab/{object_id}").mock(return_value=Response(200, json={"code": 0, "message": "ok", "data": {"encoded_collab": "encoded_data"}}))
    collab = client.get_collab(workspace_id, object_id)
    assert collab.encoded_collab == "encoded_data"

    # Test get_collab_json
    respx.get(f"https://beta.appflowy.cloud/api/workspace/v1/{workspace_id}/collab/{object_id}/json").mock(return_value=Response(200, json={"code": 0, "message": "ok", "data": {"payload": {"test": "data"}}}))
    collab_json = client.get_collab_json(workspace_id, object_id)
    assert collab_json.payload == {"test": "data"}

    # Test batch_create_collab
    respx.post(f"https://beta.appflowy.cloud/api/workspace/{workspace_id}/batch/collab").mock(return_value=Response(200, json={"code": 0, "message": "ok"}))
    client.batch_create_collab(workspace_id, {"obj1": "data1", "obj2": "data2"})

    # Test full_sync_collab
    respx.post(f"https://beta.appflowy.cloud/api/workspace/v1/{workspace_id}/collab/{object_id}/full-sync").mock(return_value=Response(200, content=b"binary_data"))
    sync_data = client.full_sync_collab(workspace_id, object_id, "doc_state")
    assert sync_data == b"binary_data"

    # Test web_update_collab
    respx.post(f"https://beta.appflowy.cloud/api/workspace/v1/{workspace_id}/collab/{object_id}/web-update").mock(return_value=Response(200, json={"code": 0, "message": "ok"}))
    client.web_update_collab(workspace_id, object_id, "web_update")

@respx.mock
def test_page_endpoints():
    client = AppFlowy(email="test@example.com", password="password")
    workspace_id = "ws1"

    # Test create_page
    respx.post(f"https://beta.appflowy.cloud/api/workspace/{workspace_id}/page-view").mock(return_value=Response(200, json={
        "code": 0,
        "message": "ok",
        "data": {"view_id": "v1", "name": "New Page", "layout": 0}
    }))
    page = client.create_page(workspace_id, "parent_v1", name="New Page")
    assert page.view_id == "v1"
    assert page.name == "New Page"

    # Test get_page
    view_id = "v1"
    respx.get(f"https://beta.appflowy.cloud/api/workspace/{workspace_id}/page-view/{view_id}").mock(return_value=Response(200, json={
        "code": 0,
        "message": "ok",
        "data": {
            "view": {"view_id": "v1", "name": "New Page", "layout": 0},
            "data": {"encoded_collab": "encoded_data"},
            "owner": {"uuid": "u1", "name": "User 1"}
        }
    }))
    page_collab = client.get_page(workspace_id, view_id)
    assert page_collab.view.view_id == "v1"
    assert page_collab.owner.name == "User 1"

    # Test append_page_blocks
    respx.post(f"https://beta.appflowy.cloud/api/workspace/{workspace_id}/page-view/{view_id}/append-block").mock(return_value=Response(200, json={"code": 0, "message": "ok"}))
    client.append_page_blocks(workspace_id, view_id, [{"ty": "text", "data": "hello"}])

    # Test create_orphaned_view
    respx.post(f"https://beta.appflowy.cloud/api/workspace/{workspace_id}/orphaned-view").mock(return_value=Response(200, json={"code": 0, "message": "ok"}))
    client.create_orphaned_view(workspace_id, name="Orphaned")

    # Test duplicate_page
    respx.post(f"https://beta.appflowy.cloud/api/workspace/{workspace_id}/page-view/{view_id}/duplicate").mock(return_value=Response(200, json={"code": 0, "message": "ok"}))
    client.duplicate_page(workspace_id, view_id)

@respx.mock
def test_quick_note_endpoints():
    client = AppFlowy(email="test@example.com", password="password")
    workspace_id = "ws1"

    # Test create_quick_note
    respx.post(f"https://beta.appflowy.cloud/api/workspace/{workspace_id}/quick-note").mock(return_value=Response(200, json={
        "code": 0,
        "message": "ok",
        "data": {
            "id": "qn1",
            "title": "Note 1",
            "content": "Content 1",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
    }))
    qn = client.create_quick_note(workspace_id, "Note 1", "Content 1")
    assert qn.id == "qn1"
    assert qn.title == "Note 1"

    # Test list_quick_notes
    respx.get(f"https://beta.appflowy.cloud/api/workspace/{workspace_id}/quick-note").mock(return_value=Response(200, json={
        "code": 0,
        "message": "ok",
        "data": {
            "items": [
                {
                    "id": "qn1",
                    "title": "Note 1",
                    "content": "Content 1",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z"
                }
            ]
        }
    }))
    qns = client.list_quick_notes(workspace_id)
    assert len(qns.items) == 1
    assert qns.items[0].id == "qn1"

@respx.mock
def test_search_endpoints():
    client = AppFlowy(email="test@example.com", password="password")
    workspace_id = "ws1"

    respx.get(f"https://beta.appflowy.cloud/api/search/{workspace_id}").mock(return_value=Response(200, json={
        "code": 0,
        "message": "ok",
        "data": [{"view_id": "v1", "name": "Page 1", "snippet": "some content"}]
    }))
    results = client.search_documents(workspace_id, "query")
    assert len(results) == 1
    assert results[0].name == "Page 1"

@respx.mock
def test_publish_endpoints():
    client = AppFlowy(email="test@example.com", password="password")
    workspace_id = "ws1"
    view_id = "v1"

    respx.post(f"https://beta.appflowy.cloud/api/workspace/{workspace_id}/page-view/{view_id}/publish").mock(return_value=Response(200, json={"code": 0, "message": "ok"}))
    client.publish_page(workspace_id, view_id)

    respx.post(f"https://beta.appflowy.cloud/api/workspace/{workspace_id}/page-view/{view_id}/unpublish").mock(return_value=Response(200, json={"code": 0, "message": "ok"}))
    client.unpublish_page(workspace_id, view_id)

@respx.mock
def test_import_endpoints():
    client = AppFlowy(email="test@example.com", password="password")

    # Test import_zip
    respx.post("https://beta.appflowy.cloud/api/import").mock(return_value=Response(200, json={"code": 0, "message": "ok"}))
    client.import_zip(b"zip_data")

    # Test create_import_task
    respx.post("https://beta.appflowy.cloud/api/import/create").mock(return_value=Response(200, json={
        "code": 0,
        "message": "ok",
        "data": {"task_id": "t1"}
    }))
    task = client.create_import_task("notion", {"key": "value"})
    assert task.task_id == "t1"
