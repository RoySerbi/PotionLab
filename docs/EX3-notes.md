# EX3 Engineering Notes — PotionLab

This document is the engineering companion for the EX3 final submission. It explains how the services are orchestrated, captures a Redis trace from a real `scripts/refresh.py` run, and documents the operational steps (JWT rotation, health checks, etc.) that a teammate would need on day one.

---

## 1. Service Topology

PotionLab is composed of **five cooperating processes**, all launched via a single `docker compose up --build -d`:

| Service        | Image / Build           | Internal port | Host port | Purpose                                                                 |
| -------------- | ----------------------- | ------------- | --------- | ----------------------------------------------------------------------- |
| `api`          | `Dockerfile`            | 8000          | 8000      | FastAPI backend (CRUD for cocktails / ingredients / flavor tags + JWT). |
| `db`           | `postgres:16-alpine`    | 5432          | 5432      | Persistent storage; SQLModel migrations seeded via `scripts/seed.py`.   |
| `redis`        | `redis:7-alpine`        | 6379          | 6379      | Cache + idempotency keys for the async refresh worker.                  |
| `ai_service`   | `Dockerfile.ai`         | 8001          | 8001      | Standalone microservice wrapping Google Gemini (`/mix`, `/substitute`). |
| `streamlit`    | `Dockerfile.streamlit`  | 8501          | 8501      | User-facing dashboard. Talks to `api` and `ai_service` over the bridge. |

### Service dependencies

```
streamlit ──▶ api ──▶ db
                └──▶ redis ◀── ai_service
scripts/refresh.py ──▶ ai_service ──▶ redis (idempotency + cache)
                      └──▶ db (read cocktails)
```

`api` waits for `db` and `redis` health checks before starting. `streamlit` waits for `api`'s `/health` healthcheck.

---

## 2. Async Refresh Worker (`scripts/refresh.py`)

The refresher demonstrates the Session 09 deliverable. Key properties:

| Concern              | Implementation                                                                                        |
| -------------------- | ----------------------------------------------------------------------------------------------------- |
| Bounded concurrency  | `asyncio.Semaphore(MAX_CONCURRENT_REQUESTS=5)`                                                        |
| Retries              | Exponential-ish backoff: `RETRY_DELAYS_SECONDS = (1, 2, 4)` — up to 4 total attempts per cocktail.    |
| Idempotency          | Redis key `cocktail:<id>` set via `mark_processed(..., 86400)`; checked with `is_processed` per item. |
| Caching              | Successful AI responses cached at `ai:suggestion:cocktail:<id>` for 1 hour (`CACHE_TTL_SECONDS`).     |
| Observability        | Structured JSON log lines (`event=cocktail_refreshed`, `elapsed_ms=...`).                             |
| Tests                | `tests/test_refresh.py` (`pytest.mark.anyio`) covers happy path, skip-on-idempotent, retry-then-fail. |

Run it locally against the live stack:

```bash
docker compose up --build -d
docker compose exec api python scripts/seed.py
uv run python scripts/refresh.py
```

### Redis trace excerpt

Captured with `docker compose exec redis redis-cli MONITOR` while `scripts/refresh.py` was processing a freshly seeded database (22 cocktails). Truncated for brevity.

**First run** (clean Redis, AI service quota available):

```
1779653632.775022 [0 172.19.0.3:43920] "EXISTS" "processed:cocktail:1"
1779653632.799343 [0 172.19.0.3:43956] "EXISTS" "processed:cocktail:2"
1779653632.812011 [0 172.19.0.3:43920] "EXISTS" "processed:cocktail:3"
1779653633.412905 [0 172.19.0.3:43920] "SETEX" "ai:suggestion:cocktail:1" "3600" "{\"name\":\"Refreshed Negroni\",\"ingredients\":[...],\"instructions\":\"Stir...\"}"
1779653633.413188 [0 172.19.0.3:43920] "SETEX" "processed:cocktail:1"     "86400" "1"
1779653633.612042 [0 172.19.0.3:43956] "SETEX" "ai:suggestion:cocktail:2" "3600" "{\"name\":\"Refreshed Daiquiri\",...}"
1779653633.612311 [0 172.19.0.3:43956] "SETEX" "processed:cocktail:2"     "86400" "1"
...
```

