from __future__ import annotations

# pyright: reportAny=false, reportExplicitAny=false
import asyncio

import pytest

from scripts import refresh


@pytest.mark.anyio
async def test_refresh_enforces_bounded_concurrency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    in_flight = 0
    max_in_flight = 0
    lock = asyncio.Lock()

    async def fake_call_ai_mix_endpoint(
        client: object,
        *,
        ai_service_url: str,
        ingredients: list[str],
        mood: str,
        preferences: str,
    ) -> dict[str, object]:
        _ = client
        _ = ai_service_url
        _ = ingredients
        _ = mood
        _ = preferences
        nonlocal in_flight, max_in_flight
        async with lock:
            in_flight += 1
            max_in_flight = max(max_in_flight, in_flight)
        await asyncio.sleep(0.02)
        async with lock:
            in_flight -= 1
        return {"name": "Suggestion", "ingredients": [], "instructions": "Stir"}

    monkeypatch.setattr(refresh, "call_ai_mix_endpoint", fake_call_ai_mix_endpoint)

    items = [
        refresh.CocktailWorkItem(
            id=index,
            name=f"Cocktail {index}",
            ingredients=["gin", "lime"],
        )
        for index in range(1, 13)
    ]

    processed_keys: set[str] = set()
    cached_keys: list[str] = []

    def fake_is_processed(key: str) -> bool:
        return key in processed_keys

    def fake_mark_processed(key: str, ttl: int) -> bool:
        _ = ttl
        processed_keys.add(key)
        return True

    def fake_cache_set(key: str, value: str, ttl: int) -> bool:
        _ = value
        _ = ttl
        cached_keys.append(key)
        return True

    stats = await refresh.refresh_cocktails(
        items,
        ai_service_url="http://localhost:8001",
        mood="test",
        preferences="test",
        max_concurrent=5,
        is_processed_fn=fake_is_processed,
        mark_processed_fn=fake_mark_processed,
        cache_set_fn=fake_cache_set,
    )

    assert max_in_flight <= 5
    assert stats.total == 12
    assert stats.processed == 12
    assert stats.skipped == 0
    assert stats.failed == 0
    assert len(cached_keys) == 12


@pytest.mark.anyio
async def test_refresh_skips_already_processed(monkeypatch: pytest.MonkeyPatch) -> None:
    ai_call_count = 0

    async def fake_call_ai_mix_endpoint(
        client: object,
        *,
        ai_service_url: str,
        ingredients: list[str],
        mood: str,
        preferences: str,
    ) -> dict[str, object]:
        _ = client
        _ = ai_service_url
        _ = ingredients
        _ = mood
        _ = preferences
        nonlocal ai_call_count
        ai_call_count += 1
        return {
            "name": "Suggestion",
            "ingredients": [{"ingredient": "gin", "amount": "1 oz"}],
            "instructions": "Shake",
        }

    monkeypatch.setattr(refresh, "call_ai_mix_endpoint", fake_call_ai_mix_endpoint)

    items = [
        refresh.CocktailWorkItem(id=1, name="Already Done", ingredients=["gin"]),
        refresh.CocktailWorkItem(id=2, name="Needs Refresh", ingredients=["vodka"]),
    ]

    processed_keys: set[str] = {"cocktail:1"}
    mark_calls: list[str] = []

    def fake_is_processed(key: str) -> bool:
        return key in processed_keys

    def fake_mark_processed(key: str, ttl: int) -> bool:
        _ = ttl
        processed_keys.add(key)
        mark_calls.append(key)
        return True

    def fake_cache_set(key: str, value: str, ttl: int) -> bool:
        _ = key
        _ = value
        _ = ttl
        return True

    stats = await refresh.refresh_cocktails(
        items,
        ai_service_url="http://localhost:8001",
        mood="test",
        preferences="test",
        max_concurrent=5,
        is_processed_fn=fake_is_processed,
        mark_processed_fn=fake_mark_processed,
        cache_set_fn=fake_cache_set,
    )

    assert ai_call_count == 1
    assert mark_calls == ["cocktail:2"]
    assert stats.total == 2
    assert stats.processed == 1
    assert stats.skipped == 1
    assert stats.failed == 0
