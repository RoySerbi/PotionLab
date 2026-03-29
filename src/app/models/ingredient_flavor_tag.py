from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, PrimaryKeyConstraint
from sqlmodel import Field, SQLModel


class IngredientFlavorTag(SQLModel, table=True):
    __tablename__ = "ingredientflavortag"
    __table_args__ = (PrimaryKeyConstraint("ingredient_id", "flavor_tag_id"),)

    ingredient_id: int = Field(
        sa_column=Column(Integer, ForeignKey("ingredient.id"), nullable=False)
    )
    flavor_tag_id: int = Field(
        sa_column=Column(Integer, ForeignKey("flavortag.id"), nullable=False)
    )
