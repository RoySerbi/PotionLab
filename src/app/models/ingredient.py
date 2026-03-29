from __future__ import annotations

from sqlalchemy import Column, String
from sqlmodel import Field, SQLModel


class Ingredient(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(
        sa_column=Column(String(80), unique=True, nullable=False, index=True)
    )
    category: str = Field(sa_column=Column(String(50), nullable=False))
    description: str | None = Field(
        default=None, sa_column=Column(String(255), nullable=True)
    )
