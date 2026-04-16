"""
Dependency injection utilities for FastAPI route handlers.

Provides:
- get_db_session: async database session
- get_current_user: extracts and validates JWT, returns User
- get_current_active_user: ensures user is active
"""
import uuid
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.models.user import User
from app.models.token_blocklist import TokenBlocklist
from app.core.security import decode_token

security_scheme = HTTPBearer()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session, ensuring cleanup on exit."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """
    Extract the JWT from the Authorization header, decode it,
    verify it has not been blocklisted, and return the corresponding User.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id_str: str | None = payload.get("sub")
    token_type: str | None = payload.get("type")
    jti: str | None = payload.get("jti")

    if user_id_str is None or token_type != "access":
        raise credentials_exception

    # Check if token has been blocklisted
    if jti:
        result = await db.execute(
            select(TokenBlocklist).where(TokenBlocklist.jti == jti)
        )
        if result.scalar_one_or_none() is not None:
            raise credentials_exception

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure the authenticated user account is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )
    return current_user