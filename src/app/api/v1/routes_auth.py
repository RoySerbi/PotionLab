from __future__ import annotations

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import (
    authenticate_user,
    create_access_token,
    hash_password,
    require_auth,
    require_role,
)
from app.db.session import get_session
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=6, max_length=128)


class RegisterResponse(BaseModel):
    id: int
    username: str
    role: str


class TokenRequest(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    username: str
    role: str


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterResponse,
)
def register_user(
    payload: RegisterRequest,
    session: Session = Depends(get_session),
) -> RegisterResponse:
    existing = session.exec(
        select(User).where(User.username == payload.username)
    ).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    user = User(
        username=payload.username,
        hashed_password=hash_password(payload.password),
        role="reader",
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User creation failed",
        )
    return RegisterResponse(id=user.id, username=user.username, role=user.role)


@router.post("/token", response_model=TokenResponse)
def login_for_token(
    payload: TokenRequest,
    session: Session = Depends(get_session),
) -> TokenResponse:
    user = authenticate_user(session, payload.username, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    token = create_access_token(
        {"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=settings.jwt_access_token_expire_minutes),
    )
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
def read_me(payload: dict[str, Any] = Depends(require_auth)) -> MeResponse:
    return MeResponse(username=str(payload.get("sub")), role=str(payload.get("role")))


@router.delete(
    "/users/{username}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
def delete_user(username: str, session: Session = Depends(get_session)) -> None:
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    session.delete(user)
    session.commit()
