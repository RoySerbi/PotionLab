from __future__ import annotations

from sqlalchemy import Column, String
from sqlmodel import Field, SQLModel


class FlavorTag(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(
        sa_column=Column(String(50), unique=True, nullable=False, index=True)
    )
    category: str = Field(sa_column=Column(String(30), nullable=False))
