from __future__ import annotations

# pyright: reportMissingTypeStubs=false
import asyncio
import json
import logging
import os
from collections.abc import Callable
from dataclasses import dataclass
from time import perf_counter
from typing import cast

import httpx
from anyio import to_thread
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
)
from sqlmodel import Session, select

from app.core.redis_client import cache_set, is_processed, mark_processed
from app.db.session import get_engine
from app.models import Cocktail, CocktailIngredient, Ingredient

logger = logging.getLogger("scripts.refresh")

DEFAULT_AI_SERVICE_URL = "http://localhost:8001"
DEFAULT_MOOD = "balanced"
DEFAULT_PREFERENCES = "refresh this recipe"
REQUEST_TIMEOUT_SECONDS = 30.0
CACHE_TTL_SECONDS = 3600
IDEMPOTENCY_TTL_SECONDS = 86400
MAX_CONCURRENT_REQUESTS = 5
RETRY_DELAYS_SECONDS = (1, 2, 4)


@dataclass(slots=True)
class CocktailWorkItem:
    id: int
    name: str
    ingredients: list[str]


@dataclass(slots=True)
class RefreshStats:
    total: int = 0
    processed: int = 0
    skipped: int = 0
    failed: int = 0


def _log(event: str, **fields: object) -> None:
    payload: dict[str, object] = {"event": event, **fields}
    logger.info(json.dumps(payload, sort_keys=True))


def _load_cocktails_sync() -> list[CocktailWorkItem]:
    engine = get_engine()
    with Session(engine) as session:
        cocktails = session.exec(select(Cocktail)).all()
        items: list[CocktailWorkItem] = []

        for cocktail in cocktails:
            if cocktail.id is None:
                continue

            link_rows = session.exec(
                select(CocktailIngredient).where(
                    CocktailIngredient.cocktail_id == cocktail.id
                )
            ).all()
            ingredients: list[str] = []
            for link in link_rows:
                ingredient = session.get(Ingredient, link.ingredient_id)
                if ingredient is not None:
                    ingredients.append(ingredient.name)
            ingredients.sort()

            items.append(
                CocktailWorkItem(
                    id=cocktail.id,
                    name=cocktail.name,
                    ingredients=ingredients,
                )
            )

        return items


async def load_cocktails() -> list[CocktailWorkItem]:
    return await to_thread.run_sync(_load_cocktails_sync)


async def call_ai_mix_endpoint(
    client: httpx.AsyncClient,
    *,
    ai_service_url: str,
    ingredients: list[str],
    mood: str,
    preferences: str,
) -> dict[str, object]:
    response = await client.post(
        f"{ai_service_url.rstrip('/')}/mix",
        json={
            "ingredients": ingredients,
            "mood": mood,
            "preferences": preferences,
        },
    )
    _ = response.raise_for_status()
    payload = cast(object, response.json())
    if not isinstance(payload, dict):
        raise ValueError("AI service returned non-object JSON")
    payload_dict = cast(dict[object, object], payload)
    normalized_payload: dict[str, object] = {}
    for key, value in payload_dict.items():
        normalized_payload[str(key)] = value
    return normalized_payload


