"""
Application factory — creates and configures the FastAPI application.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from sqlalchemy import text

from app.config import get_settings
from app.core.exceptions import AppException, app_exception_handler, generic_exception_handler
from app.database import _get_engine, _get_session_factory
from app.middleware.cors import setup_cors
from app.schemas.common import HealthCheckResponse

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown events."""
    yield
    engine = _get_engine()
    await engine.dispose()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # ── Middleware ──
    setup_cors(application)

    # ── Rate Limiting ──
    try:
        from app.middleware.rate_limit import setup_rate_limiting
        setup_rate_limiting(application)
    except ImportError:
        pass  # rate limiting middleware is optional

    # ── Exception Handlers ──
    application.add_exception_handler(AppException, app_exception_handler)
    application.add_exception_handler(Exception, generic_exception_handler)

    # ── Health Check ──
    @application.get("/api/health", response_model=HealthCheckResponse, tags=["Health"])
    async def health_check() -> HealthCheckResponse:
        """Check application and database health."""
        db_status = "disconnected"
        try:
            session_factory = _get_session_factory()
            async with session_factory() as session:
                await session.execute(text("SELECT 1"))
                db_status = "connected"
        except Exception:
            db_status = "disconnected"

        return HealthCheckResponse(
            status="healthy" if db_status == "connected" else "unhealthy",
            database=db_status,
            version=settings.APP_VERSION,
        )

    # ── Routers ──
    # Import here to avoid circular imports
    from app.api.router import api_router
    application.include_router(api_router, prefix="/api")

    return application


app = create_app()