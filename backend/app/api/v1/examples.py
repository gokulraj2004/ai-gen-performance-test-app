"""
EXAMPLE CRUD endpoints — demonstrates FastAPI router patterns.
DELETE this entire file and create your own domain endpoints.

To remove:
1. Delete this file
2. Remove the examples router import from app/api/router.py
3. Create your domain router files in app/api/v1/
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.schemas.examples import (
    ItemCreate,
    ItemUpdate,
    ItemResponse,
    ItemListResponse,
    TagCreate,
    TagResponse,
    TagListResponse,
)
from app.services.example_service import ExampleService

router = APIRouter()


# ── Item Endpoints (EXAMPLE - DELETE & replace) ──────────────────────────────


@router.get(
    "/items",
    response_model=ItemListResponse,
    summary="List items with pagination, search, and filtering",
)
async def list_items(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(default=None, description="Search title and description"),
    tags: list[str] | None = Query(default=None, description="Filter by tag names"),
    sort_by: str = Query(
        default="created_at_desc",
        pattern="^(title_asc|title_desc|created_at_desc)$",
        description="Sort order",
    ),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> ItemListResponse:
    service = ExampleService(db)
    return await service.list_items(
        page=page,
        page_size=page_size,
        search=search,
        tags=tags,
        sort_by=sort_by,
    )


@router.get(
    "/items/{item_id}",
    response_model=ItemResponse,
    summary="Get a single item by ID",
)
async def get_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> ItemResponse:
    service = ExampleService(db)
    item = await service.get_item(item_id)
    return item


@router.post(
    "/items",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new item",
)
async def create_item(
    data: ItemCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> ItemResponse:
    service = ExampleService(db)
    return await service.create_item(data, current_user.id)


@router.put(
    "/items/{item_id}",
    response_model=ItemResponse,
    summary="Update an existing item (owner only)",
)
async def update_item(
    item_id: UUID,
    data: ItemUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> ItemResponse:
    service = ExampleService(db)
    return await service.update_item(item_id, data, current_user.id)


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an item (owner only)",
)
async def delete_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> None:
    service = ExampleService(db)
    await service.delete_item(item_id, current_user.id)


# ── Tag Endpoints (EXAMPLE - DELETE & replace) ──────────────────────────────


@router.get(
    "/tags",
    response_model=TagListResponse,
    summary="List all tags (public)",
)
async def list_tags(
    db: AsyncSession = Depends(get_db_session),
) -> TagListResponse:
    service = ExampleService(db)
    return await service.list_tags()


@router.post(
    "/tags",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tag",
)
async def create_tag(
    data: TagCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> TagResponse:
    service = ExampleService(db)
    return await service.create_tag(data)