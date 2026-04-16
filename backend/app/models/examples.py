"""
EXAMPLE MODELS — Demonstrates SQLAlchemy ORM patterns.
DELETE this entire file and create your own domain models.

To remove:
1. Delete this file (app/models/examples.py)
2. Remove Item, Tag, item_tags imports from app/models/__init__.py
3. Delete app/schemas/examples.py
4. Delete app/api/v1/examples.py
5. Delete app/services/example_service.py
6. Remove example routes from app/api/router.py
7. Generate a new Alembic migration to drop the tables
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


# ── Association table for many-to-many: items <-> tags ──
item_tags = Table(
    "item_tags",
    Base.metadata,
    Column(
        "item_id",
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        UUID(as_uuid=True),
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "created_at",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    ),
)


class Item(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Generic item entity — demonstrates common model patterns.
    REPLACE with your domain entities (e.g., BlogPost, Product, Task, Project, etc.)
    """

    __tablename__ = "items"

    title: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    user = relationship("User", back_populates="items")
    tags = relationship(
        "Tag",
        secondary=item_tags,
        back_populates="items",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Item(id={self.id}, title={self.title!r})>"


class Tag(UUIDPrimaryKeyMixin, Base):
    """
    Generic tag entity — demonstrates many-to-many relationships.
    REPLACE with your domain entities.
    """

    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    items = relationship(
        "Item",
        secondary=item_tags,
        back_populates="tags",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name={self.name!r})>"