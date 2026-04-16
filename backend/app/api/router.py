"""
Main API router aggregating all sub-routers.
"""
from fastapi import APIRouter

from app.api.v1 import auth, examples

api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/v1/auth",
    tags=["Authentication"],
)

# EXAMPLE ROUTER - DELETE and replace with your domain routers
api_router.include_router(
    examples.router,
    prefix="/v1",
    tags=["Examples"],
)