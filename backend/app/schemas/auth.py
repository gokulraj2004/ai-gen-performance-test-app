"""
Authentication-related Pydantic schemas.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Schema for login endpoint."""
    email: EmailStr
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    """Schema for registration endpoint."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    """Schema for token refresh endpoint."""
    refresh_token: str


class LogoutRequest(BaseModel):
    """Schema for logout endpoint."""
    refresh_token: str


# Keep backward-compatible alias
RefreshTokenRequest = RefreshRequest


class UserResponse(BaseModel):
    """Schema for user profile response."""
    id: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    def __init__(self, **data):
        # Convert UUID to string if needed
        if "id" in data and not isinstance(data["id"], str):
            data["id"] = str(data["id"])
        super().__init__(**data)


class UserUpdateRequest(BaseModel):
    """Schema for updating user profile."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None