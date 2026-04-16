"""
EXAMPLE service — demonstrates service-layer patterns with async SQLAlchemy.
DELETE this entire file and create your own domain services.

To remove:
1. Delete this file
2. Delete app/api/v1/examples.py
3. Remove the examples router from app/api/router.py
4. Create your domain service files in app/services/
"""
import math
import uuid
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.examples import Item, Tag, item_tags
from app.schemas.examples import (
    ItemCreate,
    ItemUpdate,
    ItemResponse,
    ItemListResponse,
    TagCreate,
    TagResponse,
    TagListResponse,
)


class ExampleService:
    """CRUD operations for the example Item and Tag entities."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_items(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        tags: list[str] | None = None,
        sort_by: str = "created_at_desc",
    ) -> ItemListResponse:
        """List items with pagination, search, tag filtering, and sorting."""
        query = select(Item).options(selectinload(Item.tags))

        # Search filter
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Item.title.ilike(search_term),
                    Item.description.ilike(search_term),
                )
            )

        # Tag filter
        if tags:
            query = query.join(Item.tags).where(Tag.name.in_(tags)).distinct()

        # Sorting
        if sort_by == "title_asc":
            query = query.order_by(Item.title.asc())
        elif sort_by == "title_desc":
            query = query.order_by(Item.title.desc())
        else:
            query = query.order_by(Item.created_at.desc())

        # Count total before pagination
        count_query = select(func.count()).select_from(Item)
        if search:
            search_term = f"%{search}%"
            count_query = count_query.where(
                or_(
                    Item.title.ilike(search_term),
                    Item.description.ilike(search_term),
                )
            )
        if tags:
            count_query = count_query.join(Item.tags).where(Tag.name.in_(tags)).distinct()

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        items = result.scalars().unique().all()

        total_pages = math.ceil(total / page_size) if page_size > 0 else 0

        return ItemListResponse(
            items=[ItemResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_item(self, item_id: UUID) -> ItemResponse:
        """Get a single item by ID. Raises 404 if not found."""
        result = await self.db.execute(
            select(Item).options(selectinload(Item.tags)).where(Item.id == item_id)
        )
        item = result.scalar_one_or_none()
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )
        return ItemResponse.model_validate(item)

    async def create_item(self, data: ItemCreate, user_id: UUID) -> ItemResponse:
        """Create a new item, optionally associating tags by name."""
        item = Item(
            id=uuid.uuid4(),
            title=data.title.strip(),
            description=data.description.strip() if data.description else None,
            user_id=user_id,
        )

        if data.tag_names:
            tags = await self._get_or_create_tags(data.tag_names)
            item.tags = tags

        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)

        # Re-fetch with tags loaded
        result = await self.db.execute(
            select(Item).options(selectinload(Item.tags)).where(Item.id == item.id)
        )
        item = result.scalar_one()
        return ItemResponse.model_validate(item)

    async def update_item(
        self, item_id: UUID, data: ItemUpdate, user_id: UUID
    ) -> ItemResponse:
        """Update an item. Only the owner can update."""
        result = await self.db.execute(
            select(Item).options(selectinload(Item.tags)).where(Item.id == item_id)
        )
        item = result.scalar_one_or_none()

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )

        if item.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this item",
            )

        if data.title is not None:
            item.title = data.title.strip()
        if data.description is not None:
            item.description = data.description.strip() if data.description else None
        if data.tag_names is not None:
            tags = await self._get_or_create_tags(data.tag_names)
            item.tags = tags

        await self.db.commit()
        await self.db.refresh(item)

        # Re-fetch with tags loaded
        result = await self.db.execute(
            select(Item).options(selectinload(Item.tags)).where(Item.id == item.id)
        )
        item = result.scalar_one()
        return ItemResponse.model_validate(item)

    async def delete_item(self, item_id: UUID, user_id: UUID) -> None:
        """Delete an item. Only the owner can delete."""
        result = await self.db.execute(
            select(Item).where(Item.id == item_id)
        )
        item = result.scalar_one_or_none()

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )

        if item.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this item",
            )

        await self.db.delete(item)
        await self.db.commit()

    async def list_tags(self) -> TagListResponse:
        """List all tags."""
        result = await self.db.execute(
            select(Tag).order_by(Tag.name.asc())
        )
        tags = result.scalars().all()
        return TagListResponse(
            tags=[TagResponse.model_validate(tag) for tag in tags]
        )

    async def create_tag(self, data: TagCreate) -> TagResponse:
        """Create a new tag. Raises 409 if name already exists."""
        tag_name = data.name.lower().strip()
        result = await self.db.execute(
            select(Tag).where(Tag.name == tag_name)
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A tag with this name already exists",
            )

        tag = Tag(
            id=uuid.uuid4(),
            name=tag_name,
        )
        self.db.add(tag)
        await self.db.commit()
        await self.db.refresh(tag)
        return TagResponse.model_validate(tag)

    async def _get_or_create_tags(self, tag_names: list[str]) -> list[Tag]:
        """Get existing tags or create new ones for the given names."""
        normalized = [name.lower().strip() for name in tag_names if name.strip()]
        if not normalized:
            return []

        result = await self.db.execute(
            select(Tag).where(Tag.name.in_(normalized))
        )
        existing_tags = list(result.scalars().all())
        existing_names = {tag.name for tag in existing_tags}

        new_tags = []
        for name in normalized:
            if name not in existing_names:
                tag = Tag(id=uuid.uuid4(), name=name)
                self.db.add(tag)
                new_tags.append(tag)
                existing_names.add(name)

        if new_tags:
            await self.db.flush()

        return existing_tags + new_tags