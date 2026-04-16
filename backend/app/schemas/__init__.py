"""
Pydantic schemas package — re-exports for convenient imports.
"""
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RefreshRequest,
    RefreshTokenRequest,
    LogoutRequest,
    UserResponse,
    UserUpdateRequest,
)
from app.schemas.common import (
    ErrorResponse,
    MessageResponse,
    PaginatedResponse,
    HealthCheckResponse,
)
from app.schemas.examples import (
    ItemCreate,
    ItemUpdate,
    ItemResponse,
    TagCreate,
    TagResponse,
    ItemListResponse,
    TagListResponse,
)

__all__ = [
    # Auth
    "LoginRequest",
    "RegisterRequest",
    "TokenResponse",
    "RefreshRequest",
    "RefreshTokenRequest",
    "LogoutRequest",
    "UserResponse",
    "UserUpdateRequest",
    # Common
    "ErrorResponse",
    "MessageResponse",
    "PaginatedResponse",
    "HealthCheckResponse",
    # Examples (DELETE when removing example entities)
    "ItemCreate",
    "ItemUpdate",
    "ItemResponse",
    "TagCreate",
    "TagResponse",
    "ItemListResponse",
    "TagListResponse",
]