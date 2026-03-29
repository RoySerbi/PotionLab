from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
)
from sqlmodel import Field, SQLModel


class CocktailIngredient(SQLModel, table=True):
    __tablename__ = "cocktailingredient"
    __table_args__ = (PrimaryKeyConstraint("cocktail_id", "ingredient_id"),)

    cocktail_id: int = Field(
        sa_column=Column(Integer, ForeignKey("cocktail.id"), nullable=False)
    )
    ingredient_id: int = Field(
        sa_column=Column(Integer, ForeignKey("ingredient.id"), nullable=False)
    )
    amount: str = Field(sa_column=Column(String(50), nullable=False))
    is_optional: bool = Field(default=False, sa_column=Column(Boolean, nullable=False))
