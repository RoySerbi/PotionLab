from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CocktailIngredientCreate(BaseModel):
    ingredient_id: int = Field(gt=0)
    amount: str = Field(min_length=1, max_length=40)
    is_optional: bool = Field(default=False)


class CocktailCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=500)
    instructions: str = Field(min_length=1, max_length=2000)
    glass_type: str = Field(min_length=1, max_length=40)
    difficulty: int = Field(ge=1, le=5)
    ingredients: list[CocktailIngredientCreate] = Field(default=[])


class CocktailRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(gt=0)
    name: str
    description: str | None
    glass_type: str
    difficulty: int


class CocktailReadFull(CocktailRead):
    instructions: str
    ingredients: list[dict[str, object]] = Field(default=[])
    flavor_profile: list[str] = Field(default=[])
