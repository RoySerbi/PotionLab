from __future__ import annotations

from sqlalchemy import Column, String
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(
        sa_column=Column(String(80), unique=True, nullable=False, index=True)
    )
    hashed_password: str = Field(sa_column=Column(String(255), nullable=False))
    role: str = Field(default="reader", sa_column=Column(String(20), nullable=False))
