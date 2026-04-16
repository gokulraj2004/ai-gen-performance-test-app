"""
Token blocklist model for revoking JWT refresh tokens.
Part of the authentication system — KEEP this model.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin


class TokenBlocklist(UUIDPrimaryKeyMixin, Base):
    """
    Stores revoked/blocklisted JWT tokens.
    Used to invalidate refresh tokens on logout.
    """

    __tablename__ = "token_blocklist"

    jti: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, index=True
    )
    token_type: Mapped[str] = mapped_column(
        String(10), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="blocklisted_tokens")

    def __repr__(self) -> str:
        return f"<TokenBlocklist(jti={self.jti!r}, token_type={self.token_type!r})>"