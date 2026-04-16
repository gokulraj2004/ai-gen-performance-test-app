"""
Async SQLAlchemy engine, session factory, and dependency for FastAPI.
"""
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.config import get_settings

_engine: Optional[AsyncEngine] = None
_async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def _get_engine() -> AsyncEngine:
    """Lazily create and cache the async engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.async_database_url,
            echo=settings.DEBUG,
            future=True,
            pool_pre_ping=True,
            poolclass=NullPool if settings.APP_ENV == "testing" else None,
        )
    return _engine


def _get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Lazily create and cache the session factory."""
    global _async_session_factory
    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(
            bind=_get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _async_session_factory


def reset_engine() -> None:
    """
    Reset the cached engine and session factory.
    Useful for testing when settings change between test runs.
    """
    global _engine, _async_session_factory
    _engine = None
    _async_session_factory = None


# Provide module-level accessors for backward compatibility
@property
def engine() -> AsyncEngine:
    return _get_engine()


@property
def async_session_factory() -> async_sessionmaker[AsyncSession]:
    return _get_session_factory()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an async database session.
    Automatically closes the session when the request is complete.
    """
    session_factory = _get_session_factory()
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()