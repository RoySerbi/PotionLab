# PotionLab — Cocktail Recipe Engine & Flavor Chemistry Workbench

[![CI](https://github.com/EASS-HIT-PART-A-2026-CLASS-IX/PotionLab/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/EASS-HIT-PART-A-2026-CLASS-IX/PotionLab/actions/workflows/ci.yml)

PotionLab is a full-stack cocktail recipe engine packaged as a five-service local stack: a **FastAPI** backend (CRUD + JWT/RBAC + rate limiting), **PostgreSQL** for persistence, **Redis** for caching and async idempotency, a separate **AI Mixologist** microservice powered by **Google Gemini**, and a **Streamlit** dashboard. An async refresh worker (`scripts/refresh.py`) fans out AI calls with bounded concurrency, retries, and Redis-backed idempotency. Everything is orchestrated by a single `docker compose up`; the test suite covers CRUD, auth, RBAC, the async worker, and a live Schemathesis contract pass in CI.

The chosen domain is mixology: the API manages cocktails, ingredients, and flavor profiles; the dashboard ships a "What Can I Make?" pantry matcher; the AI service generates new recipes and suggests substitutions.

## For Graders

- **End-to-end demo video:** [`docs/demo.webm`](docs/demo.webm) — full walkthrough of the Compose stack, JWT auth, Streamlit dashboard, AI Mixologist, and the async refresh worker.
- **EX3 engineering notes:** [`docs/EX3-notes.md`](docs/EX3-notes.md) — service topology, Redis trace excerpt, JWT rotation runbook, rate-limit contract, and enhancement details.
- **Compose runbook:** [`docs/runbooks/compose.md`](docs/runbooks/compose.md) — launch / verify / debug / tear down.
- **Final submission tag:** [`ex3-final`](https://github.com/EASS-HIT-PART-A-2026-CLASS-IX/PotionLab/releases/tag/ex3-final).

## Prerequisites

- Python 3.12+
- `uv` (modern Python package manager): [Installation Guide](https://docs.astral.sh/uv/getting-started/installation/)
- Docker Engine 24.0+ and Docker Compose v2 (for containerized stack)
- Minimum 2GB RAM (recommended for full stack)
- Google Gemini API Key: [Get an API Key](https://makersuite.google.com/app/apikey)

## Quick Start

### Option 1: Docker Compose Stack (Recommended for EX3)

1. **Clone and navigate to the project**:
   ```bash
   git clone https://github.com/EASS-HIT-PART-A-2026-CLASS-IX/PotionLab.git
   cd PotionLab
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and set GOOGLE_API_KEY and POSTGRES_PASSWORD
   ```

3. **Start all services**:
   ```bash
   docker compose up --build -d
   ```

4. **Wait for services to become healthy** (30-60 seconds):
   ```bash
   docker compose ps
   ```
   All services should show "Up (healthy)" status.

5. **Seed the database** (inside the API container):
   ```bash
   docker compose exec api python scripts/seed.py
   ```

6. **Verify the stack is working**:
   ```bash
   curl http://localhost:8000/health          # → {"status":"ok","redis":"connected"}
   curl http://localhost:8001/health          # → {"status":"ok","service":"ai-mixologist"}
   curl http://localhost:8000/api/v1/cocktails  # public GET, no auth
   ```

   The seed script also creates a default admin user (`admin` / `admin123`).
   Mutating endpoints (`POST` / `PUT` / `DELETE`) require a bearer token:

   ```bash
   TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/token \
     -H 'Content-Type: application/json' \
     -d '{"username":"admin","password":"admin123"}' | jq -r .access_token)

   curl -X POST http://localhost:8000/api/v1/cocktails \
     -H "Authorization: Bearer $TOKEN" \
     -H 'Content-Type: application/json' \
     -d '{"name":"Test","instructions":"Stir"}'
   ```

   See [`docs/EX3-notes.md`](docs/EX3-notes.md) for the full security model
   and the rate-limit contract (60 requests / minute / client IP).

7. **Open the Streamlit dashboard** at <http://localhost:8501> — it is
   already running as a Compose service; no extra command needed.

8. **One-command end-to-end smoke test** (optional but recommended for graders):
   ```bash
   bash scripts/demo.sh
   ```
   This walks through health checks, auth, a JWT-protected mutation,
   the AI Mixologist, and the async refresh worker in a single run.

### Option 2: Local Development (Without Docker)

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Set up environment**:
   ```bash
   cp .env.example .env
   mkdir -p data
   # POTION_DATABASE_URL defaults to SQLite (data/app.db)
   ```

3. **Start Redis** (required for AI features):
   ```bash
   # If you have Redis installed locally
   redis-server
   # OR use Docker for just Redis
   docker run -d -p 6379:6379 redis:7-alpine
   ```

4. **Run database migrations** (if needed):
   ```bash
   uv run python scripts/init_db.py
   ```

5. **Seed the database**:
   ```bash
   uv run python scripts/seed.py
   ```

6. **Start the API server**:
   ```bash
   uv run uvicorn app.main:app --reload --app-dir src
   ```

7. **In a separate terminal, start Streamlit**:
   ```bash
   uv run streamlit run streamlit_app.py
   ```

   > Note: `--app-dir src` is technically redundant because `uv sync`
   > installs the package in editable mode, but it makes the import path
   > explicit and works in either case.

## API Endpoints

The API is versioned under `/api/v1/`.

| Method | Path | Description |
| :--- | :--- | :--- |
| **GET** | `/health` | Liveness check (returns `{"status":"ok","redis":"connected"}`) |
| **POST** | `/api/v1/flavor-tags/` | Create a new flavor profile tag |
| **GET** | `/api/v1/flavor-tags/` | List all available flavor tags |
| **GET** | `/api/v1/flavor-tags/{id}` | Get detailed flavor tag information |
| **PUT** | `/api/v1/flavor-tags/{id}` | Update an existing flavor tag |
| **DELETE** | `/api/v1/flavor-tags/{id}` | Remove a flavor tag |
| **POST** | `/api/v1/ingredients/` | Create a new ingredient with flavor tags |
| **GET** | `/api/v1/ingredients/` | List all ingredients |
| **GET** | `/api/v1/ingredients/{id}` | Get ingredient detail with tags |
| **PUT** | `/api/v1/ingredients/{id}` | Update ingredient properties |
| **DELETE** | `/api/v1/ingredients/{id}` | Remove an ingredient |
| **POST** | `/api/v1/cocktails/` | Create a cocktail with nested ingredients |
| **GET** | `/api/v1/cocktails/` | List all cocktails |
| **GET** | `/api/v1/cocktails/{id}` | Get cocktail with full ingredient list |
| **PUT** | `/api/v1/cocktails/{id}` | Update cocktail recipe or metadata |
| **DELETE** | `/api/v1/cocktails/{id}` | Remove a cocktail from the library |

## Streamlit Dashboard

The Streamlit dashboard provides a visual interface for the PotionLab API, enabling flavor discovery and recipe management. In the Docker Compose stack (Option 1 above) it runs automatically as the `streamlit` service on <http://localhost:8501> — no extra command needed.

### Running the dashboard locally (without Docker)

If you are following Option 2 (local development), launch the API and Streamlit in two terminals:

```bash
# Terminal 1: Start the Backend API
uv run uvicorn app.main:app --reload --app-dir src

# Terminal 2: Start the Streamlit Dashboard
uv run streamlit run streamlit_app.py
```

### Dashboard Features

#### Cocktail Browser
- Browse the full cocktail library with search and difficulty filters.
- Visualize collection-wide flavor trends with an aggregate flavor wheel.
- View detailed recipe information and per-cocktail flavor radar charts.

#### Ingredient Explorer
- Explore the ingredient database via a categorized grid layout.
- Filter ingredients by type and view associated flavor profiles.
- Discover which cocktails use a specific ingredient with one-click filtering.

#### Mix a Cocktail
- A dynamic, multi-step form for creating new cocktail recipes.
- Real-time ingredient row management (add/remove).
- Built-in form validation and recipe persistence to the backend.

#### What Can I Make?
- Select ingredients from your home bar to see what you can mix.
- Matches are split between recipes you can make immediately and those where you're "Almost There" (missing 1-2 items).
- Missing ingredients are highlighted to help plan your next grocery trip.

## EX3: Docker Compose Stack & AI Integration

The full PotionLab stack is containerized using Docker Compose, providing a robust environment with persistent storage, caching, and an AI-powered mixologist microservice.

### Launching the Stack

See the [Quick Start](#quick-start) guide above for complete setup instructions.

To start all services (API, AI Service, Postgres, Redis, Streamlit):

```bash
docker compose up --build -d
```

The services will be available at:
- **API**: <http://localhost:8000>
- **AI Mixologist**: <http://localhost:8001>
- **Streamlit Dashboard**: <http://localhost:8501> (runs automatically as a Compose service)

### Environment Variables

Ensure these variables are set in your `.env` file (see `.env.example`):

| Variable | Description | Default |
| :--- | :--- | :--- |
| `GOOGLE_API_KEY` | Gemini API key for AI generation | (Required) |
| `POTION_REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `POTION_JWT_SECRET` | Secret key for JWT signing | `change-me-in-production` |
| `POTION_DATABASE_URL` | Database connection string | (SQLite if unset) |

### Service Ports

| Service | Host Port | Internal Port |
| :--- | :--- | :--- |
| **API** | 8000 | 8000 |
| **AI Mixologist** | 8001 | 8001 |
| **Postgres** | 5432 | 5432 |
| **Redis** | 6379 | 6379 |
| **Streamlit** | 8501 | 8501 |

## Testing

Run the full test suite (**124 tests** covering CRUD operations, JWT auth, role-based authorization, the async refresh worker, and the AI service):
```bash
uv run pytest -q
```

To check test coverage:
```bash
uv run pytest --cov=src --cov-report=term-missing
```

## REST Client Playground

An `examples.http` file is provided for use with the [VS Code REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) extension. It contains ready-to-run requests for all primary API operations.

## Troubleshooting

### Docker Compose Issues

**Services won't start:**
- Check Docker is running: `docker --version`
- Check ports are available: `lsof -i :8000 -i :8001 -i :5432 -i :6379`
- Check logs: `docker compose logs <service-name>`

**Build failures:**
- Clear Docker cache: `docker compose build --no-cache`
- Check internet connectivity for package downloads

**Database connection errors:**
- Wait 30 seconds after `docker compose up` for PostgreSQL to initialize
- Verify `POSTGRES_PASSWORD` is set in `.env` — `compose.yaml` reads it via env substitution, so you do **not** need to edit `compose.yaml` itself.

### Local Development Issues

**Import errors:**
- Ensure virtual environment is activated or using `uv run`
- Reinstall dependencies: `uv sync`

**Redis connection errors:**
- Check Redis is running: `redis-cli ping` should return `PONG`
- Verify POTION_REDIS_URL in .env matches Redis location

## AI Assistance

This project was developed with the help of AI (Claude Code).

AI was used as a pair-programming assistant throughout the project — every design decision, architectural choice, and final implementation was made and reviewed by me. The AI accelerated specific tasks but did not replace the engineering work:

- **Architectural design**: I decided on the five-service topology (FastAPI + Postgres + Redis + AI microservice + Streamlit), the SQLModel schema, the many-to-many relationships, and the JWT/RBAC model. AI helped me sketch initial drafts and discuss trade-offs, which I then evaluated and adapted to the project's requirements.
- **Implementation**: I wrote and directed the code structure. AI assisted with boilerplate, repetitive route handlers, and Streamlit/Plotly snippets, which I then read, modified, debugged, and integrated. Anything that did not fit the project was rewritten or discarded.
- **AI Mixologist microservice**: The decision to expose Gemini behind a separate FastAPI process (rather than embedding it in the main API) is mine. AI helped me with the Google `genai` client wiring and prompt scaffolding; I designed the request/response contract and the failure-handling strategy.
- **Testing**: I defined what needed to be tested (CRUD happy paths, JWT expiry, RBAC negative cases, bounded concurrency in the refresh worker, idempotency contracts). AI helped me write the test bodies faster; I ran them, fixed the failures, and added the cases AI missed.
- **Documentation**: AI helped me draft and tighten this README, the EX3 notes, and the compose runbook. The content — what to document, which trade-offs to surface, what a grader needs — is mine.

Every AI-generated line was read, run, and verified locally before being committed. The architecture, the trade-offs, and the bugs are all mine; the AI was a faster keyboard, not the author.

