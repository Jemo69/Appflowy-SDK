"""Pydantic models and enums for the AppFlowy Cloud API."""

from __future__ import annotations

from datetime import datetime
from enum import Enum, IntEnum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class IconType(IntEnum):
    EMOJI = 0
    URL = 1
    ICON = 2


class ViewLayout(IntEnum):
    DOCUMENT = 0
    GRID = 1
    BOARD = 2
    CALENDAR = 3
    CHAT = 4


class Role(str, Enum):
    """Workspace member role.

    AppFlowy Cloud's API returns the role as a string ("Owner", "Member",
    "Guest"). Older releases used integers (1, 2, 3), so ``_missing_``
    accepts both forms for backward compatibility.
    """

    OWNER = "Owner"
    MEMBER = "Member"
    GUEST = "Guest"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, int):
            return {1: cls.OWNER, 2: cls.MEMBER, 3: cls.GUEST}.get(value)
        if isinstance(value, str):
            lookup = {
                "1": cls.OWNER, "2": cls.MEMBER, "3": cls.GUEST,
                "owner": cls.OWNER, "member": cls.MEMBER, "guest": cls.GUEST,
            }
            return lookup.get(value.lower())
        return None


# ---------------------------------------------------------------------------
# Token models
# ---------------------------------------------------------------------------


class Token(BaseModel):
    """Internal token storage."""

    access_token: str = ""
    refresh_token: str = ""
    expires_in: int = 0


class TokenResponse(BaseModel):
    """Server response from authentication endpoints."""

    access_token: str
    token_type: str | None = None
    expires_in: int
    expires_at: int | None = None
    refresh_token: str
    user: dict[str, Any] | None = None
    provider_access_token: str | None = None
    provider_refresh_token: str | None = None


# ---------------------------------------------------------------------------
# Generic API response
# ---------------------------------------------------------------------------


class ApiResponse(BaseModel):
    code: int
    message: str


# ---------------------------------------------------------------------------
# Workspace & User models
# ---------------------------------------------------------------------------


class User(BaseModel):
    uuid: str
    name: str
    avatar_url: str | None = None


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


# ---------------------------------------------------------------------------
# View / Folder models
# ---------------------------------------------------------------------------


class ViewIcon(BaseModel):
    ty: IconType | None = None
    value: str | None = None


class FolderViewMin(BaseModel):
    view_id: str
    name: str
    icon: ViewIcon | None = None
    layout: ViewLayout | None = None


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


# ---------------------------------------------------------------------------
# Database models
# ---------------------------------------------------------------------------


class Database(BaseModel):
    id: str
    views: list[FolderViewMin] = Field(default_factory=list)


class DatabaseField(BaseModel):
    id: str
    name: str | None = None
    field_type: str | None = None
    type_option: dict[str, Any] | None = None
    is_primary: bool | None = None


class DatabaseRow(BaseModel):
    id: str


class DatabaseRowUpdated(BaseModel):
    id: str
    updated_at: datetime | None = None


class DatabaseRowDetail(BaseModel):
    id: str
    cells: dict[str, Any] = Field(default_factory=dict)
    has_doc: bool | None = None
    doc: str | None = None


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------


class AddDatabaseRowRequest(BaseModel):
    cells: dict[str, Any] = Field(default_factory=dict)
    document: str | None = None


class UpsertDatabaseRowRequest(BaseModel):
    pre_hash: str
    cells: dict[str, Any] = Field(default_factory=dict)
    document: str | None = None


# ---------------------------------------------------------------------------
# Typed API response wrappers
# ---------------------------------------------------------------------------


class WorkspacesResponse(BaseModel):
    code: int
    message: str
    data: list[Workspace] = Field(default_factory=list)


class FolderResponse(BaseModel):
    code: int
    message: str
    data: FolderView | None = None


class DatabasesResponse(BaseModel):
    code: int
    message: str
    data: list[Database] = Field(default_factory=list)


class DatabaseFieldsResponse(BaseModel):
    code: int
    message: str
    data: list[DatabaseField] = Field(default_factory=list)


class DatabaseRowsResponse(BaseModel):
    code: int
    message: str
    data: list[DatabaseRow] = Field(default_factory=list)


class DatabaseRowsUpdatedResponse(BaseModel):
    code: int
    message: str
    data: list[DatabaseRowUpdated] = Field(default_factory=list)


class DatabaseRowDetailsResponse(BaseModel):
    code: int
    message: str
    data: list[DatabaseRowDetail] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Document (Collab) models
# ---------------------------------------------------------------------------


class CreateCollabParams(BaseModel):
    encoded_collab: str


class CollabResponse(BaseModel):
    encoded_collab: str


class CollabJsonResponse(BaseModel):
    payload: dict[str, Any]


class BatchCreateCollabParams(BaseModel):
    collabs: dict[str, str]


class CollabDocStateParams(BaseModel):
    doc_state: str


class UpdateCollabWebParams(BaseModel):
    update: str


# ---------------------------------------------------------------------------
# Page & View models
# ---------------------------------------------------------------------------


class CreatePageParams(BaseModel):
    parent_view_id: str
    layout: ViewLayout
    name: str | None = None
    page_data: dict[str, Any] | None = None


class PageCollabData(BaseModel):
    encoded_collab: str
    row_data: dict[str, Any] | None = None


class PageCollab(BaseModel):
    view: FolderView
    data: PageCollabData
    owner: User


class AppendBlockToPageParams(BaseModel):
    blocks: list[dict[str, Any]]


class CreateOrphanedViewParams(BaseModel):
    layout: ViewLayout
    name: str | None = None


class DuplicatePageParams(BaseModel):
    parent_view_id: str | None = None


# ---------------------------------------------------------------------------
# Quick Note models
# ---------------------------------------------------------------------------


class CreateQuickNoteParams(BaseModel):
    title: str
    content: str


class QuickNote(BaseModel):
    id: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime


class QuickNotes(BaseModel):
    items: list[QuickNote]


# ---------------------------------------------------------------------------
# Search models
# ---------------------------------------------------------------------------


class SearchDocumentRequest(BaseModel):
    query: str


class SearchDocumentResponseItem(BaseModel):
    view_id: str
    name: str
    snippet: str | None = None


# ---------------------------------------------------------------------------
# Publishing models
# ---------------------------------------------------------------------------


class PublishPageParams(BaseModel):
    pass


# ---------------------------------------------------------------------------
# Import models
# ---------------------------------------------------------------------------


class CreateImportTask(BaseModel):
    import_type: str
    data: dict[str, Any]


class CreateImportTaskResponse(BaseModel):
    task_id: str


# ---------------------------------------------------------------------------
# Typed API response wrappers (New)
# ---------------------------------------------------------------------------


class CollabResponseWrapper(BaseModel):
    code: int
    message: str
    data: CollabResponse


class CollabJsonResponseWrapper(BaseModel):
    code: int
    message: str
    data: CollabJsonResponse


class PageResponse(BaseModel):
    code: int
    message: str
    data: FolderView


class PageCollabResponse(BaseModel):
    code: int
    message: str
    data: PageCollab


class QuickNoteResponse(BaseModel):
    code: int
    message: str
    data: QuickNote


class QuickNotesResponse(BaseModel):
    code: int
    message: str
    data: QuickNotes


class SearchResponse(BaseModel):
    code: int
    message: str
    data: list[SearchDocumentResponseItem]


class ImportTaskResponse(BaseModel):
    code: int
    message: str
    data: CreateImportTaskResponse
