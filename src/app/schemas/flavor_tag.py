from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class FlavorTagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=30)
    category: str = Field(min_length=1, max_length=30)


class FlavorTagRead(FlavorTagCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(gt=0)
