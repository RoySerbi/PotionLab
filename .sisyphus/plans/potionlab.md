# PotionLab — Cocktail Recipe Engine & Flavor Chemistry Workbench

## TL;DR

> **Quick Summary**: Build "PotionLab" — a cocktail recipe management system with flavor chemistry modeling, a visual Streamlit dashboard, and an AI Mixologist powered by Google Gemini — across three progressive exercises (EX1→EX2→EX3) for the EASS course. The domain is deliberately non-obvious (cocktail chemistry, not movies/recipes) to maximize grader impression.
> 
> **Deliverables**:
> - EX1: FastAPI CRUD backend with 3 SQLModel models (Cocktail, Ingredient, FlavorTag) + many-to-many relationships + pytest suite + seed script
> - EX2: Streamlit dashboard with cocktail browser, flavor wheel visualization, add-cocktail form, and basic ingredient filter
> - EX3: Docker Compose multi-service stack (API + Postgres + Redis + AI Mixologist) with JWT auth, async worker, "What Can I Make?" feature, demo script, and runbook
> 
> **Estimated Effort**: Large (3 separate submissions over ~4 months, with EX3 being the biggest)
> **Parallel Execution**: YES — 4 waves per exercise phase
> **Critical Path**: EX1 foundation → EX2 dashboard → EX3 integration + AI service

---

## Context

### Original Request
Student needs to pick a project domain for the EASS course's three progressive exercises (EX1, EX2, EX3) that combine into a final capstone. Wanted "non-boring / non-intuitive" ideas that guarantee a perfect score and stand out. Chose "PotionLab" (cocktail recipe engine with flavor chemistry) from three proposals.

### Interview Summary
**Key Discussions**:
- Domain: Cocktails & mixology with a **flavor chemistry** angle — not a simple recipe box
- Data model: Rich 3-model design with many-to-many (Cocktail ↔ Ingredient via link table, Ingredient ↔ FlavorTag)
- Interface: Streamlit (GUI) with visual flavor wheels and rich data display
- AI provider: Google AI Studio (Gemini free tier) for the EX3 AI Mixologist service
- Enhancement: "What Can I Make?" — filter cocktails by available ingredients
- Effort: Go big, stand out. Student wants showpiece quality.

**Research Findings**:
- Course stack: Python 3.12+, uv, FastAPI, SQLModel, Pydantic, Streamlit, pytest, Docker Compose
- Students pick domain Day 1, keep it through all exercises — "movies" is the canonical example to avoid
- Course values local-first: everything offline, no cloud required
- Rubric weights: Craft 30%, Correctness 30%, Empathy 20%, Resilience 20%

### Metis Review
**Identified Gaps** (all addressed):
- Many-to-many link tables must use composite primary keys (not synthetic IDs) — incorporated
- Use `StaticPool` for in-memory SQLite test fixtures — incorporated
- Use FastAPI `lifespan` context manager instead of deprecated `@app.on_event("startup")` — incorporated
- Gemini free tier limits (15 RPM, 1500 RPD) require client-side rate limiting + Redis caching — incorporated
- Response models must avoid lazy-loading outside session scope — separate flat/nested read models designed
- Use `passlib[bcrypt]` for auth (as taught in Session 11), not `pwdlib` — incorporated
- Timing attack prevention on auth failures — incorporated

---

## Work Objectives

### Core Objective
Build a complete, polished cocktail chemistry platform that progresses from backend → dashboard → multi-service AI stack, scoring perfectly on every rubric dimension while demonstrating unusually high domain expertise and visual polish.

### Concrete Deliverables

**EX1 (due 30/03/2026):**
- FastAPI application with `/cocktails`, `/ingredients`, `/flavor-tags` CRUD endpoints
- SQLModel models: `Cocktail`, `Ingredient`, `FlavorTag`, `CocktailIngredient` (link), `IngredientFlavorTag` (link)
- Pydantic schemas: Create/Read/Update for each resource, nested read models
- pytest test suite (≥80% coverage) covering happy paths + failure modes
- Seed script with 20+ real cocktails and their ingredients
- README with setup instructions
- `.http` file for REST Client playground

**EX2 (due 18/05/2026):**
- Streamlit dashboard (`streamlit_app.py`) connected to EX1 API
- Pages: Cocktail Browser, Ingredient Explorer, Add New Cocktail form
- Flavor wheel chart visualization (plotly polar chart)
- "What Can I Make?" basic filter (select ingredients → show matching cocktails)
- README documenting side-by-side API + Streamlit launch

**EX3 (due 01/07/2026):**
- `compose.yaml` orchestrating: FastAPI API, PostgreSQL, Redis, AI Mixologist service
- AI Mixologist microservice (separate FastAPI app using Google Gemini)
- JWT authentication on mutation endpoints with role checks
- `scripts/refresh.py` with bounded async concurrency + Redis idempotency
- Polished "What Can I Make?" with AI-powered suggestions for missing-ingredient substitutions
- Demo script (`scripts/demo.sh` or `python -m app.demo`)
- `docs/EX3-notes.md` with runbook, architecture decisions, and trace excerpts
- `docs/runbooks/compose.md` with launch/verify/test instructions

### Definition of Done
- [ ] Each exercise passes its full rubric with ≥95 points + bonus
- [ ] `uv run pytest -q` passes with ≥80% coverage on each exercise
- [ ] `uv run ruff check .` and `uv run mypy src` clean
- [ ] `docker compose up` brings up all EX3 services successfully
- [ ] Demo script runs end-to-end without manual intervention

### Must Have
- Three-model data architecture with many-to-many relationships (composite PK link tables)
- Pydantic validation on all inputs with meaningful error messages
- Separate flat and nested response models (avoid lazy-load outside session)
- Tests covering: happy path CRUD, 404s, 422 validation errors, duplicate prevention
- Real cocktail data in seed script (not placeholder data)
- FastAPI `lifespan` context manager (not deprecated `on_event`)
- `StaticPool` in test fixtures for in-memory SQLite
- EX3: Redis caching of AI responses (TTL ≥ 3600s)
- EX3: Client-side rate limiting for Gemini (15 RPM cap)
- EX3: `passlib[bcrypt]` for credential hashing (as taught in course)
- EX3: Timing attack prevention on auth failures

### Must NOT Have (Guardrails)
- No cloud deployment — everything local
- No `@app.on_event("startup")` — use `lifespan`
- No `pwdlib` — use `passlib[bcrypt]` per course material
- No synthetic auto-increment IDs on link tables — composite PKs only
- No committed `.db` files — use seed scripts/migrations
- No over-engineered auth (OAuth, OIDC) — simple API key or JWT as taught
- No massive data ingestion — keep seed data to 20-30 cocktails
- No frontend framework (React, Vue) — Streamlit only
- No excessive abstraction — keep service layer lean
- No `as any` / `@ts-ignore` equivalent (`type: ignore` abuse in Python)

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (course mandates pytest from Session 1)
- **Automated tests**: YES (tests-after, not TDD — tests written alongside implementation)
- **Framework**: pytest + pytest-asyncio + httpx AsyncClient
- **Coverage target**: ≥80% per exercise (course requirement)

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Backend API**: Use Bash (curl/httpx) — Send requests, assert status + response fields
- **Streamlit UI**: Use Playwright (playwright skill) — Navigate, interact, assert DOM, screenshot
- **Docker Compose**: Use Bash — `docker compose up -d`, health checks, curl endpoints
- **AI Service**: Use Bash (curl) — Send prompt, verify structured response, check Redis cache

---

## Execution Strategy

### Parallel Execution Waves

