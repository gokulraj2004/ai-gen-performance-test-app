"""
User model — part of the authentication system. KEEP this model.
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Application user with authentication fields.
    This is a core model — keep it and extend as needed.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    first_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    last_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Relationships
    items = relationship(
        "Item", back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
    blocklisted_tokens = relationship(
        "TokenBlocklist", back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email!r})>"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"