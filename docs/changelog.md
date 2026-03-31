# Changelog

## 0.1.0 (2026-03-30)

Initial release with full AppFlowy Cloud REST API coverage.

### Features

- **Authentication**: Password login, token refresh, OAuth 2.0 token exchange
- **Workspaces**: List workspaces, get folder structure with depth control
- **Databases**: List databases, get field schemas
- **Rows**: List row IDs, get row details, create rows, upsert rows, get updated rows
- **Models**: 28 Pydantic v2 models with strict type annotations
- **Enums**: `IconType`, `ViewLayout`, `Role` enums with named values
- **Errors**: 7 typed exception classes with proper hierarchy
- **Type Safety**: Full type annotations on all public methods
- **Context Manager**: `with` statement support for resource cleanup

### Bug Fixes

- Fixed `login` and `refresh_token` being nested functions inside `__init__`
- Fixed `tokenstore.py` broken import path
- Fixed exception handling order (specific before general)
- Fixed empty `consontant.py` (missing `BASE_URL`)
- Fixed overly permissive type hints (`str | None | Any`)


## 0.1.1 - 0.1.2 (2026-03-30)

- GitHub Actions release workflow
- Fixed broken PyPI release