**Second run** (immediately after — idempotency short-circuits every item):

```
1779653640.118012 [0 172.19.0.3:44102] "EXISTS" "processed:cocktail:1"   # → 1
1779653640.118511 [0 172.19.0.3:44102] "EXISTS" "processed:cocktail:2"   # → 1
1779653640.118905 [0 172.19.0.3:44102] "EXISTS" "processed:cocktail:3"   # → 1
... no SETEX writes ...
```

Key observations:

1. The first pass produces exactly two writes per cocktail — a `SETEX ai:suggestion:cocktail:<id>` for the AI response cache (1-hour TTL) and a `SETEX processed:cocktail:<id>` for the idempotency marker (24-hour TTL). The `processed:` prefix is added inside `mark_processed` (`src/app/core/redis_client.py:72`).
2. On a subsequent invocation, `EXISTS processed:cocktail:<id>` short-circuits before any HTTP request reaches `ai_service` — that's the idempotency contract.
3. Concurrency is visibly bounded: no more than five in-flight writes overlap in any 100 ms window (`MAX_CONCURRENT_REQUESTS = 5` in `scripts/refresh.py:36`).

> ⚠️ **If `refresh.py` reports `failed=22`:** the Gemini free tier rate-limits aggressive bursts. Wait a minute and re-run, or `docker compose exec redis redis-cli FLUSHDB` if the idempotency keys from a previous successful run are masking activity.

---

## 3. Security Baseline (Session 11)

| Control                  | Where                                       | Notes                                                                       |
| ------------------------ | ------------------------------------------- | --------------------------------------------------------------------------- |
| Password hashing         | `src/app/core/security.py` — `hash_password`| bcrypt via `passlib.context.CryptContext(schemes=["bcrypt"])`.              |
| JWT signing              | `create_access_token`                       | HS256 (configurable), secret from `POTION_JWT_SECRET`, default 60 min TTL.  |
| Auth dependency          | `require_auth`                              | Rejects missing / malformed / expired tokens with 401.                      |
| Role-based authorization | `require_role("admin")`                     | Returns 403 when `payload.role` is not in the allowed set.                  |
| Protected routes         | `src/app/api/v1/routes_auth.py`             | `/auth/token` (login), `/auth/me`, plus admin-only routes wired via `require_role`. |
| Negative tests           | `tests/api/test_auth.py`                    | Asserts 401 on missing/expired tokens and 403 on insufficient scope.        |

### JWT secret rotation runbook

1. Generate a new secret locally and keep it next to the old one for the rollover window:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```
2. Update `.env`:
   ```env
   POTION_JWT_SECRET=<new-secret>
   ```
3. Restart only the API (db / redis / ai_service keep running):
   ```bash
   docker compose up -d --no-deps --build api
   ```
4. All previously issued tokens are now invalid; users will receive 401 and must re-authenticate via `POST /api/v1/auth/token`.
5. Verify rotation:
   ```bash
   # Old token should fail
   curl -i -H "Authorization: Bearer $OLD_TOKEN" http://localhost:8000/api/v1/auth/me   # expect 401
   # New login should succeed
   curl -i -X POST http://localhost:8000/api/v1/auth/token \
        -H 'Content-Type: application/json' \
        -d '{"username":"admin","password":"admin123"}'
   ```

For production-style rotation we would publish the new secret to all replicas first, accept tokens signed by either secret for the overlap window, and then retire the old key — out of scope for the local KISS deliverable but noted for completeness.

---

## 3.5. Rate Limiting

A global rate limit protects every route on `api` from abuse and from accidental
test-loop stampedes. It is implemented with [`slowapi`](https://github.com/laurentS/slowapi)
in `src/app/main.py:30-53`.

| Concern        | Value                                                                                  |
| -------------- | -------------------------------------------------------------------------------------- |
| Default limit  | **60 requests / minute / client IP** (`["60/minute"]`)                                 |
| Key function   | `slowapi.util.get_remote_address` — uses `request.client.host`                          |
| Storage        | In-memory (per-process). Suitable for the single-replica KISS deployment.              |
| Wiring         | `Limiter(default_limits=...)` + `app.add_middleware(SlowAPIMiddleware)`                |
| Test bypass    | `POTION_DISABLE_RATE_LIMIT=1` or `PYTEST_CURRENT_TEST` env var → limit set to 1 000 000 |
| 429 response   | `{"error":"Rate limit exceeded: 60 per 1 minute"}` with HTTP status `429`              |

### Verifying it works (real capture)

```bash
$ for i in $(seq 1 70); do
    curl -s -o /dev/null -w "%{http_code} " http://localhost:8000/api/v1/cocktails
  done | tr ' ' '\n' | sort | uniq -c
     60 200
     10 429

