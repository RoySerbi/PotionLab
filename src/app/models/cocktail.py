from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text
from sqlmodel import Field, SQLModel


class Cocktail(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(
        sa_column=Column(String(100), unique=True, nullable=False, index=True)
    )
    description: str | None = Field(
        default=None, sa_column=Column(String(255), nullable=True)
    )
    instructions: str = Field(sa_column=Column(Text, nullable=False))
    glass_type: str = Field(sa_column=Column(String(50), nullable=False))
    difficulty: int = Field(sa_column=Column(Integer, nullable=False), ge=1, le=5)
