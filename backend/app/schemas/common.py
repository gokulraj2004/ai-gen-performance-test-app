"""
Common/shared Pydantic schemas used across the application.
"""
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    status_code: int
    errors: Optional[List[dict[str, Any]]] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class HealthCheckResponse(BaseModel):
    """Health check endpoint response."""
    status: str
    database: str
    version: str