$ curl -i http://localhost:8000/api/v1/cocktails
HTTP/1.1 429 Too Many Requests
date: Sun, 24 May 2026 20:26:36 GMT
server: uvicorn
content-length: 48
content-type: application/json

{"error":"Rate limit exceeded: 60 per 1 minute"}
```

> **Note on headers:** the default slowapi handler does **not** emit
> `X-RateLimit-Limit` / `Retry-After` headers (verified with `curl -D -`).
> Enabling them would require passing `headers_enabled=True` to `Limiter(...)`;
> for the EX3 KISS scope we expose the limit only through the 429 body. Clients
> should treat any 429 as "back off ≥1 s and retry"; this is exactly what
> `scripts/refresh.py` already does via `RETRY_DELAYS_SECONDS = (1, 2, 4)`.

---

## 4. Enhancement: "What Can I Make?" + AI Mixologist

PotionLab's chosen enhancement is a two-part flavor-matching workflow:

1. **Pantry matcher** (Streamlit page "What Can I Make?"): the user ticks the ingredients they have on hand; the UI splits the catalogue into recipes that can be made *now* and recipes that are "Almost There" (missing 1–2 items). Missing items are surfaced as a shopping list.
2. **AI Mixologist** (`ai_service`): a separate FastAPI process that calls Google Gemini to (a) suggest a brand-new recipe from a list of ingredients + a mood, and (b) propose substitutions when the user is missing something.

Coverage:

- `tests/ai_service/test_gemini_client.py` mocks Gemini and asserts schema-correct outputs.
- `tests/test_refresh.py` exercises the async pipeline that fan-out the AI calls across the catalogue.
- `tests/integration/test_compose_stack.py` smoke-tests that the live Compose stack returns 200 on `/health` for both `api` and `ai_service`.

---

## 5. Demo script

`scripts/demo.sh` walks a grader through:

1. Bringing up the Compose stack and waiting for healthchecks.
2. Seeding the database.
3. Hitting key API endpoints with `curl`.
4. Launching Streamlit and pointing the user at the dashboard URL.
5. Triggering the AI refresh worker and printing a snippet of the resulting Redis state.

Run it from the repo root:

```bash
bash scripts/demo.sh
```

## 6. End-to-end demo recording

A full screen capture of the stack in action is committed at [`docs/demo.webm`](demo.webm). It walks through:

1. `docker compose up --build -d` and waiting for every service to report `healthy`.
2. Seeding the database (`scripts/seed.py`) and exercising both public `GET` routes and JWT-protected mutations via `curl`.
3. The Streamlit dashboard: Cocktail Browser, Ingredient Explorer, "Mix a Cocktail", and the "What Can I Make?" pantry matcher.
4. The AI Mixologist microservice generating a recipe via `/mix`.
5. Running `scripts/refresh.py` and inspecting the resulting Redis state with `redis-cli MONITOR` — both the first pass (writes) and a second pass (idempotency short-circuit).

> The clip is slightly longer than the rubric's 2-minute suggestion; this was approved by the instructor in advance.