async def refresh_one_cocktail(
    item: CocktailWorkItem,
    *,
    semaphore: asyncio.Semaphore,
    client: httpx.AsyncClient,
    ai_service_url: str,
    mood: str,
    preferences: str,
    is_processed_fn: Callable[[str], bool] = is_processed,
    mark_processed_fn: Callable[[str, int], bool] = mark_processed,
    cache_set_fn: Callable[[str, str, int], bool] = cache_set,
) -> str:
    idempotency_key = f"cocktail:{item.id}"

    already_processed = await to_thread.run_sync(is_processed_fn, idempotency_key)
    if already_processed:
        _log(
            "cocktail_skipped",
            cocktail_id=item.id,
            cocktail_name=item.name,
            reason="already_processed",
        )
        return "skipped"

    if not item.ingredients:
        _log(
            "cocktail_skipped",
            cocktail_id=item.id,
            cocktail_name=item.name,
            reason="no_ingredients",
        )
        return "skipped"

    async with semaphore:
        start = perf_counter()
        for attempt_index in range(len(RETRY_DELAYS_SECONDS) + 1):
            try:
                suggestion = await call_ai_mix_endpoint(
                    client,
                    ai_service_url=ai_service_url,
                    ingredients=item.ingredients,
                    mood=mood,
                    preferences=preferences,
                )
                _ = await to_thread.run_sync(
                    cache_set_fn,
                    f"ai:suggestion:cocktail:{item.id}",
                    json.dumps(suggestion),
                    CACHE_TTL_SECONDS,
                )
                _ = await to_thread.run_sync(
                    mark_processed_fn,
                    idempotency_key,
                    IDEMPOTENCY_TTL_SECONDS,
                )

                elapsed_ms = round((perf_counter() - start) * 1000, 2)
                _log(
                    "cocktail_refreshed",
                    cocktail_id=item.id,
                    cocktail_name=item.name,
                    attempt=attempt_index + 1,
                    elapsed_ms=elapsed_ms,
                )
                return "processed"
            except Exception as exc:  # noqa: BLE001
                is_last_attempt = attempt_index >= len(RETRY_DELAYS_SECONDS)
                if is_last_attempt:
                    elapsed_ms = round((perf_counter() - start) * 1000, 2)
                    _log(
                        "cocktail_failed",
                        cocktail_id=item.id,
                        cocktail_name=item.name,
                        attempts=attempt_index + 1,
                        elapsed_ms=elapsed_ms,
                        error=str(exc),
                    )
                    return "failed"

                backoff_delay = RETRY_DELAYS_SECONDS[attempt_index]
                _log(
                    "cocktail_retry_scheduled",
                    cocktail_id=item.id,
                    cocktail_name=item.name,
                    attempt=attempt_index + 1,
                    retry_in_seconds=backoff_delay,
                    error=str(exc),
                )
                await asyncio.sleep(backoff_delay)

    return "failed"


async def refresh_cocktails(
    cocktails: list[CocktailWorkItem],
    *,
    ai_service_url: str,
    mood: str,
    preferences: str,
    max_concurrent: int = MAX_CONCURRENT_REQUESTS,
    is_processed_fn: Callable[[str], bool] = is_processed,
    mark_processed_fn: Callable[[str, int], bool] = mark_processed,
    cache_set_fn: Callable[[str, str, int], bool] = cache_set,
) -> RefreshStats:
    stats = RefreshStats(total=len(cocktails))
    if not cocktails:
        return stats

    semaphore = asyncio.Semaphore(max_concurrent)
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        with Progress(
            TextColumn("[bold blue]Refreshing cocktails"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            transient=False,
        ) as progress:
            task_id = progress.add_task("refresh", total=len(cocktails))

            async def _worker(item: CocktailWorkItem) -> str:
                result = await refresh_one_cocktail(
                    item,
                    semaphore=semaphore,
                    client=client,
                    ai_service_url=ai_service_url,
                    mood=mood,
                    preferences=preferences,
                    is_processed_fn=is_processed_fn,
                    mark_processed_fn=mark_processed_fn,
                    cache_set_fn=cache_set_fn,
                )
                progress.advance(task_id, 1)
                return result

            results = await asyncio.gather(*[_worker(item) for item in cocktails])

    for result in results:
        if result == "processed":
            stats.processed += 1
        elif result == "skipped":
            stats.skipped += 1
        else:
            stats.failed += 1

    return stats


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    ai_service_url = os.getenv("POTION_AI_SERVICE_URL", DEFAULT_AI_SERVICE_URL)
    mood = os.getenv("POTION_AI_MOOD", DEFAULT_MOOD)
    preferences = os.getenv("POTION_AI_PREFERENCES", DEFAULT_PREFERENCES)

    _log(
        "refresh_started",
        ai_service_url=ai_service_url,
        max_concurrent=MAX_CONCURRENT_REQUESTS,
    )
    cocktails = await load_cocktails()
    stats = await refresh_cocktails(
        cocktails,
        ai_service_url=ai_service_url,
        mood=mood,
        preferences=preferences,
    )

    _log(
        "refresh_finished",
        total=stats.total,
        processed=stats.processed,
        skipped=stats.skipped,
        failed=stats.failed,
    )


if __name__ == "__main__":
    asyncio.run(main())
