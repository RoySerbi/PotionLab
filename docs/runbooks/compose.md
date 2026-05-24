# Compose Runbook — PotionLab

This runbook is the single source of truth for operating the PotionLab Docker Compose stack: launch, verify, debug, and tear down. It assumes Docker Engine ≥ 24 and Docker Compose v2.

---

## 1. Prerequisites

- Docker Desktop (or Docker Engine + the `docker compose` plugin) running.
- A populated `.env` file at the repo root (copy from `.env.example`):
  ```env
  GOOGLE_API_KEY=<your-gemini-api-key>
  POSTGRES_PASSWORD=<choose-a-password>
  POTION_JWT_SECRET=<long-random-string>
  ```
- Free TCP ports: 8000, 8001, 8501, 5432, 6379.

---

## 2. Launching the stack

From the repo root:

```bash
docker compose up --build -d
```

Wait ~30–60 seconds for the Postgres and Redis health checks to flip to `healthy`, then for the API to become reachable.

Check the per-service status:

```bash
docker compose ps
```

Expected output (abridged):

```
NAME                    STATUS                   PORTS
potionlab-api-1         Up (healthy)             0.0.0.0:8000->8000/tcp
potionlab-ai_service-1  Up                       0.0.0.0:8001->8001/tcp
potionlab-db-1          Up (healthy)             0.0.0.0:5432->5432/tcp
potionlab-redis-1       Up (healthy)             0.0.0.0:6379->6379/tcp
potionlab-streamlit-1   Up                       0.0.0.0:8501->8501/tcp
```

Seed the database (only needed once per fresh volume):

```bash
docker compose exec api python scripts/seed.py
```

---

## 3. Health verification

```bash
# Backend API liveness
curl -s http://localhost:8000/health
# {"status":"ok"}

# AI Mixologist liveness
curl -s http://localhost:8001/health
# {"status":"ok"}

# Postgres ready
docker compose exec db pg_isready -U postgres
# /var/run/postgresql:5432 - accepting connections

# Redis ready
docker compose exec redis redis-cli ping
# PONG

# Streamlit dashboard
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8501
# 200
```

### Sanity-check an authenticated route

The seed script creates a default admin user: **`admin` / `admin123`**.
Mutating endpoints (`POST` / `PUT` / `DELETE`) require a bearer token;
`GET` endpoints are public.

```bash
# Login → grab token (note the endpoint is /auth/token, not /auth/login)
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/token \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}' | jq -r .access_token)

# Use it
curl -i -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/auth/me
```

A request **without** the header (or with an expired token) should return `401 Unauthorized`; a token with the wrong role should return `403 Forbidden`. Both behaviors are covered by `tests/api/test_auth.py`.

### Rate-limit headers

Rate limiting is enabled via `slowapi` middleware (default: **60 requests / minute / client IP**, see `src/app/main.py`). Every response carries:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
X-RateLimit-Reset: 1719655412
```

Inspect them with:

```bash
curl -i http://localhost:8000/api/v1/cocktails/ | grep -i X-RateLimit
```

When the limit is exceeded the API responds with `429 Too Many Requests`.

---

## 4. Running tests and Schemathesis

### Unit + integration tests

Inside the API container (matches the CI image exactly):

```bash
docker compose exec api uv run pytest -q
docker compose exec api uv run pytest --cov=src --cov-report=term-missing
```

Locally with `uv` (faster feedback loop):

```bash
uv run pytest -q
```

The `tests/test_refresh.py` suite uses `@pytest.mark.anyio` and exercises the bounded-concurrency / idempotency / retry paths of `scripts/refresh.py`.

### Schemathesis (contract testing)

While the stack is up:

```bash
uv tool run schemathesis run \
  --checks all \
  --hypothesis-max-examples=25 \
  http://localhost:8000/openapi.json
```

This walks every operation in the OpenAPI schema and flags 5xx responses, schema violations, and stateful contract issues. Use it as a quick smoke pass before submitting.

### CI sketch

A minimal GitHub Actions job would:

1. Check out the code.
2. Install `uv`.
3. `uv sync`
4. `uv run pytest -q`
5. Spin up the Compose stack (`docker compose up --build -d`) and run `schemathesis` against `http://localhost:8000/openapi.json`.
6. Tear the stack down with `docker compose down -v`.

---

## 5. Triggering the async refresh worker

```bash
# Inside the api container (has app + scripts on PYTHONPATH)
docker compose exec api python scripts/refresh.py
```

Watch Redis activity in a second terminal:

```bash
docker compose exec redis redis-cli MONITOR
```

Expect to see paired writes per cocktail (`SET ai:suggestion:cocktail:<id> ... EX 3600` and `SET cocktail:<id> ... EX 86400 NX`). On a second invocation, every cocktail short-circuits at the `EXISTS cocktail:<id>` check — that's the idempotency contract in action.

A captured trace lives in `docs/EX3-notes.md` (§2).

---

## 6. Common operations

### Tail logs for a single service

```bash
docker compose logs -f api
docker compose logs -f ai_service
```

### Rebuild after a code change

```bash
docker compose up -d --no-deps --build api
```

### Reset the database (destroys data)

```bash
docker compose down -v
docker compose up --build -d
docker compose exec api python scripts/seed.py
```

### Tear everything down

```bash
docker compose down          # keep volumes
docker compose down -v       # also delete postgres data
```

---

## 7. Troubleshooting

| Symptom                                       | Likely cause                                                  | Fix                                                                                              |
| --------------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `api` stuck `unhealthy`                       | Postgres still initialising; `POTION_DATABASE_URL` wrong.     | `docker compose logs db api`; confirm `POSTGRES_PASSWORD` matches between `.env` and `compose.yaml`. |
| `ai_service` returns 500 on `/mix`            | `GOOGLE_API_KEY` missing or quota exceeded.                   | Check `.env`; rotate or top up the key.                                                          |
| `scripts/refresh.py` reports `0 processed`    | Idempotency keys already set from a previous run.             | `docker compose exec redis redis-cli FLUSHDB` (dev only).                                        |
| Port already in use (8000 / 8501 / 5432)      | Another local service holds the port.                         | Stop the offender or change the host-side port in `compose.yaml`.                                |
| Streamlit shows "connection refused"          | API container not yet healthy.                                | `docker compose ps` until `api` is `(healthy)`.                                                  |
| JWT routes always 401 after rotation          | Old tokens cached in the browser / Streamlit session.         | Log out and log back in; see `docs/EX3-notes.md` §3 rotation runbook.                            |

If a problem isn't on this list, capture `docker compose ps`, `docker compose logs --since=5m`, and the failing `curl` output, then open an issue with the session number in the title.
