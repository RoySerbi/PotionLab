from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.flavor_tag import FlavorTagRead


class IngredientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    category: str = Field(min_length=1, max_length=40)
    description: str | None = Field(default=None, max_length=255)
    flavor_tag_ids: list[int] = Field(default=[])


class IngredientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(gt=0)
    name: str
    category: str
    description: str | None


class IngredientReadWithTags(IngredientRead):
    flavor_tags: list[FlavorTagRead] = Field(default=[])
