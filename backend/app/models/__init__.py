"""
SQLAlchemy models package.

All models are imported here so that Alembic can discover them
when running `alembic revision --autogenerate`.
"""
from app.models.base import Base
from app.models.user import User
from app.models.token_blocklist import TokenBlocklist
from app.models.examples import Item, Tag, item_tags

__all__ = [
    "Base",
    "User",
    "TokenBlocklist",
    "Item",
    "Tag",
    "item_tags",
]