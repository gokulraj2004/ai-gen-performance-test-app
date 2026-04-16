"""
Authentication service — handles registration, login, token refresh, logout,
and profile updates. All database interactions go through this layer.
"""
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User
from app.models.token_blocklist import TokenBlocklist
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserUpdateRequest,
)
from app.config import get_settings


class AuthService:
    """Encapsulates authentication business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def register(self, data: RegisterRequest) -> User:
        """Register a new user. Raises 409 if email already exists."""
        result = await self.db.execute(
            select(User).where(User.email == data.email.lower())
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )

        user = User(
            id=uuid.uuid4(),
            email=data.email.lower().strip(),
            hashed_password=hash_password(data.password),
            first_name=data.first_name.strip(),
            last_name=data.last_name.strip(),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def authenticate(self, data: LoginRequest) -> TokenResponse:
        """Validate credentials and return an access/refresh token pair."""
        result = await self.db.execute(
            select(User).where(User.email == data.email.lower())
        )
        user = result.scalar_one_or_none()

        if user is None or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated",
            )

        return self._generate_tokens(user)

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """
        Validate a refresh token, blocklist it (rotation), and issue a new pair.
        """
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        jti = payload.get("jti")
        user_id_str = payload.get("sub")

        if not jti or not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload",
            )

        # Check if already blocklisted
        result = await self.db.execute(
            select(TokenBlocklist).where(TokenBlocklist.jti == jti)
        )
        if result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked",
            )

        # Blocklist the old refresh token (token rotation)
        exp_timestamp = payload.get("exp", 0)
        expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

        blocklist_entry = TokenBlocklist(
            id=uuid.uuid4(),
            jti=jti,
            token_type="refresh",
            user_id=uuid.UUID(user_id_str),
            expires_at=expires_at,
        )
        self.db.add(blocklist_entry)
        await self.db.commit()

        # Fetch user
        result = await self.db.execute(
            select(User).where(User.id == uuid.UUID(user_id_str))
        )
        user = result.scalar_one_or_none()
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        return self._generate_tokens(user)

    async def logout(
        self,
        refresh_token: str,
        user_id: uuid.UUID,
        access_token_jti: str | None = None,
        access_token_exp: int | None = None,
    ) -> None:
        """Blocklist the provided refresh token and optionally the access token."""
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token",
            )

        jti = payload.get("jti")
        if not jti:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token payload",
            )

        # Check if already blocklisted — idempotent logout
        result = await self.db.execute(
            select(TokenBlocklist).where(TokenBlocklist.jti == jti)
        )
        if result.scalar_one_or_none() is None:
            exp_timestamp = payload.get("exp", 0)
            expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

            blocklist_entry = TokenBlocklist(
                id=uuid.uuid4(),
                jti=jti,
                token_type="refresh",
                user_id=user_id,
                expires_at=expires_at,
            )
            self.db.add(blocklist_entry)

        # Also blocklist the access token if JTI is provided
        if access_token_jti:
            result = await self.db.execute(
                select(TokenBlocklist).where(TokenBlocklist.jti == access_token_jti)
            )
            if result.scalar_one_or_none() is None:
                access_expires_at = datetime.fromtimestamp(
                    access_token_exp or 0, tz=timezone.utc
                )
                access_blocklist_entry = TokenBlocklist(
                    id=uuid.uuid4(),
                    jti=access_token_jti,
                    token_type="access",
                    user_id=user_id,
                    expires_at=access_expires_at,
                )
                self.db.add(access_blocklist_entry)

        await self.db.commit()

    async def update_profile(self, user: User, data: UserUpdateRequest) -> User:
        """Update user profile fields."""
        if data.first_name is not None:
            user.first_name = data.first_name.strip()
        if data.last_name is not None:
            user.last_name = data.last_name.strip()
        if data.email is not None:
            new_email = data.email.lower().strip()
            if new_email != user.email:
                result = await self.db.execute(
                    select(User).where(User.email == new_email)
                )
                if result.scalar_one_or_none() is not None:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="A user with this email already exists",
                    )
                user.email = new_email

        await self.db.commit()
        await self.db.refresh(user)
        return user

    @staticmethod
    def _generate_tokens(user: User) -> TokenResponse:
        """Create a fresh access + refresh token pair for the given user."""
        settings = get_settings()
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )