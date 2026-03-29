from __future__ import annotations

from fastapi import FastAPI

from ai_service.gemini_client import GeminiClient
from ai_service.schemas import CocktailSuggestion, MixRequest

app = FastAPI(title="PotionLab AI Mixologist", version="0.1.0")
gemini_client = GeminiClient()


@app.post("/mix", response_model=CocktailSuggestion)
async def generate_cocktail(request: MixRequest) -> CocktailSuggestion:
    cache_key = gemini_client.generate_cache_key(request)
    cached = gemini_client.get_cached(cache_key)
    if cached is not None:
        return cached

    gemini_client.enforce_rate_limit()
    suggestion = gemini_client.generate_suggestion(request)
    gemini_client.set_cached(cache_key, suggestion)
    return suggestion


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "ai-mixologist"}
