"""
EXAMPLE SCHEMAS — Demonstrates Pydantic schema patterns.
DELETE this file when removing example entities.

To remove:
1. Delete this file (app/schemas/examples.py)
2. Remove example imports from app/schemas/__init__.py
"""
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    """Schema for creating a tag. REPLACE with your domain schemas."""
    name: str = Field(..., min_length=1, max_length=100)


class TagResponse(BaseModel):
    """Schema for tag in responses. REPLACE with your domain schemas."""
    id: uuid.UUID
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TagListResponse(BaseModel):
    """Schema for list of tags response."""
    tags: List[TagResponse]


class ItemCreate(BaseModel):
    """Schema for creating an item. REPLACE with your domain schemas."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    tag_names: Optional[List[str]] = Field(default_factory=list)


class ItemUpdate(BaseModel):
    """Schema for updating an item. REPLACE with your domain schemas."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    tag_names: Optional[List[str]] = None


class ItemResponse(BaseModel):
    """Schema for item in responses. REPLACE with your domain schemas."""
    id: uuid.UUID
    title: str
    description: Optional[str]
    tags: List[TagResponse]
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ItemListResponse(BaseModel):
    """Schema for paginated item list response."""
    items: List[ItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int