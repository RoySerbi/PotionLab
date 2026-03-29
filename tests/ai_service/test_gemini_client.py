from __future__ import annotations

import time
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from redis import Redis

from ai_service.gemini_client import GeminiClient
from ai_service.schemas import CocktailSuggestion, MixRequest


@pytest.fixture
def mix_request() -> MixRequest:
    return MixRequest(ingredients=["gin", "tonic"], mood="refreshing")


@pytest.fixture(autouse=True)
def set_google_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "test")


def test_generate_cache_key_is_stable(mix_request: MixRequest) -> None:
    client = GeminiClient(redis_factory=lambda: None)
    first = client.generate_cache_key(mix_request)
    second = client.generate_cache_key(
        MixRequest(ingredients=["tonic", "gin"], mood="refreshing")
    )
    assert first == second


def test_rate_limit_allows_up_to_fifteen_requests() -> None:
    redis = MagicMock(spec=Redis)
    pipeline_read = MagicMock()
    pipeline_read.zremrangebyscore.return_value = pipeline_read
    pipeline_read.zcard.return_value = pipeline_read
    pipeline_read.execute.return_value = [None, 14]

    pipeline_write = MagicMock()
    pipeline_write.zadd.return_value = pipeline_write
    pipeline_write.expire.return_value = pipeline_write
    pipeline_write.execute.return_value = [1, True]

    redis.pipeline.side_effect = [pipeline_read, pipeline_write]

    client = GeminiClient(redis_factory=lambda: redis, now_fn=lambda: 1000.0)
    client.enforce_rate_limit()

    assert pipeline_write.zadd.called


def test_rate_limit_blocks_after_fifteen_requests() -> None:
    redis = MagicMock(spec=Redis)
    pipeline_read = MagicMock()
    pipeline_read.zremrangebyscore.return_value = pipeline_read
    pipeline_read.zcard.return_value = pipeline_read
    pipeline_read.execute.return_value = [None, 15]
    redis.pipeline.return_value = pipeline_read

    client = GeminiClient(redis_factory=lambda: redis, now_fn=lambda: 1000.0)
    with pytest.raises(HTTPException) as exc:
        client.enforce_rate_limit()
    assert exc.value.status_code == 429


def test_cached_response_roundtrip() -> None:
    key = "cocktail:test"
    suggestion = CocktailSuggestion(
        name="Gin Tonic",
        ingredients=[{"ingredient": "gin", "amount": "2 oz"}],
        instructions="Build over ice.",
        flavor_profile=["crisp"],
        why_this_works="Botanicals pair with quinine.",
    )

    redis = MagicMock(spec=Redis)
    store: dict[str, str] = {}

    def setex(cache_key: str, ttl: int, value: str) -> None:
        if ttl == 3600:
            store[cache_key] = value

    redis.setex.side_effect = setex
    redis.get.side_effect = lambda cache_key: store.get(cache_key)

    client = GeminiClient(redis_factory=lambda: redis, now_fn=time.time)
    client.set_cached(key, suggestion)
    cached = client.get_cached(key)
    assert cached is not None
    assert cached.name == suggestion.name


def test_generate_suggestion_uses_test_fallback(mix_request: MixRequest) -> None:
    client = GeminiClient(redis_factory=lambda: MagicMock(spec=Redis))
    suggestion = client.generate_suggestion(mix_request)
    assert suggestion.name
    assert suggestion.ingredients
