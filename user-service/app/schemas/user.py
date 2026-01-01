"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr


class UserBase(BaseModel):
    """Shared attributes for user representations."""

    name: str = Field(min_length=1, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    """Payload for creating a new user."""

    password: SecretStr = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    """Payload for updating an existing user."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[SecretStr] = Field(default=None, min_length=8, max_length=128)
    is_active: Optional[bool] = None


class UserRead(UserBase):
    """Response model for user data."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
