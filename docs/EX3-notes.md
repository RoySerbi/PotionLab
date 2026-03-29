# EX3 Notes — AI Mixologist Microservice

## AI Integration Approach

- Added a standalone FastAPI microservice under `ai_service/` with two endpoints:
  - `POST /mix` for cocktail generation
  - `GET /health` for service health
- Gemini integration lives in `ai_service/gemini_client.py`.
- Request and response are strictly validated through Pydantic models in `ai_service/schemas.py`.
- Gemini is called with JSON-only structured output and parsed into `CocktailSuggestion` before returning.

## Rate Limiting Strategy (15 RPM)

- Implemented client-side rate limiting with Redis sorted set (`ai:mixologist:requests`).
- Sliding window logic:
  1. Remove entries older than 60 seconds.
  2. Count current window entries.
  3. Reject with `429 Rate limit exceeded` when count reaches 15.
  4. Record current request timestamp and set key expiry.

## Redis Caching Behavior

- Cache key format: `cocktail:{md5(hash of sorted ingredients + mood + preferences)}`.
- Cache lookup runs before rate limit + Gemini call.
- Cached values are serialized `CocktailSuggestion` JSON.
- TTL is 3600 seconds.
- Verified by making identical `/mix` calls and observing lower response time plus Redis key presence.

## Example AI Response

```json
{
  "name": "Gin Tonic Highball",
  "ingredients": [
    {"ingredient": "gin", "amount": "1 oz"},
    {"ingredient": "tonic", "amount": "1 oz"}
  ],
  "instructions": "Build over ice and stir gently.",
  "flavor_profile": ["balanced", "refreshing"],
  "why_this_works": "Ingredients complement each other through acidity, sweetness, and aroma balance."
}
```

## Docker Compose Integration

- Added `ai_service` to `compose.yaml`:
  - Build from `Dockerfile.ai`
  - Expose port `8001`
  - Inject `GOOGLE_API_KEY` and `POTION_REDIS_URL`
  - Depend on healthy Redis service

## Refresh Script Execution Log

```text
2026-03-29 22:07:38,557 INFO {"ai_service_url": "http://localhost:8001", "event": "refresh_started", "max_concurrent": 5}
2026-03-29 22:07:38,613 INFO {"cocktail_id": 1, "cocktail_name": "Negroni", "event": "cocktail_skipped", "reason": "already_processed"}
2026-03-29 22:07:38,614 INFO {"cocktail_id": 4, "cocktail_name": "Daiquiri", "event": "cocktail_skipped", "reason": "already_processed"}
2026-03-29 22:07:38,629 INFO {"attempt": 1, "cocktail_id": 11, "cocktail_name": "Espresso Martini", "elapsed_ms": 16.06, "event": "cocktail_refreshed"}
2026-03-29 22:07:38,670 INFO {"event": "refresh_finished", "failed": 0, "processed": 8, "skipped": 15, "total": 23}
Refreshing cocktails ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 23/23 0:00:00
```
