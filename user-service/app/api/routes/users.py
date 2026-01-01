"""API routes for user management."""

from typing import Annotated

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User
from app.schemas import UserCreate, UserRead, UserUpdate

DbSession = Annotated[Session, Depends(get_db)]

router = APIRouter(prefix="/users", tags=["Users"])


def _hash_password(plain_password: str) -> str:
    """Hash a password with bcrypt using a work factor suitable for API usage."""

    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _require_name(name: str) -> str:
    trimmed = name.strip()
    if not trimmed:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Name cannot be blank")
    return trimmed


def _get_user_or_404(user_id: int, db: Session) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/", response_model=list[UserRead], status_code=status.HTTP_200_OK)
def list_users(db: DbSession) -> list[UserRead]:
    """Return all users ordered by their identifier."""

    result = db.execute(select(User).order_by(User.id))
    return list(result.scalars().all())


@router.get("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
def get_user(user_id: int, db: DbSession) -> UserRead:
    """Retrieve a single user by identifier."""

    return _get_user_or_404(user_id, db)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: DbSession) -> UserRead:
    """Create a new user ensuring email uniqueness and secure password storage."""

    normalized_email = _normalize_email(payload.email)
    existing_user = db.execute(select(User).where(User.email == normalized_email)).scalar_one_or_none()
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        name=_require_name(payload.name),
        email=normalized_email,
        hashed_password=_hash_password(payload.password.get_secret_value()),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
def update_user(user_id: int, payload: UserUpdate, db: DbSession) -> UserRead:
    """Update select fields of an existing user."""

    user = _get_user_or_404(user_id, db)

    if payload.name is not None:
        user.name = _require_name(payload.name)

    if payload.password is not None:
        user.hashed_password = _hash_password(payload.password.get_secret_value())

    if payload.is_active is not None:
        user.is_active = payload.is_active

    if payload.email is not None:
        normalized_email = _normalize_email(payload.email)
        if normalized_email != user.email:
            conflict = db.execute(
                select(User).where(User.email == normalized_email, User.id != user.id)
            ).scalar_one_or_none()
            if conflict is not None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
            user.email = normalized_email

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: DbSession) -> None:
    """Delete a user from the system."""

    user = _get_user_or_404(user_id, db)
    db.delete(user)
    db.commit()