```
=== PHASE 1: EX1 (Backend Foundation) — Due 30/03/2026 ===

Wave 1 (Foundation — scaffolding + models):
├── Task 1: Project scaffolding (pyproject.toml, uv, directory structure) [quick]
├── Task 2: SQLModel models (Cocktail, Ingredient, FlavorTag, link tables) [unspecified-high]
├── Task 3: Pydantic schemas (Create/Read/Update for all resources) [quick]
└── Task 4: Database session + lifespan setup [quick]

Wave 2 (Core API — routes + service layer):
├── Task 5: Ingredient CRUD routes + service (depends: 2, 3, 4) [unspecified-high]
├── Task 6: FlavorTag CRUD routes + service (depends: 2, 3, 4) [unspecified-high]
├── Task 7: Cocktail CRUD routes + service with nested ingredient management (depends: 2, 3, 4) [deep]
└── Task 8: Seed script with 20+ real cocktails (depends: 2, 4) [quick]

Wave 3 (Quality + Docs):
├── Task 9: Test suite — happy paths + failure modes for all endpoints (depends: 5, 6, 7) [unspecified-high]
├── Task 10: README + .http playground file (depends: 5, 6, 7) [writing]
└── Task 11: Lint, type-check, coverage verification (depends: 9) [quick]

=== PHASE 2: EX2 (Streamlit Dashboard) — Due 18/05/2026 ===

Wave 4 (Dashboard Core):
├── Task 12: Streamlit app skeleton + API client module (depends: EX1 complete) [unspecified-high]
├── Task 13: Cocktail Browser page (table + detail view + search) [visual-engineering]
├── Task 14: Ingredient Explorer page (list, filter, flavor tag badges) [visual-engineering]
└── Task 15: Add New Cocktail form (multi-step: name → ingredients → tags) [visual-engineering]

Wave 5 (Polish + Extra):
├── Task 16: Flavor wheel visualization (plotly polar chart) [visual-engineering]
├── Task 17: "What Can I Make?" basic filter page (depends: 12) [unspecified-high]
├── Task 18: EX2 README + side-by-side launch docs (depends: 12-17) [writing]
└── Task 19: Bonus: automated Streamlit test via subprocess/CLI runner (depends: 12) [quick]

=== PHASE 3: EX3 (Capstone Integration) — Due 01/07/2026 ===

Wave 6 (Infrastructure + Migration):
├── Task 20: Migrate SQLite → PostgreSQL (update session.py, add psycopg dep) [unspecified-high]
├── Task 21: Docker Compose setup (API + Postgres + Redis) [unspecified-high]
├── Task 22: JWT authentication module (passlib + python-jose) [deep]
└── Task 23: Redis integration (connection, caching utilities) [unspecified-high]

Wave 7 (AI Service + Async):
├── Task 24: AI Mixologist microservice (separate FastAPI app + Gemini client) (depends: 21, 23) [deep]
├── Task 25: scripts/refresh.py — async refresher with bounded concurrency + Redis idempotency (depends: 23) [deep]
├── Task 26: "What Can I Make?" enhanced — AI-powered substitution suggestions (depends: 24) [unspecified-high]
└── Task 27: Protect mutation endpoints with JWT + role checks (depends: 22) [unspecified-high]

Wave 8 (Demo + Docs + Final QA):
├── Task 28: Demo script (scripts/demo.sh or python -m app.demo) (depends: 21, 24, 26, 27) [unspecified-high]
├── Task 29: docs/EX3-notes.md + docs/runbooks/compose.md (depends: all EX3 tasks) [writing]
├── Task 30: EX3 test suite — integration tests for multi-service stack (depends: 24, 27) [unspecified-high]
└── Task 31: Final lint, type-check, coverage, Compose smoke test (depends: 28, 29, 30) [quick]

Wave FINAL (After ALL tasks — verification):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|-----------|--------|
| 1 | — | 2, 3, 4 |
| 2 | 1 | 5, 6, 7, 8 |
| 3 | 1 | 5, 6, 7 |
| 4 | 1 | 5, 6, 7, 8 |
| 5 | 2, 3, 4 | 9, 10 |
| 6 | 2, 3, 4 | 9, 10 |
| 7 | 2, 3, 4 | 9, 10 |
| 8 | 2, 4 | 9 |
| 9 | 5, 6, 7, 8 | 11 |
| 10 | 5, 6, 7 | 11 |
| 11 | 9, 10 | 12 (EX2 start) |
| 12 | 11 | 13, 14, 15, 17 |
| 13 | 12 | 16, 18 |
| 14 | 12 | 18 |
| 15 | 12 | 18 |
| 16 | 13 | 18 |
| 17 | 12 | 18 |
| 18 | 13-17 | 19 |
| 19 | 12 | — |
| 20 | 11 | 21 |
| 21 | 20 | 24, 28 |
| 22 | 11 | 27 |
| 23 | 11 | 24, 25, 26 |
| 24 | 21, 23 | 26, 28, 30 |
| 25 | 23 | 29 |
| 26 | 24 | 28 |
| 27 | 22 | 28, 30 |
| 28 | 21, 24, 26, 27 | 29 |
| 29 | all EX3 | 31 |
| 30 | 24, 27 | 31 |
| 31 | 28, 29, 30 | F1-F4 |

### Agent Dispatch Summary

- **Wave 1**: 4 tasks — T1 → `quick`, T2 → `unspecified-high`, T3 → `quick`, T4 → `quick`
- **Wave 2**: 4 tasks — T5 → `unspecified-high`, T6 → `unspecified-high`, T7 → `deep`, T8 → `quick`
- **Wave 3**: 3 tasks — T9 → `unspecified-high`, T10 → `writing`, T11 → `quick`
- **Wave 4**: 4 tasks — T12 → `unspecified-high`, T13-T15 → `visual-engineering`
- **Wave 5**: 4 tasks — T16 → `visual-engineering`, T17 → `unspecified-high`, T18 → `writing`, T19 → `quick`
- **Wave 6**: 4 tasks — T20 → `unspecified-high`, T21 → `unspecified-high`, T22 → `deep`, T23 → `unspecified-high`
- **Wave 7**: 4 tasks — T24 → `deep`, T25 → `deep`, T26 → `unspecified-high`, T27 → `unspecified-high`
- **Wave 8**: 4 tasks — T28 → `unspecified-high`, T29 → `writing`, T30 → `unspecified-high`, T31 → `quick`
- **FINAL**: 4 tasks — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

### === PHASE 1: EX1 — FastAPI Backend Foundation (Due 30/03/2026) ===

- [x] 1. Project Scaffolding & Environment Setup

  **What to do**:
  - Initialize a new Python project with `uv init` in a fresh repo
  - Create `pyproject.toml` with dependencies: fastapi, uvicorn[standard], sqlmodel, pydantic, httpx, pytest, pytest-asyncio, ruff, mypy, typer, rich
  - Set up directory structure matching course layout:
    ```
    src/app/main.py
    src/app/api/v1/__init__.py
    src/app/core/config.py
    src/app/db/session.py
    src/app/models/__init__.py
    src/app/schemas/__init__.py
    src/app/services/__init__.py
    tests/__init__.py
    tests/conftest.py
    tests/api/__init__.py
    ```
  - Create minimal `main.py` with `FastAPI(title="PotionLab", version="0.1.0")` and `/health` endpoint
  - Use `lifespan` context manager (NOT `@app.on_event("startup")`)
  - Create `conftest.py` with in-memory SQLite fixture using `StaticPool`
  - Add `tests/api/test_health.py` verifying health endpoint returns `{"status": "ok"}`
  - Run `uv run pytest -q` to verify green baseline

  **Must NOT do**:
  - Do not use `@app.on_event("startup")` — use `lifespan`
  - Do not commit `.db` files
  - Do not add dependencies beyond what's listed (no bloat)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Scaffolding is straightforward file creation, no complex logic
  - **Skills**: []
    - No special skills needed for project setup

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 1 (first task — all others depend on this)
  - **Blocks**: Tasks 2, 3, 4
  - **Blocked By**: None (starting point)

  **References**:

  **Pattern References**:
  - `instructions.mdc:62-102` — Standard project layout the course expects
  - `instructions.mdc:152-187` — Meeting 1 Part B bootstrap commands and scaffold pattern
  - `instructions.mdc:437-443` — `lifespan` wiring pattern (note: the file shows deprecated `on_event` — use modern `lifespan` instead)

  **API/Type References**:
  - `instructions.mdc:159-161` — Health endpoint pattern (`@app.get("/health")`)

  **Test References**:
  - `instructions.mdc:165-176` — Health check test using `httpx.AsyncClient`
  - `instructions.mdc:551-569` — `conftest.py` with `tmp_path` and `monkeypatch` for DB isolation

  **External References**:
  - FastAPI lifespan docs: `https://fastapi.tiangolo.com/advanced/events/#lifespan`
  - SQLModel StaticPool: `https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#configure-the-in-memory-database`

  **WHY Each Reference Matters**:
  - The course layout (instructions.mdc:62-102) is what graders expect — deviate and lose Craft points
  - The conftest pattern with `StaticPool` prevents the subtle bug where each test connection gets a different in-memory DB
  - Using `lifespan` instead of `on_event` shows awareness of current FastAPI best practice (impresses graders)

  **Acceptance Criteria**:
  - [ ] `uv run pytest -q` passes (1 test, 0 failures)
  - [ ] `uv run uvicorn app.main:app --reload` starts without errors
  - [ ] `curl -s localhost:8000/health | jq` returns `{"status": "ok"}`
  - [ ] Directory structure matches course layout
  - [ ] `ruff check .` returns 0 errors

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Health endpoint returns OK
    Tool: Bash (curl)
    Preconditions: Server running via `uv run uvicorn app.main:app --port 8000`
    Steps:
      1. curl -s http://localhost:8000/health
      2. Parse JSON response
      3. Assert response body equals {"status": "ok"}
      4. Assert HTTP status code is 200
    Expected Result: {"status": "ok"} with 200 status
    Failure Indicators: Non-200 status, missing "status" key, server fails to start
    Evidence: .sisyphus/evidence/task-1-health-endpoint.json

  Scenario: pytest baseline green
    Tool: Bash
    Preconditions: Project scaffolded, dependencies installed
    Steps:
      1. Run `uv run pytest -q`
      2. Assert exit code 0
      3. Assert output contains "1 passed"
    Expected Result: "1 passed" in output, exit code 0
    Failure Indicators: Any test failure, import errors, missing conftest
    Evidence: .sisyphus/evidence/task-1-pytest-baseline.txt
  ```

  **Commit**: YES
  - Message: `feat: scaffold PotionLab project with health endpoint and test baseline`
  - Files: `pyproject.toml, uv.lock, src/app/**, tests/**, .gitignore`
  - Pre-commit: `uv run pytest -q && uv run ruff check .`

- [x] 2. SQLModel Models — Cocktail, Ingredient, FlavorTag with Many-to-Many

  **What to do**:
  - Create `src/app/models/flavor_tag.py`:
    - `FlavorTag(SQLModel, table=True)`: id (int PK), name (str, unique, max_length=30), category (str, max_length=30 — e.g., "citrus", "bitter", "sweet", "herbal", "smoky", "floral", "spicy", "umami")
  - Create `src/app/models/ingredient.py`:
    - `Ingredient(SQLModel, table=True)`: id (int PK), name (str, unique, max_length=80), category (str, max_length=40 — e.g., "spirit", "liqueur", "mixer", "garnish", "bitter"), description (optional str, max_length=255)
    - Relationship: `flavor_tags: list[FlavorTag]` via link model
  - Create `src/app/models/cocktail.py`:
    - `Cocktail(SQLModel, table=True)`: id (int PK), name (str, unique, max_length=80), description (optional str, max_length=500), instructions (str, max_length=2000), glass_type (str, max_length=40 — e.g., "coupe", "rocks", "highball"), difficulty (int, 1-5)
    - Relationship: `ingredients: list[Ingredient]` via link model
  - Create link tables with **composite primary keys**:
    - `src/app/models/cocktail_ingredient.py`: `CocktailIngredient(SQLModel, table=True)` with cocktail_id (FK), ingredient_id (FK), amount (str, max_length=40 — e.g., "2 oz", "dash"), is_optional (bool, default=False). Primary key = (cocktail_id, ingredient_id)
    - `src/app/models/ingredient_flavor_tag.py`: `IngredientFlavorTag(SQLModel, table=True)` with ingredient_id (FK), flavor_tag_id (FK). Primary key = (ingredient_id, flavor_tag_id)
  - Create `src/app/models/__init__.py` barrel file importing all models
  - Update `db/session.py` `init_db()` to create all tables

  **Must NOT do**:
  - Do NOT use synthetic auto-increment IDs on link tables — use composite PKs
  - Do NOT add circular imports between model files
  - Do NOT use `Optional` from typing — use `X | None` syntax (Python 3.12)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Many-to-many SQLModel relationships require careful design and are error-prone
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 3, 4)
  - **Parallel Group**: Wave 1 (with 3, 4)
  - **Blocks**: Tasks 5, 6, 7, 8
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `instructions.mdc:329-334` — Item model pattern with Field constraints
  - `instructions.mdc:486-514` — Category model with Relationship and back_populates pattern
  - `instructions.mdc:508-514` — Back-reference pattern on Item model with foreign_key

  **External References**:
  - SQLModel many-to-many: `https://sqlmodel.tiangolo.com/tutorial/many-to-many/`
  - SQLModel link model with extra fields: `https://sqlmodel.tiangolo.com/tutorial/many-to-many/link-model-with-extra-fields/`

  **WHY Each Reference Matters**:
  - instructions.mdc:486-514 shows the exact Relationship/back_populates pattern the course uses — follow this for consistency
  - The CocktailIngredient link table needs `amount` and `is_optional` fields (extra data on the relationship), which requires the "link model with extra fields" SQLModel pattern
  - Composite PKs on link tables prevent duplicate relationships and are the SQLModel-recommended approach

  **Acceptance Criteria**:
  - [ ] All 5 model files exist with correct fields and constraints
  - [ ] Link tables use composite primary keys
  - [ ] `init_db()` creates all tables without errors
  - [ ] Models can be imported without circular dependency errors
  - [ ] `from app.models import Cocktail, Ingredient, FlavorTag, CocktailIngredient, IngredientFlavorTag` works

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Models create tables in SQLite
    Tool: Bash (python)
    Preconditions: Models defined, db/session.py updated
    Steps:
      1. Run `uv run python -c "from app.db.session import init_db; init_db(); print('OK')"`
      2. Verify output contains "OK"
      3. Run `uv run python -c "import sqlite3; conn = sqlite3.connect('data/app.db'); print([t[0] for t in conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall()])"`
      4. Assert output contains: cocktail, ingredient, flavortag, cocktailingredient, ingredientflavortag
    Expected Result: All 5 tables created successfully
    Failure Indicators: Import errors, missing tables, FK constraint failures
    Evidence: .sisyphus/evidence/task-2-model-tables.txt

  Scenario: Composite PK prevents duplicate links
    Tool: Bash (pytest)
    Preconditions: Models created, test fixture with in-memory DB
    Steps:
      1. Create a cocktail and an ingredient
      2. Create a CocktailIngredient link
      3. Attempt to create a duplicate CocktailIngredient with same (cocktail_id, ingredient_id)
      4. Assert IntegrityError is raised
    Expected Result: IntegrityError on duplicate composite key
    Failure Indicators: Duplicate allowed, wrong error type, no error raised
    Evidence: .sisyphus/evidence/task-2-composite-pk-constraint.txt
  ```

  **Commit**: YES (groups with Task 3)
  - Message: `feat(models): add Cocktail, Ingredient, FlavorTag models with M2M link tables`
  - Files: `src/app/models/*.py, src/app/db/session.py`
  - Pre-commit: `uv run ruff check . && uv run mypy src`

- [x] 3. Pydantic Schemas — Create/Read/Update for All Resources

  **What to do**:
  - Create `src/app/schemas/flavor_tag.py`:
    - `FlavorTagCreate(BaseModel)`: name (str, min 1, max 30), category (str, min 1, max 30)
    - `FlavorTagRead(FlavorTagCreate)`: id (int, gt=0)
  - Create `src/app/schemas/ingredient.py`:
    - `IngredientCreate(BaseModel)`: name (str, min 1, max 80), category (str, min 1, max 40), description (str | None, max 255), flavor_tag_ids (list[int], default=[])
    - `IngredientRead(BaseModel)`: id, name, category, description — flat, no nested relationships
    - `IngredientReadWithTags(IngredientRead)`: flavor_tags (list[FlavorTagRead]) — nested version for detail endpoints
  - Create `src/app/schemas/cocktail.py`:
    - `CocktailIngredientCreate(BaseModel)`: ingredient_id (int, gt=0), amount (str, min 1, max 40), is_optional (bool, default=False)
    - `CocktailCreate(BaseModel)`: name (str, min 1, max 80), description (str | None, max 500), instructions (str, min 1, max 2000), glass_type (str, min 1, max 40), difficulty (int, ge=1, le=5), ingredients (list[CocktailIngredientCreate])
    - `CocktailRead(BaseModel)`: id, name, description, glass_type, difficulty — flat
    - `CocktailReadFull(CocktailRead)`: instructions, ingredients (list with amount/name), flavor_profile (list[str]) — nested for detail view
  - All schemas use `model_config = ConfigDict(from_attributes=True)` for SQLModel compatibility

  **Must NOT do**:
  - Do NOT access relationship attributes outside session context in Read models
  - Do NOT create a single monolithic schema — keep flat and nested versions separate
  - Do NOT skip validation constraints (min_length, max_length, ge, le)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Schema files are straightforward Pydantic model definitions
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 2, 4)
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 5, 6, 7
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `instructions.mdc:336-349` — ItemCreate/ItemRead schema pattern with Field constraints
  - `instructions.mdc:516-523` — Updated schema with foreign key reference (category_id)

  **External References**:
  - Pydantic `model_config` docs: `https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict`

  **WHY Each Reference Matters**:
  - instructions.mdc:336-349 shows the exact Create/Read pattern graders expect — flat BaseModel with Field constraints
  - Separate flat/nested schemas prevent the lazy-loading-outside-session bug that Metis flagged as critical
  - `from_attributes=True` enables `model_validate(sqlmodel_instance)` which is required for response serialization

  **Acceptance Criteria**:
  - [ ] All schema files exist with correct fields and constraints
  - [ ] FlavorTagCreate rejects empty name (min_length=1)
  - [ ] CocktailCreate rejects difficulty outside 1-5 range
  - [ ] `model_config = ConfigDict(from_attributes=True)` on all Read schemas
  - [ ] Flat and nested Read schemas exist for Ingredient and Cocktail

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Schema validation rejects invalid input
    Tool: Bash (python)
    Preconditions: Schemas defined
    Steps:
      1. Run `uv run python -c "from app.schemas.cocktail import CocktailCreate; CocktailCreate(name='', instructions='Mix', glass_type='coupe', difficulty=6, ingredients=[])"`
      2. Assert ValidationError is raised (name too short AND difficulty > 5)
    Expected Result: ValidationError with details about name min_length and difficulty le constraint
    Failure Indicators: No error raised, wrong field flagged
    Evidence: .sisyphus/evidence/task-3-schema-validation.txt

  Scenario: Schema accepts valid cocktail input
    Tool: Bash (python)
    Preconditions: Schemas defined
    Steps:
      1. Run `uv run python -c "from app.schemas.cocktail import CocktailCreate; c = CocktailCreate(name='Margarita', instructions='Shake with ice', glass_type='coupe', difficulty=2, ingredients=[{'ingredient_id': 1, 'amount': '2 oz', 'is_optional': False}]); print(c.model_dump_json())"`
      2. Assert valid JSON output with all fields present
    Expected Result: JSON string with name="Margarita", difficulty=2, ingredients list with 1 item
    Failure Indicators: ValidationError, missing fields, wrong types
    Evidence: .sisyphus/evidence/task-3-schema-valid.txt
  ```

  **Commit**: YES (groups with Task 2)
  - Message: `feat(schemas): add Create/Read/Update Pydantic schemas for all resources`
  - Files: `src/app/schemas/*.py`
  - Pre-commit: `uv run ruff check . && uv run mypy src`

- [x] 4. Database Session, Lifespan, and Config Setup

  **What to do**:
  - Create `src/app/core/config.py`:
    - `Settings(BaseModel)` with `database_url: str = "sqlite:///data/app.db"`, `app_title: str = "PotionLab"`, `app_version: str = "0.1.0"`
    - Load from environment variables via `model_config = SettingsConfigDict(env_prefix="POTION_")`
  - Update `src/app/db/session.py`:
    - `_sqlite_url()` helper respecting `SQLMODEL_DATABASE` env var (for test isolation)
    - Engine creation with `check_same_thread=False` for SQLite
    - `init_db()` calling `SQLModel.metadata.create_all(engine)`
    - `get_session()` context manager yielding `Session(engine)`
  - Update `src/app/main.py`:
    - `lifespan` async context manager that calls `init_db()` on startup
    - `app = FastAPI(title=settings.app_title, version=settings.app_version, lifespan=lifespan)`
  - Update `tests/conftest.py`:
    - Fixture using `create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)`
    - Override `get_session` dependency with test session
    - `AsyncClient` fixture for test HTTP calls

  **Must NOT do**:
  - Do NOT use `@app.on_event("startup")` — use `lifespan` context manager
  - Do NOT hardcode database paths — always use config/env vars
  - Do NOT forget `StaticPool` in test engine (causes inter-test state leakage)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Config and session setup follows well-established course patterns
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 2, 3)
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 5, 6, 7, 8
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `instructions.mdc:352-386` — Database session module with `_sqlite_url()`, engine creation, `init_db()`, and `get_session()`
  - `instructions.mdc:437-443` — Main.py wiring with startup event (use `lifespan` instead)
  - `instructions.mdc:551-569` — Test conftest with `tmp_path`, `monkeypatch`, and `AsyncClient` fixture

  **External References**:
  - FastAPI lifespan: `https://fastapi.tiangolo.com/advanced/events/#lifespan`
  - SQLModel StaticPool testing: `https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/`
  - Pydantic Settings: `https://docs.pydantic.dev/latest/concepts/pydantic_settings/`

  **WHY Each Reference Matters**:
  - instructions.mdc:352-386 is the exact session.py pattern graders expect — follow it but modernize with lifespan
  - StaticPool is critical for test reliability (Metis flagged this) — without it, each test connection creates a separate in-memory DB
  - Config via Pydantic Settings shows "craft" on the rubric (30% weight)

  **Acceptance Criteria**:
  - [ ] `lifespan` context manager in main.py (not `on_event`)
  - [ ] `SQLMODEL_DATABASE` env var respected in session.py
  - [ ] `StaticPool` used in conftest.py
  - [ ] `uv run pytest -q` still passes after changes
  - [ ] Settings class loads from environment variables

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: App starts with lifespan and creates DB tables
    Tool: Bash (curl)
    Preconditions: No existing data/app.db file
    Steps:
      1. Start server: `uv run uvicorn app.main:app --port 8000`
      2. Wait 2 seconds for startup
      3. curl -s http://localhost:8000/health
      4. Check that data/app.db file exists
    Expected Result: Health returns 200, app.db file created by init_db()
    Failure Indicators: Server fails to start, no DB file, health returns error
    Evidence: .sisyphus/evidence/task-4-lifespan-startup.txt

  Scenario: Test isolation with StaticPool
    Tool: Bash (pytest)
    Preconditions: conftest.py with StaticPool engine
    Steps:
      1. Run `uv run pytest tests/api/test_health.py -q`
      2. Assert no warnings about session/engine
      3. Assert test passes
    Expected Result: 1 passed, 0 warnings about DB state
    Failure Indicators: "OperationalError: no such table", test state leaking between tests
    Evidence: .sisyphus/evidence/task-4-test-isolation.txt
  ```

  **Commit**: YES
  - Message: `feat(core): add config, database session with lifespan, and test fixtures with StaticPool`
  - Files: `src/app/core/config.py, src/app/db/session.py, src/app/main.py, tests/conftest.py`
  - Pre-commit: `uv run pytest -q`

- [x] 5. Ingredient CRUD Routes + Service Layer

  **What to do**:
  - Create `src/app/services/ingredient_service.py`:
    - `IngredientService` class with `session_factory` constructor
    - Methods: `create_ingredient(payload: IngredientCreate) -> Ingredient`, `list_ingredients() -> list[Ingredient]`, `get_ingredient(id: int) -> Ingredient`, `delete_ingredient(id: int) -> None`
    - `create_ingredient` must check for duplicate names and raise `ValueError`
    - `create_ingredient` must attach flavor tags by IDs from payload
  - Create `src/app/api/v1/routes_ingredients.py`:
    - `router = APIRouter(prefix="/ingredients", tags=["ingredients"])`
    - `POST /` → 201 + `IngredientRead`
    - `GET /` → 200 + `list[IngredientRead]`
    - `GET /{id}` → 200 + `IngredientReadWithTags` (nested with flavor tags)
    - `DELETE /{id}` → 204
    - Convert `ValueError` → 409 Conflict, missing → 404
  - Wire router in `main.py`

  **Must NOT do**:
  - Do NOT put business logic in route handlers — keep in service layer
  - Do NOT return nested relationships from list endpoints (only detail endpoint)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Service layer with M2M relationship management requires careful session handling
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 6, 7, 8)
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 9, 10
  - **Blocked By**: Tasks 2, 3, 4

  **References**:

  **Pattern References**:
  - `instructions.mdc:388-426` — Routes pattern with APIRouter, Depends, HTTPException, status codes
  - `instructions.mdc:630-658` — InventoryService class pattern with session_factory, create, list, adjust
  - `instructions.mdc:660-681` — Route-to-service wiring with Depends(get_service) and ValueError→409

  **WHY Each Reference Matters**:
  - instructions.mdc:630-658 is THE service layer pattern the course teaches — follow it exactly for "Craft" points
  - The route-to-service wiring (660-681) shows how to catch ValueError and raise HTTPException — graders check this

  **Acceptance Criteria**:
  - [ ] `POST /ingredients/` creates ingredient with flavor tags
  - [ ] `GET /ingredients/` returns flat list (no nested tags)
  - [ ] `GET /ingredients/{id}` returns ingredient with nested flavor tags
  - [ ] `POST /ingredients/` with duplicate name returns 409
  - [ ] `GET /ingredients/999` returns 404
  - [ ] `DELETE /ingredients/{id}` returns 204

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Create and fetch ingredient with flavor tags
    Tool: Bash (curl)
    Preconditions: Server running, flavor tags "citrus" and "sweet" already created (IDs 1, 2)
    Steps:
      1. POST /ingredients/ with {"name": "Fresh Lime Juice", "category": "mixer", "flavor_tag_ids": [1, 2]}
      2. Assert 201 status and response contains "id" field
      3. GET /ingredients/{id} (from step 1)
      4. Assert response includes "flavor_tags" array with 2 entries
    Expected Result: 201 on create, detail view shows nested flavor tags
    Failure Indicators: 500 error, missing flavor_tags in response, wrong status code
    Evidence: .sisyphus/evidence/task-5-ingredient-crud.json

  Scenario: Duplicate ingredient name returns 409
    Tool: Bash (curl)
    Preconditions: Ingredient "Vodka" already exists
    Steps:
      1. POST /ingredients/ with {"name": "Vodka", "category": "spirit"}
      2. Assert 409 status
      3. Assert response body contains "already exists"
    Expected Result: 409 Conflict with descriptive error message
    Failure Indicators: 500 error, 201 (duplicate allowed), generic error message
    Evidence: .sisyphus/evidence/task-5-duplicate-409.json
  ```

  **Commit**: YES (groups with Task 6)
  - Message: `feat(api): add ingredient CRUD routes and service layer`
  - Files: `src/app/services/ingredient_service.py, src/app/api/v1/routes_ingredients.py, src/app/main.py`
  - Pre-commit: `uv run ruff check .`

- [x] 6. FlavorTag CRUD Routes + Service Layer

  **What to do**:
  - Create `src/app/services/flavor_tag_service.py`:
    - `FlavorTagService` class: `create(payload) -> FlavorTag`, `list_all() -> list[FlavorTag]`, `get(id) -> FlavorTag`, `delete(id) -> None`
    - Duplicate name check → `ValueError`
  - Create `src/app/api/v1/routes_flavor_tags.py`:
    - `router = APIRouter(prefix="/flavor-tags", tags=["flavor-tags"])`
    - `POST /` → 201, `GET /` → 200 list, `GET /{id}` → 200, `DELETE /{id}` → 204
  - Wire router in `main.py`

  **Must NOT do**:
  - Do NOT over-engineer — FlavorTag is the simplest CRUD, keep it lean

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Follows same pattern as Task 5 but simpler; needs correct session handling
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 5, 7, 8)
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 9, 10
  - **Blocked By**: Tasks 2, 3, 4

  **References**:

  **Pattern References**:
  - Same as Task 5 (instructions.mdc:388-426, 630-681)
  - `instructions.mdc:524-549` — Categories router pattern (FlavorTag is structurally identical to Category)

  **WHY Each Reference Matters**:
  - instructions.mdc:524-549 is the closest analog — Category CRUD is almost identical to FlavorTag CRUD

  **Acceptance Criteria**:
  - [ ] All 4 endpoints work (POST, GET list, GET detail, DELETE)
  - [ ] Duplicate name → 409
  - [ ] Missing ID → 404

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: CRUD lifecycle for flavor tag
    Tool: Bash (curl)
    Preconditions: Server running, no existing flavor tags
    Steps:
      1. POST /flavor-tags/ with {"name": "citrus", "category": "fruit"}
      2. Assert 201, capture id
      3. GET /flavor-tags/ — assert array contains "citrus"
      4. GET /flavor-tags/{id} — assert name is "citrus"
      5. DELETE /flavor-tags/{id} — assert 204
      6. GET /flavor-tags/{id} — assert 404
    Expected Result: Full CRUD lifecycle completes
    Failure Indicators: Any unexpected status code, missing fields
    Evidence: .sisyphus/evidence/task-6-flavor-tag-crud.json

  Scenario: Duplicate flavor tag name returns 409
    Tool: Bash (curl)
    Preconditions: FlavorTag "bitter" exists
    Steps:
      1. POST /flavor-tags/ with {"name": "bitter", "category": "taste"}
      2. Assert 409
    Expected Result: 409 Conflict
    Evidence: .sisyphus/evidence/task-6-duplicate-409.json
  ```

  **Commit**: YES (groups with Task 5)
  - Message: `feat(api): add flavor tag CRUD routes and service layer`
  - Files: `src/app/services/flavor_tag_service.py, src/app/api/v1/routes_flavor_tags.py, src/app/main.py`
  - Pre-commit: `uv run ruff check .`

- [x] 7. Cocktail CRUD Routes + Service with Nested Ingredient Management

  **What to do**:
  - Create `src/app/services/cocktail_service.py`:
    - `CocktailService` class:
      - `create_cocktail(payload: CocktailCreate) -> Cocktail` — creates cocktail + CocktailIngredient links with amounts. Validates all ingredient_ids exist. Raises ValueError on duplicate name.
      - `list_cocktails() -> list[Cocktail]` — returns flat list (no eager-loading ingredients)
      - `get_cocktail(id: int) -> Cocktail` — returns with eager-loaded ingredients + their flavor tags (for detail view)
      - `update_cocktail(id: int, payload: CocktailUpdate) -> Cocktail` — partial update, can replace ingredient list
      - `delete_cocktail(id: int) -> None` — cascade-deletes CocktailIngredient links
  - Create `src/app/api/v1/routes_cocktails.py`:
    - `router = APIRouter(prefix="/cocktails", tags=["cocktails"])`
    - `POST /` → 201 + `CocktailRead`
    - `GET /` → 200 + `list[CocktailRead]` (flat)
    - `GET /{id}` → 200 + `CocktailReadFull` (nested with ingredients, amounts, flavor profile)
    - `PUT /{id}` → 200 + `CocktailReadFull`
    - `DELETE /{id}` → 204
  - Use `selectinload` for eager-loading relationships in `get_cocktail`
  - Wire router in `main.py`

  **Must NOT do**:
  - Do NOT lazy-load relationships outside session context
  - Do NOT return ingredient details in list endpoint (flat CocktailRead only)
  - Do NOT allow creating cocktail with non-existent ingredient IDs (validate first)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Most complex CRUD — nested creation, eager loading, partial updates, relationship management
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 5, 6, 8)
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 9, 10
  - **Blocked By**: Tasks 2, 3, 4

  **References**:

  **Pattern References**:
  - `instructions.mdc:388-426` — Route pattern with response_model and status codes
  - `instructions.mdc:630-658` — Service layer pattern
  - `instructions.mdc:406-412` — Create endpoint with model_validate and session.commit/refresh

  **External References**:
  - SQLModel selectinload: `https://sqlmodel.tiangolo.com/tutorial/fastapi/relationships/#use-selectinload`

  **WHY Each Reference Matters**:
  - selectinload prevents the N+1 query problem AND avoids lazy-load-outside-session errors
  - The model_validate pattern (406-412) shows how to convert Pydantic input to SQLModel instance

  **Acceptance Criteria**:
  - [ ] `POST /cocktails/` creates cocktail with ingredient links (including amounts)
  - [ ] `GET /cocktails/` returns flat list (no ingredient details)
  - [ ] `GET /cocktails/{id}` returns full details with ingredients, amounts, and flavor profile
  - [ ] `PUT /cocktails/{id}` updates cocktail and replaces ingredients
  - [ ] `DELETE /cocktails/{id}` removes cocktail and its ingredient links
  - [ ] Creating cocktail with non-existent ingredient_id returns 422 or 404
  - [ ] Duplicate cocktail name returns 409

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Create cocktail with ingredients and verify detail view
    Tool: Bash (curl)
    Preconditions: Ingredients "Tequila" (id=1) and "Lime Juice" (id=2) exist
    Steps:
      1. POST /cocktails/ with {"name": "Margarita", "instructions": "Shake all with ice, strain into coupe", "glass_type": "coupe", "difficulty": 2, "ingredients": [{"ingredient_id": 1, "amount": "2 oz"}, {"ingredient_id": 2, "amount": "1 oz"}]}
      2. Assert 201, capture cocktail id
      3. GET /cocktails/{id}
      4. Assert response has "ingredients" array with 2 items, each containing "amount"
      5. Assert response has "name" == "Margarita"
    Expected Result: Full cocktail with nested ingredients in detail view
    Failure Indicators: Missing ingredients in response, 500 error, missing amount field
    Evidence: .sisyphus/evidence/task-7-cocktail-create-detail.json

  Scenario: Cocktail with non-existent ingredient returns error
    Tool: Bash (curl)
    Preconditions: No ingredient with id=999
    Steps:
      1. POST /cocktails/ with {"name": "Ghost Drink", "instructions": "...", "glass_type": "coupe", "difficulty": 1, "ingredients": [{"ingredient_id": 999, "amount": "1 oz"}]}
      2. Assert 404 or 422 status
    Expected Result: Error response about non-existent ingredient
    Failure Indicators: 201 (succeeded with invalid data), 500 error
    Evidence: .sisyphus/evidence/task-7-invalid-ingredient.json
  ```

  **Commit**: YES
  - Message: `feat(api): add cocktail CRUD with nested ingredient management and eager loading`
  - Files: `src/app/services/cocktail_service.py, src/app/api/v1/routes_cocktails.py, src/app/main.py`
  - Pre-commit: `uv run ruff check .`

- [x] 8. Seed Script with 20+ Real Cocktails

  **What to do**:
  - Create `data/seed_cocktails.json` with 20+ real cocktail recipes:
    - Include classics: Margarita, Old Fashioned, Negroni, Daiquiri, Whiskey Sour, Manhattan, Mojito, Espresso Martini, Cosmopolitan, Moscow Mule, Aperol Spritz, Mai Tai, Sidecar, Tom Collins, Gimlet, Paloma, Dark 'n' Stormy, Penicillin, Last Word, Boulevardier
    - Each entry: name, description, instructions, glass_type, difficulty (1-5), ingredients (with real amounts), flavor tags per ingredient
  - Create `scripts/seed.py`:
    - Read JSON file
    - Create FlavorTags first (citrus, bitter, sweet, herbal, smoky, floral, spicy, umami, boozy, creamy)
    - Create Ingredients with flavor tag associations
    - Create Cocktails with ingredient links and amounts
    - Use service layer (not raw SQL)
    - Print summary: "Seeded X flavor tags, Y ingredients, Z cocktails"
  - Add `pyproject.toml` script entry: `[project.scripts] seed = "scripts.seed:main"`

  **Must NOT do**:
  - Do NOT use fake/placeholder data — use real cocktail recipes and amounts
  - Do NOT commit the resulting `.db` file
  - Do NOT seed via raw SQL — use the service layer

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Data entry + script writing, no architectural complexity
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 5, 6, 7)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 9
  - **Blocked By**: Tasks 2, 4

  **References**:

  **Pattern References**:
  - `instructions.mdc:686-726` — Seed command pattern using Typer CLI + JSON file + service layer
  - `instructions.mdc:703-709` — JSON sample data format

  **WHY Each Reference Matters**:
  - instructions.mdc:686-726 shows the exact seed pattern the course teaches (Typer command, JSON, service layer)
  - Using real cocktail data (not "Test Item 1") earns Empathy rubric points (20% weight) — shows domain knowledge

  **Acceptance Criteria**:
  - [ ] `data/seed_cocktails.json` contains 20+ real cocktail recipes with accurate ingredients
  - [ ] `uv run python scripts/seed.py` seeds the DB without errors
  - [ ] After seeding, `GET /cocktails/` returns 20+ items
  - [ ] Ingredients have correct flavor tags
  - [ ] Script is idempotent (running twice doesn't duplicate data) OR clears before seeding

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Seed script populates database
    Tool: Bash
    Preconditions: Clean database (no existing data)
    Steps:
      1. Run `uv run python scripts/seed.py`
      2. Assert output contains "Seeded" with counts
      3. Start server, curl GET /cocktails/
      4. Assert response array has ≥20 items
      5. curl GET /cocktails/1 and verify it has ingredients with amounts
    Expected Result: 20+ cocktails with real data, ingredients properly linked
    Failure Indicators: Empty response, missing ingredients, duplicate entries
    Evidence: .sisyphus/evidence/task-8-seed-populated.json

  Scenario: Seed data uses real cocktail recipes
    Tool: Bash (curl + jq)
    Preconditions: Database seeded
    Steps:
      1. curl GET /cocktails/ | jq '.[].name'
      2. Assert output contains "Margarita", "Old Fashioned", "Negroni"
      3. curl GET /cocktails/ with name filter for "Margarita"
      4. Verify ingredients include "Tequila" and "Lime Juice" with realistic amounts
    Expected Result: Real cocktail names with accurate ingredient lists
    Failure Indicators: Placeholder names like "Test Cocktail 1", missing ingredients
    Evidence: .sisyphus/evidence/task-8-real-data-check.json
  ```

  **Commit**: YES
  - Message: `feat(seed): add seed script with 20+ real cocktail recipes`
  - Files: `scripts/seed.py, data/seed_cocktails.json`
  - Pre-commit: `uv run python scripts/seed.py`

- [x] 9. Comprehensive Test Suite — All Endpoints + Failure Modes

  **What to do**:
  - Create/expand `tests/api/test_ingredients.py`:
    - Test create ingredient, list, get detail (with tags), delete, duplicate name 409, not found 404, invalid payload 422
  - Create `tests/api/test_flavor_tags.py`:
    - Test create, list, get, delete, duplicate 409, not found 404
  - Create/expand `tests/api/test_cocktails.py`:
    - Test create with ingredients, list (flat), get detail (nested), update, delete, duplicate name 409, invalid ingredient_id error, not found 404
  - Create `tests/services/test_cocktail_service.py`:
    - Unit tests for service layer: duplicate detection, ingredient validation, quantity adjustments
  - Run coverage, target ≥80%:
    ```bash
    uv run coverage run -m pytest
    uv run coverage report -m
    ```
  - All tests use conftest.py fixtures with `StaticPool` and `AsyncClient`

  **Must NOT do**:
  - Do NOT test only happy paths — failure modes are 20% of the rubric (Resilience)
  - Do NOT skip parametrize for input validation tests
  - Do NOT hardcode IDs in tests — use response IDs from create operations

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Comprehensive test writing requires understanding all endpoints and edge cases
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (needs all routes implemented)
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 11
  - **Blocked By**: Tasks 5, 6, 7, 8

  **References**:

  **Pattern References**:
  - `instructions.mdc:444-465` — Test pattern with AsyncClient, tmp_path, monkeypatch
  - `instructions.mdc:571-589` — Category + Item association test pattern
  - `instructions.mdc:592-599` — parametrize and failure mode testing (negative quantity → 422)

  **WHY Each Reference Matters**:
  - instructions.mdc:444-465 shows the exact test structure graders expect (AsyncClient + monkeypatch)
  - Failure mode tests (592-599) directly address the Resilience rubric dimension (20%)

  **Acceptance Criteria**:
  - [ ] `uv run pytest -q` — all tests pass
  - [ ] `uv run coverage report` shows ≥80% coverage
  - [ ] Tests cover: create, list, get, update, delete for each resource
  - [ ] Tests cover: 404, 409, 422 error cases
  - [ ] At least one `parametrize` for validation boundary testing

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Full test suite passes
    Tool: Bash
    Preconditions: All routes and services implemented
    Steps:
      1. Run `uv run pytest -q`
      2. Assert exit code 0
      3. Assert output shows 0 failures
      4. Count total tests — assert ≥15
    Expected Result: ≥15 tests, 0 failures
    Evidence: .sisyphus/evidence/task-9-pytest-results.txt

  Scenario: Coverage meets threshold
    Tool: Bash
    Preconditions: Tests passing
    Steps:
      1. Run `uv run coverage run -m pytest -q`
      2. Run `uv run coverage report -m`
      3. Assert total coverage ≥80%
    Expected Result: ≥80% statement coverage
    Failure Indicators: Coverage below 80%, uncovered critical paths
    Evidence: .sisyphus/evidence/task-9-coverage-report.txt
  ```

  **Commit**: YES
  - Message: `test: add comprehensive test suite with ≥80% coverage for all endpoints`
  - Files: `tests/**`
  - Pre-commit: `uv run pytest -q`

- [ ] 10. README + .http Playground File

  **What to do**:
  - Write `README.md` with:
    - Project title and one-paragraph description ("PotionLab is a cocktail recipe engine...")
    - Prerequisites: Python 3.12+, uv
    - Setup instructions: `uv venv && source .venv/bin/activate && uv sync`
    - Run API: `uv run uvicorn app.main:app --reload`
    - Run tests: `uv run pytest -q`
    - Seed data: `uv run python scripts/seed.py`
    - API endpoints table (method, path, description)
    - "AI Assistance" section (required by submission guidelines)
  - Create `examples.http` for VS Code REST Client:
    - Health check
    - Create flavor tag
    - Create ingredient with flavor tags
    - Create cocktail with ingredients
    - List all cocktails
    - Get cocktail detail
    - Update cocktail
    - Delete cocktail
  - Write `.env.example` with `SQLMODEL_DATABASE=data/app.db`

  **Must NOT do**:
  - Do NOT write a wall of text — keep README concise and actionable
  - Do NOT forget the "AI Assistance" section (submission requirement)

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: Documentation task — clear prose, structured README
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 9)
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 11
  - **Blocked By**: Tasks 5, 6, 7

  **References**:

  **Pattern References**:
  - `docs/exercises.md:36` — "README explaining how to create the uv environment, run the API locally, and execute the tests"
  - `docs/exercises.md:73-74` — Submission guideline: "AI Assistance" section required

  **Acceptance Criteria**:
  - [ ] README has setup, run, test, seed instructions
  - [ ] README has API endpoints table
  - [ ] README has "AI Assistance" section
  - [ ] `examples.http` has working requests for all endpoints
  - [ ] `.env.example` exists

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: README instructions work from scratch
    Tool: Bash
    Preconditions: Clean checkout of repo
    Steps:
      1. Follow README setup instructions exactly
      2. Run server command from README
      3. Run test command from README
      4. Run seed command from README
    Expected Result: All commands succeed without errors
    Evidence: .sisyphus/evidence/task-10-readme-walkthrough.txt
  ```

  **Commit**: YES
  - Message: `docs: add README with setup instructions, API reference, and .http playground`
  - Files: `README.md, examples.http, .env.example`

- [ ] 11. Final Quality Gate — Lint, Type-Check, Coverage

  **What to do**:
  - Run `uv run ruff check .` — fix any lint errors
  - Run `uv run mypy src` — fix any type errors
  - Run `uv run coverage run -m pytest && uv run coverage report -m` — verify ≥80%
  - Verify `uv run uvicorn app.main:app` starts cleanly
  - Verify seed script runs cleanly on fresh DB
  - Create git tag `ex1-final`

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Tasks 9, 10)
  - **Parallel Group**: Wave 3 (after 9, 10)
  - **Blocks**: Task 12 (EX2 start)
  - **Blocked By**: Tasks 9, 10

  **Acceptance Criteria**:
  - [ ] `ruff check .` → 0 errors
  - [ ] `mypy src` → 0 errors
  - [ ] `pytest` → all pass, ≥80% coverage
  - [ ] Server starts without warnings
  - [ ] Git tag `ex1-final` created

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: All quality gates pass
    Tool: Bash
    Steps:
      1. Run `uv run ruff check .` — assert exit code 0
      2. Run `uv run mypy src` — assert exit code 0
      3. Run `uv run pytest -q` — assert exit code 0
      4. Run `uv run coverage report` — assert ≥80%
    Expected Result: All 4 commands succeed
    Evidence: .sisyphus/evidence/task-11-quality-gates.txt
  ```

  **Commit**: YES
  - Message: `chore: pass all quality gates (ruff, mypy, coverage ≥80%)`
  - Pre-commit: `uv run ruff check . && uv run mypy src && uv run pytest -q`

### === PHASE 2: EX2 — Streamlit Dashboard (Due 18/05/2026) ===

- [ ] 12. Streamlit App Skeleton + API Client Module

  **What to do**:
  - Create `src/app/clients/api_client.py`:
    - `PotionLabClient` class wrapping `httpx.Client`
    - Methods: `list_cocktails()`, `get_cocktail(id)`, `create_cocktail(data)`, `list_ingredients()`, `create_ingredient(data)`, `list_flavor_tags()`, `search_cocktails_by_ingredients(ingredient_ids: list[int])`
    - Configure base_url from env var `POTIONLAB_API_URL` (default: `http://localhost:8000`)
    - Timeout: 5 seconds
    - Graceful error handling (return empty list on connection error, show user-friendly message)
  - Create `streamlit_app.py` (project root):
    - Multi-page layout using `st.sidebar` with pages: "Cocktail Browser", "Ingredient Explorer", "Mix a Cocktail", "What Can I Make?"
    - Basic page routing skeleton
    - API client instantiation
    - Title: "PotionLab" with cocktail emoji
  - Verify with `uv run streamlit run streamlit_app.py`

  **Must NOT do**:
  - Do NOT use `httpx.AsyncClient` in Streamlit — use synchronous client
  - Do NOT hardcode API URL
  - Do NOT skip error handling for API connection failures

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires setting up multi-page Streamlit architecture + API client
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (first EX2 task)
  - **Parallel Group**: Wave 4 (start)
  - **Blocks**: Tasks 13, 14, 15, 17
  - **Blocked By**: Task 11 (EX1 complete)

  **References**:

  **Pattern References**:
  - `instructions.mdc:871-906` — Streamlit app pattern with httpx client, st.table, st.form
  - `instructions.mdc:880-884` — `fetch_items()` pattern with httpx.Client, timeout, raise_for_status

  **External References**:
  - Streamlit multipage: `https://docs.streamlit.io/develop/concepts/multipage-apps`

  **WHY Each Reference Matters**:
  - instructions.mdc:871-906 is the exact Streamlit pattern the course teaches — follow it for consistency
  - The httpx.Client pattern with timeout matches what was taught in Session 2

  **Acceptance Criteria**:
  - [ ] `streamlit_app.py` loads without errors
  - [ ] Sidebar shows 4 page options
  - [ ] API client connects to backend and fetches data
  - [ ] Graceful error when API is not running (shows message, not crash)

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Streamlit dashboard loads with API data
    Tool: Playwright
    Preconditions: API running on :8000 with seeded data, Streamlit on :8501
    Steps:
      1. Navigate to http://localhost:8501
      2. Wait for page load (timeout: 10s)
      3. Assert page title contains "PotionLab"
      4. Assert sidebar contains "Cocktail Browser" link
      5. Click "Cocktail Browser"
      6. Assert page shows table or list of cocktails
    Expected Result: Dashboard loads, shows cocktail data from API
    Evidence: .sisyphus/evidence/task-12-streamlit-loads.png

  Scenario: Dashboard handles API being down gracefully
    Tool: Playwright
    Preconditions: Streamlit running, API NOT running
    Steps:
      1. Navigate to http://localhost:8501
      2. Click "Cocktail Browser"
      3. Assert page shows friendly error message (not Python traceback)
    Expected Result: User-friendly error like "Cannot connect to API"
    Evidence: .sisyphus/evidence/task-12-api-down-graceful.png
  ```

  **Commit**: YES
  - Message: `feat(ui): add Streamlit app skeleton with API client and multi-page layout`
  - Files: `streamlit_app.py, src/app/clients/api_client.py`

- [ ] 13. Cocktail Browser Page — Table + Detail View + Search

  **What to do**:
  - In `streamlit_app.py` (or `pages/cocktail_browser.py`):
    - Display cocktails in a `st.dataframe` with columns: Name, Glass Type, Difficulty (as stars), # Ingredients
    - Add search/filter bar: text search by name, filter by difficulty range, filter by glass type
    - Click-to-expand detail: when user selects a cocktail row, show full detail card:
      - Name, description, glass type, difficulty stars
      - Ingredients list with amounts (formatted nicely)
      - Instructions in a text block
      - Flavor profile tags as colored badges
    - Style with `st.columns` for layout, `st.expander` for instructions

  **Must NOT do**:
  - Do NOT use raw JSON display — format everything nicely
  - Do NOT overcrowd the page — use expanders and columns

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: UI layout, visual design, data display formatting
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 14, 15)
  - **Parallel Group**: Wave 4
  - **Blocks**: Tasks 16, 18
  - **Blocked By**: Task 12

  **References**:

  **Pattern References**:
  - `instructions.mdc:887-889` — `st.table(items)` pattern
  - `instructions.mdc:891-901` — `st.form` with text_input and number_input pattern

  **Acceptance Criteria**:
  - [ ] Cocktail table displays with sortable columns
  - [ ] Search by name filters results in real-time
  - [ ] Detail view shows ingredients with amounts
  - [ ] Difficulty displayed as visual indicator (stars/emoji)

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Browse and search cocktails
    Tool: Playwright
    Preconditions: API running with seeded data, Streamlit on :8501
    Steps:
      1. Navigate to Cocktail Browser page
      2. Assert table shows ≥20 rows
      3. Type "Margarita" in search box
      4. Assert filtered results show "Margarita"
      5. Click on Margarita row/expander
      6. Assert detail view shows "Tequila" in ingredients
    Expected Result: Search filters work, detail view shows ingredient amounts
    Evidence: .sisyphus/evidence/task-13-cocktail-browser.png
  ```

  **Commit**: YES (groups with 14, 15)
  - Message: `feat(ui): add cocktail browser with search, filters, and detail view`

- [ ] 14. Ingredient Explorer Page

  **What to do**:
  - Ingredient Explorer page:
    - Display all ingredients in a grid/list with category badges (spirit, mixer, liqueur, etc.)
    - Filter by category dropdown
    - Each ingredient shows: name, category, description, flavor tag badges (colored pills)
    - Click ingredient to see which cocktails use it

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 13, 15)
  - **Parallel Group**: Wave 4
  - **Blocks**: Task 18
  - **Blocked By**: Task 12

  **Acceptance Criteria**:
  - [ ] All ingredients displayed with category and flavor tags
  - [ ] Category filter works
  - [ ] Clicking ingredient shows associated cocktails

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Browse ingredients with flavor tags
    Tool: Playwright
    Preconditions: API running with seeded data
    Steps:
      1. Navigate to Ingredient Explorer
      2. Assert page shows ingredient cards/list
      3. Select "spirit" from category filter
      4. Assert only spirits shown (Tequila, Vodka, Gin, etc.)
      5. Click on "Tequila"
      6. Assert shows cocktails that use Tequila (e.g., Margarita, Paloma)
    Expected Result: Filtered view with category badges and cocktail associations
    Evidence: .sisyphus/evidence/task-14-ingredient-explorer.png
  ```

  **Commit**: YES (groups with 13, 15)
  - Message: `feat(ui): add ingredient explorer with category filters and flavor tags`

- [ ] 15. Add New Cocktail Form (Multi-Step)

  **What to do**:
  - "Mix a Cocktail" page with multi-section form:
    - Section 1: Basic info (name, description, glass_type dropdown, difficulty slider 1-5)
    - Section 2: Ingredients (dynamic list — add/remove ingredient rows with ingredient dropdown + amount input + optional checkbox)
    - Section 3: Instructions (text area)
    - Submit button → POST to API → show success/error
    - On success: show the created cocktail detail and clear form
    - On validation error: show field-specific error messages (not raw JSON)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 13, 14)
  - **Parallel Group**: Wave 4
  - **Blocks**: Task 18
  - **Blocked By**: Task 12

  **Acceptance Criteria**:
  - [ ] Form has all required fields with appropriate input types
  - [ ] Can add/remove ingredient rows dynamically
  - [ ] Successful submit creates cocktail and shows confirmation
  - [ ] Validation errors display user-friendly messages
  - [ ] Glass type uses dropdown (not free text)

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Create cocktail via form
    Tool: Playwright
    Preconditions: API running, Streamlit on :8501
    Steps:
      1. Navigate to "Mix a Cocktail" page
      2. Fill name: "Test Fizz"
      3. Select glass_type: "highball"
      4. Set difficulty: 1
      5. Add ingredient row: select "Vodka", amount "2 oz"
      6. Add instructions: "Build over ice"
      7. Click Submit
      8. Assert success message appears
      9. Navigate to Cocktail Browser
      10. Assert "Test Fizz" appears in list
    Expected Result: Cocktail created via form appears in browser
    Evidence: .sisyphus/evidence/task-15-create-cocktail-form.png

  Scenario: Form shows validation errors
    Tool: Playwright
    Preconditions: API running
    Steps:
      1. Navigate to "Mix a Cocktail"
      2. Leave name empty, click Submit
      3. Assert error message about required name
    Expected Result: User-friendly validation error displayed
    Evidence: .sisyphus/evidence/task-15-form-validation-error.png
  ```

  **Commit**: YES (groups with 13, 14)
  - Message: `feat(ui): add cocktail creation form with dynamic ingredient rows`

- [ ] 16. Flavor Wheel Visualization (Plotly Polar Chart)

  **What to do**:
  - Add `plotly` dependency: `uv add plotly`
  - Create a flavor wheel component:
    - Analyze all cocktails' ingredient flavor tags
    - Build a polar/radar chart where each spoke is a flavor category (citrus, bitter, sweet, herbal, smoky, floral, spicy, umami)
    - Value = count of ingredients with that flavor tag across the collection
    - Display on Cocktail Browser page as a summary visualization
    - Also show per-cocktail flavor profile as a mini radar chart in detail view
  - Use `plotly.graph_objects.Scatterpolar` for the radar chart
  - Display via `st.plotly_chart`

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: Data visualization with plotly — needs aesthetic sensibility
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 17)
  - **Parallel Group**: Wave 5
  - **Blocks**: Task 18
  - **Blocked By**: Task 13

  **Acceptance Criteria**:
  - [ ] Collection-level flavor wheel shows all 8 flavor categories
  - [ ] Per-cocktail mini radar chart in detail view
  - [ ] Charts are visually polished (colors, labels, legend)
  - [ ] Charts update when data changes

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Flavor wheel renders with data
    Tool: Playwright
    Preconditions: API running with seeded data
    Steps:
      1. Navigate to Cocktail Browser
      2. Assert plotly chart element exists on page (css: `.js-plotly-plot`)
      3. Screenshot the flavor wheel
      4. Assert chart has labeled spokes (citrus, bitter, sweet, etc.)
    Expected Result: Polar chart visible with 8 flavor categories
    Evidence: .sisyphus/evidence/task-16-flavor-wheel.png
  ```

  **Commit**: YES
  - Message: `feat(ui): add flavor wheel radar chart visualization with plotly`
  - Files: `streamlit_app.py`

- [ ] 17. "What Can I Make?" Basic Filter Page

  **What to do**:
  - Create "What Can I Make?" page:
    - `st.multiselect` for selecting ingredients you have (populated from API ingredient list)
    - On selection change: query API to find cocktails that can be made with selected ingredients
    - Add backend endpoint if needed: `GET /cocktails/search?available_ingredients=1,2,3`
    - Display results: cocktails you CAN make (all required ingredients available) + cocktails you're CLOSE to (missing 1-2 ingredients, show what's missing)
    - Sort by: fewest missing ingredients first
  - Add the search endpoint in `routes_cocktails.py` if it doesn't exist

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires new API endpoint + Streamlit UI + matching algorithm
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 16)
  - **Parallel Group**: Wave 5
  - **Blocks**: Task 18
  - **Blocked By**: Task 12

  **Acceptance Criteria**:
  - [ ] Multiselect populated with all ingredients from API
  - [ ] Selecting ingredients filters cocktail list
  - [ ] "Can make" cocktails shown separately from "almost can make"
  - [ ] Missing ingredients clearly listed for "almost" matches

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Find cocktails with available ingredients
    Tool: Playwright
    Preconditions: API running with seeded data
    Steps:
      1. Navigate to "What Can I Make?"
      2. Select "Tequila", "Lime Juice", "Triple Sec" from multiselect
      3. Assert "Margarita" appears in "Can Make" section
      4. Assert "Paloma" appears in "Almost" section (missing grapefruit soda)
    Expected Result: Accurate matching with missing ingredient display
    Evidence: .sisyphus/evidence/task-17-what-can-i-make.png

  Scenario: Empty selection shows all cocktails or prompt
    Tool: Playwright
    Steps:
      1. Navigate to "What Can I Make?" with no ingredients selected
      2. Assert helpful prompt like "Select ingredients to find cocktails"
    Expected Result: Helpful empty state message
    Evidence: .sisyphus/evidence/task-17-empty-state.png
  ```

  **Commit**: YES
  - Message: `feat(ui): add "What Can I Make?" ingredient-based cocktail finder`

- [ ] 18. EX2 README + Side-by-Side Launch Documentation

  **What to do**:
  - Update README.md:
    - Add EX2 section: "Running the Dashboard"
    - Side-by-side instructions: "Terminal 1: `uv run uvicorn app.main:app --reload`, Terminal 2: `uv run streamlit run streamlit_app.py`"
    - Describe each page's purpose
    - Screenshot or description of key features
  - Update "AI Assistance" section for EX2 work

  **Recommended Agent Profile**:
  - **Category**: `writing`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (needs all UI tasks complete)
  - **Parallel Group**: Wave 5 (after 13-17)
  - **Blocks**: Task 19
  - **Blocked By**: Tasks 13-17

  **Acceptance Criteria**:
  - [ ] README has clear side-by-side launch instructions
  - [ ] Each dashboard page documented

  **Commit**: YES
  - Message: `docs: add EX2 dashboard documentation and launch instructions`

- [ ] 19. Bonus: Automated Streamlit Test

  **What to do**:
  - Create `tests/ui/test_streamlit.py`:
    - Use subprocess to launch Streamlit in test mode OR use `streamlit.testing` if available
    - Alternatively: test the API client module directly (simpler, still earns bonus)
    - Test: `PotionLabClient.list_cocktails()` returns data, `PotionLabClient.create_cocktail(valid_data)` returns 201
  - This earns the +5 bonus for EX2

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 18)
  - **Parallel Group**: Wave 5
  - **Blocks**: None
  - **Blocked By**: Task 12

  **Acceptance Criteria**:
  - [ ] At least one automated test exercising the Streamlit interface or API client
  - [ ] Test passes in CI

  **Commit**: YES
  - Message: `test: add automated Streamlit API client test for EX2 bonus`

### === PHASE 3: EX3 — Capstone Integration (Due 01/07/2026) ===

- [ ] 20. Migrate SQLite → PostgreSQL

  **What to do**:
  - Add `psycopg[binary]` dependency: `uv add "psycopg[binary]"`
  - Update `src/app/db/session.py`:
    - Read `DATABASE_URL` env var (PostgreSQL connection string)
    - If `DATABASE_URL` set → use PostgreSQL engine with `pool_pre_ping=True`
    - If not set → fall back to SQLite (for local dev/tests)
  - Create `scripts/init_db.py` that runs `init_db()` for PostgreSQL
  - Update seed script to work with PostgreSQL
  - Test: verify existing tests still pass with SQLite (backward compatible)

  **Must NOT do**:
  - Do NOT remove SQLite support — keep dual-mode for tests
  - Do NOT commit Postgres credentials

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 22, 23)
  - **Parallel Group**: Wave 6
  - **Blocks**: Task 21
  - **Blocked By**: Task 11

  **References**:

  **Pattern References**:
  - `instructions.mdc:370-375` — Dual-mode engine creation (DATABASE_URL or SQLite)
  - `docker-compose.yml:1-20` — Existing Postgres config in course repo

  **Acceptance Criteria**:
  - [ ] `DATABASE_URL` env var switches to PostgreSQL
  - [ ] All existing tests still pass (SQLite mode)
  - [ ] Seed script works with PostgreSQL

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: API works with PostgreSQL via Docker
    Tool: Bash
    Preconditions: Postgres container running
    Steps:
      1. Start Postgres: `docker run --rm -d -p 5432:5432 -e POSTGRES_PASSWORD=potion postgres:16-alpine`
      2. Export DATABASE_URL=postgresql+psycopg://postgres:potion@localhost:5432/postgres
      3. Run `uv run python scripts/init_db.py`
      4. Run `uv run python scripts/seed.py`
      5. Start API, curl GET /cocktails/
      6. Assert ≥20 cocktails returned
    Expected Result: Full API works against PostgreSQL
    Evidence: .sisyphus/evidence/task-20-postgres-migration.json
  ```

  **Commit**: YES
  - Message: `feat(db): add PostgreSQL support with dual-mode engine (Postgres/SQLite)`

- [ ] 21. Docker Compose Setup (API + Postgres + Redis)

  **What to do**:
  - Create `Dockerfile` for the API:
    - Multi-stage build: uv builder → python slim runtime
    - Follow course pattern from Meeting 10
    - Expose port 8000
  - Create `compose.yaml`:
    - `api` service: build from Dockerfile, ports 8000:8000, depends on db + redis
    - `db` service: postgres:16-alpine with health check, volume for data persistence
    - `redis` service: redis:7-alpine with health check
    - Environment variables for DATABASE_URL and REDIS_URL
    - `.env` file for secrets (not committed)
  - Create `docs/runbooks/compose.md`:
    - How to launch: `docker compose up --build`
    - How to verify health: `curl localhost:8000/health`
    - How to check Redis: `docker compose exec redis redis-cli ping`
    - How to run tests: `docker compose exec api pytest`
    - How to tear down: `docker compose down -v`

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Task 20)
  - **Parallel Group**: Wave 6
  - **Blocks**: Tasks 24, 28
  - **Blocked By**: Task 20

  **References**:

  **Pattern References**:
  - `instructions.mdc:1133-1147` — Dockerfile with uv multi-stage build
  - `instructions.mdc:1155-1177` — docker-compose.yml with API + Postgres + volumes

  **Acceptance Criteria**:
  - [ ] `docker compose up --build` starts all 3 services
  - [ ] API health check passes via curl
  - [ ] PostgreSQL health check passes
  - [ ] Redis PING returns PONG
  - [ ] `docs/runbooks/compose.md` covers launch, verify, test, teardown

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Full Compose stack starts and is healthy
    Tool: Bash
    Steps:
      1. Run `docker compose up --build -d`
      2. Wait for health checks (timeout: 30s)
      3. curl -s localhost:8000/health | jq
      4. Assert {"status": "ok"}
      5. docker compose exec redis redis-cli ping
      6. Assert "PONG"
      7. docker compose down
    Expected Result: All services healthy, API accessible
    Evidence: .sisyphus/evidence/task-21-compose-stack.txt
  ```

  **Commit**: YES
  - Message: `feat(infra): add Docker Compose with API, PostgreSQL, and Redis`

- [ ] 22. JWT Authentication Module

  **What to do**:
  - Add dependencies: `uv add "passlib[bcrypt]" python-jose[cryptography]`
  - Create `src/app/core/security.py`:
    - `hash_password(plain: str) -> str` using `passlib.context.CryptContext(schemes=["bcrypt"])`
    - `verify_password(plain: str, hashed: str) -> bool` with timing attack prevention (always verify against dummy hash on missing user)
    - `create_access_token(data: dict, expires_delta: timedelta) -> str` using python-jose JWT
    - `decode_access_token(token: str) -> dict` with expiry validation
    - `require_auth` dependency that extracts + validates Bearer token from Authorization header
    - `require_role(role: str)` dependency for role-based checks
  - Create `src/app/models/user.py`:
    - `User(SQLModel, table=True)`: id, username (unique), hashed_password, role (str, default="reader")
  - Create `src/app/api/v1/routes_auth.py`:
    - `POST /auth/register` → create user with hashed password
    - `POST /auth/token` → verify credentials, return JWT
  - Update `init_db()` to include User table
  - Store JWT secret in env var `POTION_JWT_SECRET`

  **Must NOT do**:
  - Do NOT use `pwdlib` — use `passlib[bcrypt]` as taught in course
  - Do NOT hardcode JWT secret — use env var
  - Do NOT implement OAuth/OIDC — keep it simple JWT

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Security implementation requires careful handling of hashing, tokens, and timing attacks
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 20, 23)
  - **Parallel Group**: Wave 6
  - **Blocks**: Task 27
  - **Blocked By**: Task 11

  **References**:

  **Pattern References**:
  - `instructions.mdc:1193-1206` — Security module with API key pattern (adapt for JWT)
  - `instructions.mdc:1207-1217` — Router-level dependency for auth protection

  **External References**:
  - FastAPI Security docs: `https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/`
  - passlib bcrypt: `https://passlib.readthedocs.io/en/stable/lib/passlib.hash.bcrypt.html`

  **WHY Each Reference Matters**:
  - instructions.mdc:1193-1206 shows the auth dependency pattern — adapt from API key to JWT Bearer
  - The course teaches `passlib[bcrypt]` specifically — using anything else will confuse graders

  **Acceptance Criteria**:
  - [ ] `POST /auth/register` creates user with bcrypt-hashed password
  - [ ] `POST /auth/token` returns valid JWT for correct credentials
  - [ ] `POST /auth/token` returns 401 for wrong password (with timing attack prevention)
  - [ ] Protected endpoints reject requests without valid JWT
  - [ ] Role-based access works (e.g., "admin" can delete, "reader" cannot)

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Auth flow — register, login, access protected endpoint
    Tool: Bash (curl)
    Steps:
      1. POST /auth/register with {"username": "bartender", "password": "shaken-not-stirred"}
      2. Assert 201
      3. POST /auth/token with {"username": "bartender", "password": "shaken-not-stirred"}
      4. Assert 200 and response contains "access_token"
      5. GET /cocktails/ with Authorization: Bearer <token>
      6. Assert 200
    Expected Result: Full auth flow works end-to-end
    Evidence: .sisyphus/evidence/task-22-auth-flow.json

  Scenario: Expired/invalid token rejected
    Tool: Bash (curl)
    Steps:
      1. GET /cocktails/ with Authorization: Bearer invalid-token-here
      2. Assert 401
      3. Assert response body contains "Could not validate"
    Expected Result: 401 Unauthorized with descriptive error
    Evidence: .sisyphus/evidence/task-22-invalid-token.json
  ```

  **Commit**: YES
  - Message: `feat(auth): add JWT authentication with bcrypt hashing and role checks`

- [ ] 23. Redis Integration — Connection + Caching Utilities

  **What to do**:
  - Add dependency: `uv add redis`
  - Create `src/app/core/redis_client.py`:
    - `get_redis()` → `redis.Redis` from `REDIS_URL` env var (default: `redis://localhost:6379`)
    - `cache_get(key: str) -> str | None`
    - `cache_set(key: str, value: str, ttl: int = 3600)`
    - `cache_delete(key: str)`
    - `is_processed(idempotency_key: str) -> bool` (for async worker idempotency)
    - `mark_processed(idempotency_key: str, ttl: int = 86400)`
  - Add Redis health check in health endpoint
  - Test utilities with mock Redis (or skip Redis in tests if `REDIS_URL` not set)

  **Must NOT do**:
  - Do NOT require Redis for tests — make it optional with fallback
  - Do NOT use Redis for primary data storage — only caching and idempotency

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 20, 22)
  - **Parallel Group**: Wave 6
  - **Blocks**: Tasks 24, 25, 26
  - **Blocked By**: Task 11

  **References**:

  **Pattern References**:
  - `docs/exercises.md:62` — "Redis-backed idempotency" requirement for scripts/refresh.py

  **Acceptance Criteria**:
  - [ ] Redis client connects when REDIS_URL is set
  - [ ] Cache get/set/delete work
  - [ ] Idempotency check works (mark_processed + is_processed)
  - [ ] Health endpoint includes Redis status
  - [ ] Tests pass without Redis (graceful degradation)

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Redis caching works
    Tool: Bash
    Preconditions: Redis running (via Docker or Compose)
    Steps:
      1. Run `uv run python -c "from app.core.redis_client import cache_set, cache_get; cache_set('test', 'hello', 60); print(cache_get('test'))"`
      2. Assert output is "hello"
    Expected Result: Cache set and get work
    Evidence: .sisyphus/evidence/task-23-redis-cache.txt

  Scenario: Health check includes Redis status
    Tool: Bash (curl)
    Preconditions: API + Redis running
    Steps:
      1. curl -s localhost:8000/health | jq
      2. Assert response includes redis: "connected" or similar
    Expected Result: Health endpoint reports Redis status
    Evidence: .sisyphus/evidence/task-23-redis-health.json
  ```

  **Commit**: YES
  - Message: `feat(cache): add Redis client with caching utilities and idempotency support`

- [ ] 24. AI Mixologist Microservice (Gemini Integration)

  **What to do**:
  - Create `ai_service/` directory as a separate FastAPI app:
    - `ai_service/main.py`: FastAPI app on port 8001
    - `ai_service/gemini_client.py`: Google Generative AI client
      - `generate_cocktail(available_ingredients: list[str], mood: str | None, preferences: str | None) -> CocktailSuggestion`
      - Use structured output: Pydantic model for response (name, ingredients with amounts, instructions, flavor_profile, why_this_works)
      - Client-side rate limiting: max 15 RPM (Gemini free tier limit)
      - Cache responses in Redis (key = sorted ingredient hash, TTL = 3600s)
    - `ai_service/schemas.py`: `MixRequest(BaseModel)` and `CocktailSuggestion(BaseModel)`
  - Endpoints:
    - `POST /mix` → takes available ingredients + mood → returns AI-generated cocktail
    - `GET /health` → health check
  - Add to compose.yaml as `ai_service` service
  - Add `GOOGLE_API_KEY` to `.env` (not committed)
  - Install: `uv add google-generativeai`

  **Must NOT do**:
  - Do NOT expose raw Gemini responses — always parse through Pydantic schema
  - Do NOT exceed 15 RPM — implement client-side rate limiting
  - Do NOT skip Redis caching — every AI response must be cached
  - Do NOT commit API keys

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: External API integration + structured output + rate limiting + caching — complex orchestration
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 25, 26, 27)
  - **Parallel Group**: Wave 7
  - **Blocks**: Tasks 26, 28, 30
  - **Blocked By**: Tasks 21, 23

  **References**:

  **External References**:
  - Google Generative AI Python: `https://ai.google.dev/gemini-api/docs/get-started/python`
  - Gemini structured output: `https://ai.google.dev/gemini-api/docs/structured-output`
  - Gemini rate limits: 15 RPM free tier

  **WHY Each Reference Matters**:
  - Structured output ensures AI returns parseable Pydantic-compatible JSON, not freeform text
  - Rate limiting is critical to avoid 429 errors during demo (Metis flagged this)

  **Acceptance Criteria**:
  - [ ] `POST /mix` returns structured CocktailSuggestion
  - [ ] Response cached in Redis (second call with same ingredients is instant)
  - [ ] Rate limiting prevents >15 RPM
  - [ ] Health check passes
  - [ ] Service runs as separate container in Compose

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: AI generates cocktail suggestion
    Tool: Bash (curl)
    Preconditions: AI service running with GOOGLE_API_KEY set
    Steps:
      1. POST http://localhost:8001/mix with {"ingredients": ["vodka", "lime juice", "ginger beer"], "mood": "refreshing"}
      2. Assert 200 status
      3. Assert response has fields: name, ingredients (array), instructions (string), flavor_profile (array)
      4. Assert response is valid JSON matching CocktailSuggestion schema
    Expected Result: Structured cocktail suggestion with name, ingredients, instructions
    Failure Indicators: 500 error, unstructured text response, missing fields
    Evidence: .sisyphus/evidence/task-24-ai-suggestion.json

  Scenario: Response is cached in Redis
    Tool: Bash (curl + redis-cli)
    Preconditions: AI service + Redis running
    Steps:
      1. POST /mix with {"ingredients": ["gin", "tonic"]}
      2. Record response time
      3. POST /mix with same ingredients again
      4. Assert second response is significantly faster (<100ms vs first call)
      5. Check Redis: `redis-cli keys '*gin*tonic*'` shows cached entry
    Expected Result: Second call served from cache
    Evidence: .sisyphus/evidence/task-24-redis-cache-hit.txt
  ```

  **Commit**: YES
  - Message: `feat(ai): add AI Mixologist microservice with Gemini, rate limiting, and Redis caching`

- [ ] 25. scripts/refresh.py — Async Refresher with Bounded Concurrency

  **What to do**:
  - Create `scripts/refresh.py`:
    - Async script that refreshes AI cocktail suggestions for all cocktails in DB
    - Uses `anyio` or `asyncio` with bounded concurrency (Semaphore, max 5 concurrent)
    - For each cocktail: extract ingredients → call AI service → cache result
    - Redis-backed idempotency: skip cocktails already refreshed (check `mark_processed`)
    - Retries: 3 attempts with exponential backoff on failure
    - Structured logging with request timing
    - Progress bar with `rich.progress`
  - Add at least one `pytest.mark.anyio` test (or `pytest.mark.asyncio`):
    - Test bounded concurrency (mock AI service, verify max N concurrent calls)
    - Test idempotency (mock Redis, verify skip on already-processed)
  - Paste a log/trace excerpt into `docs/EX3-notes.md`

  **Must NOT do**:
  - Do NOT make unlimited concurrent requests (respect Gemini rate limits)
  - Do NOT skip the idempotency check

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Async concurrency, retries, idempotency, testing — multi-concern complexity
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 24, 26, 27)
  - **Parallel Group**: Wave 7
  - **Blocks**: Task 29
  - **Blocked By**: Task 23

  **References**:

  **Pattern References**:
  - `instructions.mdc:744-776` — Async search with `anyio.to_thread.run_sync` pattern
  - `docs/exercises.md:62` — "scripts/refresh.py with bounded concurrency, retries, and Redis-backed idempotency plus at least one pytest.mark.anyio test"

  **Acceptance Criteria**:
  - [ ] Script runs: `uv run python scripts/refresh.py`
  - [ ] Bounded concurrency (max 5 concurrent) verified
  - [ ] Redis idempotency prevents re-processing
  - [ ] Retry with exponential backoff on failures
  - [ ] At least one `pytest.mark.anyio` test passes
  - [ ] Log excerpt pasted in `docs/EX3-notes.md`

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Refresh script processes cocktails with bounded concurrency
    Tool: Bash
    Preconditions: API + Redis + AI service running, DB seeded
    Steps:
      1. Run `uv run python scripts/refresh.py`
      2. Assert output shows progress (X/20 cocktails processed)
      3. Assert no more than 5 concurrent requests logged
      4. Run again — assert "already processed" skips
    Expected Result: All cocktails processed, idempotency prevents re-processing
    Evidence: .sisyphus/evidence/task-25-refresh-output.txt
  ```

  **Commit**: YES
  - Message: `feat(async): add refresh script with bounded concurrency and Redis idempotency`

- [ ] 26. Enhanced "What Can I Make?" with AI Substitution Suggestions

  **What to do**:
  - Enhance the "What Can I Make?" feature (from Task 17):
    - When user is missing 1-2 ingredients for a cocktail, add "AI Suggest Substitution" button
    - Button calls AI Mixologist service: "I want to make [cocktail] but I'm missing [ingredients]. What can I substitute?"
    - AI returns substitution suggestions with rationale
    - Display substitutions inline with the cocktail card
  - Update Streamlit page to include the AI button
  - Update API to proxy to AI service OR call AI service directly from Streamlit client

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 25, 27)
  - **Parallel Group**: Wave 7
  - **Blocks**: Task 28
  - **Blocked By**: Task 24

  **Acceptance Criteria**:
  - [ ] "Suggest Substitution" button appears for cocktails missing ≤2 ingredients
  - [ ] AI returns meaningful substitution suggestions
  - [ ] Suggestions displayed inline with cocktail card

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: AI suggests ingredient substitution
    Tool: Playwright
    Preconditions: Full stack running, user has selected some ingredients
    Steps:
      1. Navigate to "What Can I Make?"
      2. Select ingredients that are close to making a Margarita (e.g., Tequila + Lime Juice but missing Triple Sec)
      3. Find Margarita in "Almost Can Make" section
      4. Click "Suggest Substitution" button
      5. Assert AI suggestion appears (e.g., "Use orange juice or Cointreau as a substitute for Triple Sec")
    Expected Result: Meaningful substitution suggestion displayed
    Evidence: .sisyphus/evidence/task-26-ai-substitution.png
  ```

  **Commit**: YES
  - Message: `feat(enhance): add AI-powered ingredient substitution suggestions`

- [ ] 27. Protect Mutation Endpoints with JWT + Role Checks

  **What to do**:
  - Apply `require_auth` dependency to mutation endpoints:
    - `POST /cocktails/`, `PUT /cocktails/{id}`, `DELETE /cocktails/{id}` → require "editor" or "admin" role
    - `POST /ingredients/`, `DELETE /ingredients/{id}` → require "editor" or "admin"
    - `POST /flavor-tags/`, `DELETE /flavor-tags/{id}` → require "admin"
    - `GET` endpoints remain public (no auth required for reading)
  - Update tests to include auth headers where needed
  - Add seed user (admin) in seed script for demo purposes

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 24, 25, 26)
  - **Parallel Group**: Wave 7
  - **Blocks**: Tasks 28, 30
  - **Blocked By**: Task 22

  **References**:

  **Pattern References**:
  - `instructions.mdc:1207-1217` — Router-level dependency for auth
  - `instructions.mdc:1219-1229` — Auth test pattern with monkeypatch

  **Acceptance Criteria**:
  - [ ] GET endpoints work without auth
  - [ ] POST/PUT/DELETE require valid JWT
  - [ ] Role checks enforced (reader can't delete, admin can)
  - [ ] Tests include auth headers
  - [ ] Existing tests updated for auth

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Unauthenticated mutation rejected
    Tool: Bash (curl)
    Steps:
      1. POST /cocktails/ without Authorization header
      2. Assert 401
    Expected Result: 401 Unauthorized
    Evidence: .sisyphus/evidence/task-27-unauth-rejected.json

  Scenario: Role-based access control
    Tool: Bash (curl)
    Steps:
      1. Register user with role "reader"
      2. Get token for reader
      3. POST /cocktails/ with reader token
      4. Assert 403 Forbidden
      5. Register user with role "editor"
      6. Get token for editor
      7. POST /cocktails/ with editor token
      8. Assert 201 Created
    Expected Result: Reader blocked, editor allowed
    Evidence: .sisyphus/evidence/task-27-rbac.json
  ```

  **Commit**: YES
  - Message: `feat(auth): protect mutation endpoints with JWT role-based access control`

- [ ] 28. Demo Script

  **What to do**:
  - Create `scripts/demo.sh` (or `python -m app.demo`):
    - Start with clear instructions: "Starting PotionLab Demo..."
    - Step 1: Verify all services are running (health checks for API, Redis, AI service)
    - Step 2: Seed database if empty
    - Step 3: Register demo user and get JWT token
    - Step 4: Show cocktail listing via curl
    - Step 5: Create a new cocktail via API (authenticated)
    - Step 6: Show "What Can I Make?" flow (select ingredients, show matches)
    - Step 7: Call AI Mixologist to generate a new cocktail
    - Step 8: Open Streamlit URL in browser (or print URL)
    - Each step: print what's happening, show the command, show the output
    - Color-coded output with success/failure indicators

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (needs everything built)
  - **Parallel Group**: Wave 8
  - **Blocks**: Task 29
  - **Blocked By**: Tasks 21, 24, 26, 27

  **Acceptance Criteria**:
  - [ ] `scripts/demo.sh` runs end-to-end without errors
  - [ ] Each step has clear output explaining what's happening
  - [ ] Demo completes in under 2 minutes

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Demo script runs end-to-end
    Tool: Bash
    Preconditions: docker compose up running
    Steps:
      1. Run `bash scripts/demo.sh`
      2. Assert exit code 0
      3. Assert output contains "Demo complete" or similar
      4. Assert no error messages in output
    Expected Result: Full demo flow completes successfully
    Evidence: .sisyphus/evidence/task-28-demo-run.txt
  ```

  **Commit**: YES
  - Message: `feat(demo): add end-to-end demo script showcasing all features`

- [ ] 29. Documentation — EX3-notes.md + Runbook

  **What to do**:
  - Create/update `docs/EX3-notes.md`:
    - Architecture overview diagram (ASCII or Mermaid)
    - Service descriptions (API, Postgres, Redis, AI Mixologist)
    - Design decisions and trade-offs
    - JWT rotation steps
    - Log/trace excerpt from refresh.py run
    - Enhancement description ("What Can I Make?" with AI substitutions)
  - Verify `docs/runbooks/compose.md` (from Task 21) is complete
  - Update main README.md with EX3 section
  - Update "AI Assistance" section

  **Recommended Agent Profile**:
  - **Category**: `writing`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 30)
  - **Parallel Group**: Wave 8
  - **Blocks**: Task 31
  - **Blocked By**: All EX3 implementation tasks

  **Acceptance Criteria**:
  - [ ] `docs/EX3-notes.md` has architecture diagram, decisions, trace excerpts
  - [ ] `docs/runbooks/compose.md` covers launch, verify, test, teardown
  - [ ] README updated for EX3

  **Commit**: YES
  - Message: `docs: add EX3-notes with architecture, decisions, and runbook`

- [ ] 30. EX3 Integration Test Suite

  **What to do**:
  - Create `tests/integration/test_compose_stack.py`:
    - Test API health check
    - Test full auth flow (register → login → create cocktail → verify)
    - Test AI Mixologist endpoint returns valid response
    - Test "What Can I Make?" with AI substitution
  - Create `tests/services/test_auth.py`:
    - Test password hashing
    - Test JWT creation/validation
    - Test expired token rejection
    - Test timing attack prevention (verify_password always takes similar time)
  - Ensure all existing tests still pass with auth changes

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 28, 29)
  - **Parallel Group**: Wave 8
  - **Blocks**: Task 31
  - **Blocked By**: Tasks 24, 27

  **Acceptance Criteria**:
  - [ ] Integration tests pass against running Compose stack
  - [ ] Auth tests cover hashing, JWT, expiry, timing
  - [ ] All EX1/EX2 tests still pass
  - [ ] Coverage ≥80% across full codebase

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Integration tests pass
    Tool: Bash
    Preconditions: Compose stack running
    Steps:
      1. Run `uv run pytest tests/ -q`
      2. Assert all tests pass
      3. Run coverage report
      4. Assert ≥80%
    Expected Result: Full test suite green with ≥80% coverage
    Evidence: .sisyphus/evidence/task-30-integration-tests.txt
  ```

  **Commit**: YES
  - Message: `test: add integration tests for auth, AI service, and full stack`

- [ ] 31. Final Quality Gate — Lint, Type-Check, Compose Smoke Test

  **What to do**:
  - Run full quality suite:
    - `uv run ruff check .`
    - `uv run mypy src`
    - `uv run pytest -q` (all tests)
    - `docker compose up --build -d` → health checks → `docker compose down`
  - Fix any issues
  - Create git tag `ex3-final`
  - Verify demo script one final time

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (final gate)
  - **Parallel Group**: Wave 8 (last)
  - **Blocks**: F1-F4
  - **Blocked By**: Tasks 28, 29, 30

  **Acceptance Criteria**:
  - [ ] All quality gates pass (ruff, mypy, pytest, coverage)
  - [ ] Compose stack starts and all health checks pass
  - [ ] Demo script runs cleanly
  - [ ] Git tag `ex3-final` created

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Everything passes before submission
    Tool: Bash
    Steps:
      1. ruff check . → 0 errors
      2. mypy src → 0 errors
      3. pytest -q → all pass, ≥80% coverage
      4. docker compose up --build -d → all healthy
      5. bash scripts/demo.sh → completes successfully
      6. docker compose down → clean
    Expected Result: Perfect clean run
    Evidence: .sisyphus/evidence/task-31-final-gate.txt
  ```

  **Commit**: YES
  - Message: `chore: pass all final quality gates and tag ex3-final`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, curl endpoint, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `ruff check .` + `mypy src` + `uv run pytest -q`. Review all changed files for: `type: ignore` abuse, empty except blocks, print statements in prod, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names (data/result/item/temp).
  Output: `Lint [PASS/FAIL] | Types [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high` (+ `playwright` skill for Streamlit)
  Start from clean state. Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test cross-task integration (API + Streamlit + AI service working together). Test edge cases: empty state, invalid input, rapid actions. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git log/diff). Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Detect cross-task contamination: Task N touching Task M's files. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

Each exercise phase gets its own commits:

**EX1:**
- `feat(models): add Cocktail, Ingredient, FlavorTag SQLModel models with M2M links` — models/, schemas/
- `feat(api): implement CRUD routes for cocktails, ingredients, and flavor tags` — api/, services/
- `feat(seed): add seed script with 20+ real cocktails` — scripts/, data/
- `test: add comprehensive test suite for all CRUD endpoints` — tests/
- `docs: add README, .http playground, and setup instructions` — README.md, examples.http

**EX2:**
- `feat(ui): add Streamlit dashboard with cocktail browser and ingredient explorer` — streamlit_app.py
- `feat(ui): add flavor wheel visualization and "What Can I Make?" filter` — streamlit_app.py
- `docs: add EX2 README with side-by-side launch instructions` — README.md

**EX3:**
- `feat(infra): add Docker Compose with Postgres, Redis, API services` — compose.yaml, Dockerfile
- `feat(auth): add JWT authentication with role-based access control` — core/security.py
- `feat(ai): add AI Mixologist microservice with Gemini integration` — ai_service/
- `feat(async): add refresh script with bounded concurrency and Redis idempotency` — scripts/refresh.py
- `feat(enhance): add "What Can I Make?" with AI-powered substitution suggestions` — api/, services/
- `docs: add EX3-notes, runbook, and demo script` — docs/, scripts/

---

## Success Criteria

### Verification Commands
```bash
# EX1
uv run pytest -q                         # Expected: all tests pass
uv run pytest --cov=app --cov-report=term # Expected: ≥80% coverage
uv run ruff check .                      # Expected: 0 errors
uv run mypy src                          # Expected: 0 errors
uv run uvicorn app.main:app --reload     # Expected: server starts, /docs accessible
curl -s localhost:8000/cocktails | jq    # Expected: JSON array of cocktails

# EX2
uv run streamlit run streamlit_app.py    # Expected: dashboard loads at localhost:8501
# (with API running on localhost:8000)

# EX3
docker compose up --build -d             # Expected: all services healthy
curl -s localhost:8000/health | jq       # Expected: {"status": "ok"}
curl -s -H "Authorization: Bearer <token>" localhost:8000/cocktails | jq  # Expected: authed response
curl -s localhost:8001/mix -d '{"ingredients": ["vodka", "lime"]}' | jq   # Expected: AI suggestion
docker compose down                      # Expected: clean teardown
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass with ≥80% coverage
- [ ] All three exercises submitted on time
- [ ] Each exercise README is clear and complete
- [ ] Seed data uses real cocktail recipes (not Lorem Ipsum)
- [ ] Streamlit dashboard looks polished (not default styling)
- [ ] AI Mixologist returns structured, believable cocktail suggestions
- [ ] Demo script runs end-to-end without manual steps
