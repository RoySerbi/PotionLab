from __future__ import annotations

from pydantic import BaseModel, Field


class MixRequest(BaseModel):
    ingredients: list[str] = Field(min_length=1, max_length=20)
    mood: str | None = None
    preferences: str | None = None


class CocktailSuggestion(BaseModel):
    name: str
    ingredients: list[dict[str, str]]
    instructions: str
    flavor_profile: list[str]
    why_this_works: str
