"""
Authentication endpoints: register, login, refresh, logout, profile.
"""
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, get_current_active_user
from app.core.security import decode_token
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RefreshRequest,
    LogoutRequest,
    UserResponse,
    UserUpdateRequest,
)
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    service = AuthService(db)
    user = await service.register(data)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and receive access + refresh tokens",
)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    service = AuthService(db)
    return await service.authenticate(data)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token using a valid refresh token",
)
async def refresh(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    service = AuthService(db)
    return await service.refresh_tokens(data.refresh_token)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout by blocklisting the refresh and access tokens",
)
async def logout(
    data: LogoutRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> MessageResponse:
    service = AuthService(db)

    # Extract access token JTI from the Authorization header
    access_token_jti = None
    access_token_exp = None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        access_token = auth_header[7:]
        access_payload = decode_token(access_token)
        if access_payload:
            access_token_jti = access_payload.get("jti")
            access_token_exp = access_payload.get("exp")

    await service.logout(
        data.refresh_token,
        current_user.id,
        access_token_jti=access_token_jti,
        access_token_exp=access_token_exp,
    )
    return MessageResponse(message="Successfully logged out")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_me(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
)
async def update_me(
    data: UserUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    service = AuthService(db)
    updated_user = await service.update_profile(current_user, data)
    return UserResponse.model_validate(updated_user)