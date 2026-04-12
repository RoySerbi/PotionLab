from __future__ import annotations

import hashlib
import importlib
import json
import os
import time
from collections.abc import Callable
from typing import Protocol, cast

from fastapi import HTTPException, status

from ai_service.schemas import CocktailSuggestion, MixRequest


class _GeminiResponse(Protocol):
    text: str | None


class _GeminiClient(Protocol):
    @property
    def models(self) -> _GeminiModel: ...


class _GeminiModel(Protocol):
    def generate_content(
        self, model: str, contents: str, config: dict[str, object]
    ) -> _GeminiResponse: ...


class _RedisPipeline(Protocol):
    def zremrangebyscore(self, name: str, min: float, max: float) -> object: ...

    def zcard(self, name: str) -> object: ...

    def zadd(self, name: str, mapping: dict[str, float]) -> object: ...

    def expire(self, name: str, time: int) -> object: ...

    def execute(self) -> list[object]: ...


class _RedisClient(Protocol):
    def ping(self) -> object: ...

    def get(self, key: str) -> str | None: ...

    def setex(self, key: str, ttl: int, value: str) -> object: ...

    def pipeline(self, transaction: bool = True) -> _RedisPipeline: ...


class GeminiClient:
    def __init__(
        self,
        redis_factory: Callable[[], _RedisClient | None] | None = None,
        now_fn: Callable[[], float] = time.time,
    ):
        self._redis_factory: Callable[[], _RedisClient | None] = (
            redis_factory if redis_factory is not None else self._build_redis_client
        )
        self._now_fn: Callable[[], float] = now_fn
        self._max_requests: int = 15
        self._window_seconds: int = 60
        self._rate_limit_key: str = "ai:mixologist:requests"
        self._cache_ttl_seconds: int = 3600
        self._model_name: str = "gemini-2.0-flash-exp"
        self._redis_url: str = os.environ.get(
            "POTION_REDIS_URL", "redis://localhost:6379"
        )
        self._api_key: str = self._read_api_key()
        self._model: _GeminiClient | None = None
        if self._api_key != "test":
            genai_module = importlib.import_module("google.genai")
            client_class = cast(
                Callable[..., _GeminiClient], getattr(genai_module, "Client")
            )
            self._model = client_class(api_key=self._api_key)

    def _read_api_key(self) -> str:
        fallback = os.environ.get("GOOGLE_API_KEY", "")
        if not fallback.strip():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="GOOGLE_API_KEY is not configured",
            )
        return fallback

    def _build_redis_client(self) -> _RedisClient | None:
        try:
            redis_module = importlib.import_module("redis")
            from_url = cast(
                Callable[..., _RedisClient], getattr(redis_module, "Redis").from_url
            )
            client = from_url(self._redis_url, decode_responses=True)
            _ = client.ping()
            return client
        except Exception:
            return None

    def generate_cache_key(self, request: MixRequest) -> str:
        payload = {
            "ingredients": sorted(i.strip().lower() for i in request.ingredients),
            "mood": (request.mood or "").strip().lower(),
            "preferences": (request.preferences or "").strip().lower(),
        }
        raw = json.dumps(payload, sort_keys=True)
        digest = hashlib.md5(raw.encode("utf-8"), usedforsecurity=False).hexdigest()
        return f"cocktail:{digest}"

    def get_cached(self, cache_key: str) -> CocktailSuggestion | None:
        client = self._redis_factory()
        if client is None:
            return None
        cached = client.get(cache_key)
        if cached is None:
            return None
        return CocktailSuggestion.model_validate_json(str(cached))

    def set_cached(self, cache_key: str, suggestion: CocktailSuggestion) -> None:
        client = self._redis_factory()
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Redis unavailable for cache write",
            )
        _ = client.setex(
            cache_key, self._cache_ttl_seconds, suggestion.model_dump_json()
        )

    def enforce_rate_limit(self) -> None:
        client = self._redis_factory()
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Redis unavailable for rate limiting",
            )

        now = self._now_fn()
        window_start = now - self._window_seconds
        member = f"{now}:{time.monotonic_ns()}"

        pipe = client.pipeline(transaction=True)
        _ = pipe.zremrangebyscore(self._rate_limit_key, 0, window_start)
        _ = pipe.zcard(self._rate_limit_key)
        execution = pipe.execute()
        count_obj = execution[1] if len(execution) > 1 else 0
        if isinstance(count_obj, int | float | str):
            request_count = int(count_obj)
        else:
            request_count = 0
        if request_count >= self._max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )

        write_pipe = client.pipeline(transaction=True)
        _ = write_pipe.zadd(self._rate_limit_key, {member: now})
        _ = write_pipe.expire(self._rate_limit_key, self._window_seconds)
        _ = write_pipe.execute()

    def _clean_schema(self, schema: dict[str, object]) -> dict[str, object]:
        """Remove unsupported fields from the schema for google.genai."""
        cleaned = {}
        for key, value in schema.items():
            if key in ("title", "additionalProperties"):
                continue
            if isinstance(value, dict):
                cleaned[key] = self._clean_schema(value)
            elif isinstance(value, list):
                cleaned[key] = [self._clean_schema(item) if isinstance(item, dict) else item for item in value]
            else:
                cleaned[key] = value
        return cleaned

    def _fake_response(self, request: MixRequest) -> CocktailSuggestion:
        name_seed = " ".join(sorted(request.ingredients)[:2]).title() or "Custom"
        return CocktailSuggestion(
            name=f"{name_seed} Highball",
            ingredients=[
                {"ingredient": item, "amount": "1 oz"}
                for item in sorted(request.ingredients)
            ],
            instructions="Build over ice and stir gently.",
            flavor_profile=["balanced", "refreshing"],
            why_this_works=(
                "Ingredients complement each other through acidity, "
                "sweetness, and aroma balance."
            ),
        )

    def generate_suggestion(self, request: MixRequest) -> CocktailSuggestion:
        if self._api_key == "test":
            return self._fake_response(request)

        prompt = (
            "You are an expert mixologist. Return only JSON matching the schema. "
            "Create one cocktail suggestion from available ingredients. "
            f"Ingredients: {request.ingredients}. "
            f"Mood: {request.mood or 'none'}. "
            f"Preferences: {request.preferences or 'none'}."
        )
        if self._model is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gemini model is not initialized",
            )
        schema = self._clean_schema(CocktailSuggestion.model_json_schema())
        response = self._model.models.generate_content(
            model=self._model_name,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": schema,
            },
        )
        text = str(response.text or "").strip()
        if not text:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Gemini returned empty response",
            )
        return CocktailSuggestion.model_validate_json(text)
