# PotionLab — Learnings & Conventions

> Cumulative knowledge captured during implementation. Append findings after each task.

---

## Task 1: Project Scaffolding & Environment Setup

### Key Learnings

**1. Build System & Dependencies**
- Used `setuptools` with src layout (not hatchling) due to Python 3.14 compatibility issues with pydantic-core wheel builds
- uv sync can hang on pydantic-core compilation on newer Python versions; use relaxed version constraints to allow pre-built wheels
- pyproject.toml config:
  ```toml
  [tool.setuptools]
  packages = ["app"]
  package-dir = {"" = "src"}
  ```

**2. FastAPI Lifespan Pattern**
- Modern FastAPI (0.100+) uses `@asynccontextmanager` for lifespan, not deprecated `@app.on_event("startup")`
- Lifespan receives app instance as parameter: `async def lifespan(app: FastAPI):`
- Use `yield` to split startup/shutdown logic
- Pattern:
  ```python
  @asynccontextmanager
  async def lifespan(app: FastAPI):
      init_db()  # Startup
      yield
      # Shutdown code here (if needed)
  app = FastAPI(..., lifespan=lifespan)
  ```

**3. Test Fixtures with StaticPool**
- CRITICAL: Use `StaticPool` from `sqlalchemy.pool` in test fixtures, not the default `NullPool`
- Without StaticPool, each test connection creates a separate in-memory SQLite DB → state leakage between tests
- Correct fixture pattern:
  ```python
  from sqlalchemy.pool import StaticPool
  engine = create_engine(
      "sqlite://",
      connect_args={"check_same_thread": False},
      poolclass=StaticPool,
  )
  ```

**4. Test Client Setup**
- Use `TestClient` from `fastapi.testclient` for sync tests (not httpx.AsyncClient directly)
- TestClient is NOT async-compatible; use sync functions in tests
- Override dependencies via `app.dependency_overrides`:
  ```python
  def get_session_override():
      return session
  app.dependency_overrides[get_session] = get_session_override
  yield TestClient(app)
  app.dependency_overrides.clear()
  ```

**5. Directory Structure**
- Course expects `src/app/` layout with separate packages for api, models, schemas, services, db, core
- All packages need `__init__.py` (even if empty)
- Tests mirror source structure: `tests/api/`, `tests/services/`

**6. Code Quality**
- Ruff linting: prefer `collections.abc.Generator` over `typing.Generator` (UP035)
- Remove unused imports before commit
- All linting checks must pass (`uv run ruff check src tests`)

### QA Results

✓ **Scenario 1: Health endpoint**
- Server starts cleanly with lifespan context manager
- GET /health returns 200 + `{"status":"ok"}`
- Evidence: `.sisyphus/evidence/task-1-health-endpoint.json`

✓ **Scenario 2: pytest baseline**
- 1 test passes with 100% success rate
- Exit code 0, no warnings
- Evidence: `.sisyphus/evidence/task-1-pytest-baseline.txt`

### Blocking Issues Encountered & Resolved

**Issue**: Python 3.14 pydantic-core wheel build timeout
- **Root Cause**: uv tries to build pydantic-core from source on Python 3.14; no pre-built wheels available
- **Solution**: Use relaxed version constraints `pydantic>=2.0` instead of pinned `pydantic==2.10.4` to allow pre-built wheels

**Issue**: AsyncClient from httpx doesn't accept `app=` parameter
- **Root Cause**: httpx.AsyncClient is a low-level HTTP client; use TestClient from fastapi.testclient instead
- **Solution**: Switched to `from fastapi.testclient import TestClient` which wraps ASGI directly

**Issue**: Fixture dependency injection for client failed (`fixture 'session_fixture' not found`)
- **Root Cause**: Pytest fixture name in parameter didn't match declared fixture name
- **Solution**: Use consistent naming: `@pytest.fixture(name="session")` with parameter `session: Session`

### Conventions Established

1. **Config Loading**: Use Pydantic `BaseSettings` with `SettingsConfigDict(env_prefix="POTION_")`
2. **Imports**: Use `collections.abc` for generic types (Generator, etc.) on Python 3.10+
3. **Health Endpoint**: Always include minimal GET /health → {"status": "ok"} for service viability checks
4. **Database Session**: Dependency injection via `Depends(get_session)` pattern; tests override with fixture
5. **Commit Pattern**: Include `pyproject.toml`, `uv.lock`, `src/`, `tests/` in initial scaffold commit

### Next Task Blockers

Task 2 (SQLModel Models) needs:
- Working uv environment ✓
- FastAPI app with lifespan ✓
- Test fixtures with StaticPool ✓
- Config/session layer ✓
- All unblocked to proceed

---

## Task 4: Database Session, Lifespan, and Config Setup

### Key Learnings

**1. Settings Pattern with Pydantic**
- Use `pydantic_settings.BaseSettings` with `SettingsConfigDict(env_prefix="POTION_")`
- All environment variables should be prefixed with `POTION_` (e.g., `POTION_DATABASE_URL`, `POTION_APP_TITLE`)
- Settings object created at module level for global access: `settings = Settings()`
- Validated and type-checked at initialization time

**2. Database Session Module Pattern**
- Implement `get_db_url()` that respects `SQLMODEL_DATABASE` env var for test isolation
- Use single module-level `engine` initialized with proper connection args
- For SQLite: `connect_args={"check_same_thread": False}` allows concurrent test access
- `init_db()` creates all tables: `SQLModel.metadata.create_all(engine)`
- `get_session()` returns a generator dependency for FastAPI injection

**3. FastAPI Lifespan (Modern Pattern)**
- Use `@asynccontextmanager` from contextlib for lifespan management
- Replaces deprecated `@app.on_event("startup")`
- Call `init_db()` during startup phase (before `yield`)
- Lifespan passed to FastAPI constructor: `FastAPI(..., lifespan=lifespan)`

**4. Test Fixtures with StaticPool**
- CRITICAL: Conftest must use `StaticPool` for in-memory databases
- `poolclass=StaticPool` ensures all tests share ONE in-memory SQLite instance
- Without StaticPool, each connection creates a new database (data isolation breaks)
- Test client created fresh per test, but session reused if poolclass=StaticPool

**5. Environment Variable Precedence**
- `SQLMODEL_DATABASE` overrides `settings.database_url` for test runs
- Main app uses `POTION_*` prefix for all settings
- Tests typically set `SQLMODEL_DATABASE` via pytest fixtures or monkeypatch

### QA Results

✓ **Scenario 1: Lifespan startup**
- App initializes with lifespan context manager
- `init_db()` called automatically on startup
- Database file created at configured path
- Health endpoint returns 200 + `{"status":"ok"}`
- Evidence: `.sisyphus/evidence/task-4-lifespan-startup.txt`

✓ **Scenario 2: Test isolation with StaticPool**
- Tests run with in-memory SQLite (StaticPool)
- Session persists across test functions
- No warnings or state leakage
- Exit code 0
- Evidence: `.sisyphus/evidence/task-4-test-isolation.txt`

✓ **Scenario 3: Environment variable loading**
- `POTION_DATABASE_URL` successfully overrides default
- `POTION_APP_TITLE` and `POTION_APP_VERSION` load from env
- Settings validated at initialization

✓ **Scenario 4: SQLMODEL_DATABASE override**
- `SQLMODEL_DATABASE` env var overrides `settings.database_url`
- Allows pointing tests to specific database path or in-memory instance

### Patterns Established

1. **Config Module**: Single `settings` object imported throughout app
2. **Session Module**: Dependency injection via `Depends(get_session)`, overrideable in tests
3. **Main Module**: Lifespan calls `init_db()`, FastAPI uses settings for title/version
4. **Test Module**: Conftest with StaticPool and dependency override fixture

### Next Task Dependencies

Task 5 (CRUD endpoints) depends on:
- Config settings ✓
- Session management ✓
- Lifespan/init_db ✓
- All infrastructure ready

---

## Task 3: Pydantic Schemas for All Resources

### Key Learnings

**1. Schema Organization Pattern**
- Create separate flat and nested schemas to prevent lazy-loading issues outside session scope
- Flat Read schemas (no relationships): used for list endpoints
- Nested ReadWith/ReadFull schemas: used for detail endpoints only
- This pattern avoids SQLAlchemy lazy-load errors when serializing to JSON outside the session context

**2. Validation Constraints with Field()**
- Use `Field(min_length=1, max_length=80)` for string validation
- Use `Field(ge=1, le=5)` for numeric range validation (inclusive bounds)
- Empty strings rejected automatically by min_length=1
- Constraints are enforced BEFORE instantiation - ValidationError raised immediately

**3. Schema Configuration**
- All Read schemas must have `model_config = ConfigDict(from_attributes=True)`
- This enables conversion from SQLModel ORM instances: `IngredientRead.model_validate(orm_instance)`
- Critical for response serialization in route handlers

**4. Python 3.12+ Type Syntax**
- Use `str | None` instead of `Optional[str]`
- Use `list[str]` instead of `List[str]`
- Use `dict[str, object]` instead of bare `dict` (mypy type-arg requirement)
- Requires `from __future__ import annotations` at top of file

**5. Barrel File Pattern**
- Import all schemas in `__init__.py` with explicit `__all__` list
- Enables clean imports: `from app.schemas import FlavorTagCreate, CocktailRead`
- Better than accessing via `app.schemas.flavor_tag.FlavorTagCreate`

**6. Nested Schema References**
- Child schemas (e.g., CocktailReadFull) can reference parent schemas
- Example: `CocktailReadFull` inherits from `CocktailRead`, adds `instructions` and `ingredients`
- Import dependencies carefully: ingredient.py doesn't import cocktail.py, only vice versa (no circular imports)

### QA Results

✓ **Scenario 1: Invalid input rejected**
- CocktailCreate(name='', difficulty=6, ...) raises ValidationError with 2 errors
- Empty name flagged (string_too_short)
- Difficulty 6 flagged (less_than_equal constraint)
- Evidence: `.sisyphus/evidence/task-3-schema-validation.txt`

✓ **Scenario 2: Valid input accepted**
- CocktailCreate with valid name, difficulty=2, ingredients list creates successfully
- Serializes to valid JSON with all fields
- Evidence: `.sisyphus/evidence/task-3-schema-valid.txt`

✓ **Scenario 3: All schemas importable**
- `from app.schemas import FlavorTagCreate, FlavorTagRead, IngredientCreate, ...` succeeds
- Barrel file properly re-exports all schemas
- No circular import errors

### Code Quality

✓ ruff check: All checks passed
✓ mypy: Success - no issues in 4 source files
- Fixed: Removed unused IngredientRead import from cocktail.py
- Fixed: Changed `list[dict]` to `list[dict[str, object]]` for type completeness

### Key Files

- `src/app/schemas/flavor_tag.py`: FlavorTagCreate, FlavorTagRead
- `src/app/schemas/ingredient.py`: IngredientCreate, IngredientRead, IngredientReadWithTags
- `src/app/schemas/cocktail.py`: CocktailIngredientCreate, CocktailCreate, CocktailRead, CocktailReadFull
- `src/app/schemas/__init__.py`: Barrel file with __all__ list

### Next Task Blockers

Tasks 5, 6, 7 (routes + services) need:
- Schemas defined and importable ✓
- Models from Task 2 ✓
- Database session from Task 4 (pending)
- All unblocked to proceed once Task 4 complete

---

## Task 2: SQLModel Models — Many-to-Many with Composite Primary Keys

### Key Learnings

**1. Many-to-Many Link Tables with Composite PK**
- Use `__table_args__ = (PrimaryKeyConstraint("col1", "col2"),)` for composite primary keys
- Link tables prevent duplicate relationships automatically via composite PK constraint
- SQLAlchemy raises `IntegrityError` when attempting to insert duplicate composite key
- Pattern for link table:
  ```python
  from sqlalchemy import PrimaryKeyConstraint
  
  class CocktailIngredient(SQLModel, table=True):
      __tablename__ = "cocktailingredient"
      __table_args__ = (PrimaryKeyConstraint("cocktail_id", "ingredient_id"),)
      
      cocktail_id: int = Field(sa_column=Column(Integer, ForeignKey("cocktail.id"), nullable=False))
      ingredient_id: int = Field(sa_column=Column(Integer, ForeignKey("ingredient.id"), nullable=False))
      amount: str = Field(sa_column=Column(String(50), nullable=False))
      is_optional: bool = Field(default=False, sa_column=Column(Boolean, nullable=False))
  ```

**2. Model Registration for SQLModel.metadata**
- SQLModel needs to see model classes before `SQLModel.metadata.create_all()`
- Import all models in `session.py` (or wherever `init_db()` is called) to register them
- Use `# noqa: F401` comment to suppress "unused import" linting errors for model imports
- Pattern:
  ```python
  from app.models import (  # noqa: F401
      Cocktail,
      CocktailIngredient,
      FlavorTag,
      Ingredient,
      IngredientFlavorTag,
  )
  
  def init_db() -> None:
      SQLModel.metadata.create_all(engine)
  ```

**3. Field Constraints with sa_column**
- Continue using `Field(sa_column=Column(...))` pattern from Task 1
- Supports unique constraints: `sa_column=Column(String(80), unique=True, nullable=False, index=True)`
- Supports foreign keys: `sa_column=Column(Integer, ForeignKey("cocktail.id"), nullable=False)`
- Supports range validation: `Field(..., ge=1, le=5)` for difficulty ratings

**4. Table Naming**
- SQLModel auto-lowercases class names for table names (FlavorTag → flavortag)
- Override with `__tablename__` if needed: `__tablename__ = "cocktailingredient"`
- Link tables don't need synthetic `id` fields — composite PK is sufficient

**5. Testing Composite PK Constraints**
- Use `pytest.raises(IntegrityError)` to verify duplicate prevention
- Pattern:
  ```python
  link1 = CocktailIngredient(cocktail_id=1, ingredient_id=1, amount="2 oz")
  session.add(link1)
  session.commit()
  
  link2 = CocktailIngredient(cocktail_id=1, ingredient_id=1, amount="3 oz")
  session.add(link2)
  with pytest.raises(IntegrityError):
      session.commit()
  ```

### QA Results

✓ **Scenario 1: Models create tables**
- All 5 tables created: cocktail, ingredient, flavortag, cocktailingredient, ingredientflavortag
- `init_db()` completes without errors
- Evidence: `.sisyphus/evidence/task-2-model-tables.txt`

✓ **Scenario 2: Composite PK constraint**
- Duplicate link raises `IntegrityError`
- Test passes with 100% success rate
- Evidence: `.sisyphus/evidence/task-2-composite-pk-constraint.txt`

### Model Architecture

**Main Entities:**
- `FlavorTag`: id, name (unique), category
- `Ingredient`: id, name (unique), category, description (optional)
- `Cocktail`: id, name (unique), description (opt), instructions, glass_type, difficulty (1-5)

**Link Tables:**
- `CocktailIngredient`: (cocktail_id, ingredient_id) composite PK + amount + is_optional
- `IngredientFlavorTag`: (ingredient_id, flavor_tag_id) composite PK

### Conventions Established

1. **Composite PK Pattern**: Use `__table_args__` with `PrimaryKeyConstraint` tuple
2. **Model Registration**: Import all models in session.py with `# noqa: F401`
3. **Link Table Naming**: Use lowercase concatenated names (cocktailingredient, ingredientflavortag)
4. **No Synthetic IDs**: Link tables rely on composite PK only
5. **Foreign Key Constraints**: Always specify `ForeignKey("table.column")` in link tables

### Next Task Dependencies

Task 3 (Pydantic Schemas) needs:
- Working SQLModel models ✓
- All 5 tables creatable ✓
- Composite PK constraints enforced ✓
- Barrel file exporting models ✓
- All unblocked to proceed

---

## Task 7: Cocktail CRUD + Nested Ingredient Management

### Key Learnings

- Nested cocktail create/update is safest with a single transaction: validate ingredient IDs first, `flush()` to get cocktail ID, add link rows, then commit once.
- Atomic replacement pattern for updates works cleanly for link tables: fetch existing `CocktailIngredient` rows, delete them, add new rows from payload, commit.
- Flat list/detail split avoids lazy-loading/session issues:
  - `GET /cocktails` returns `CocktailRead` only.
  - `GET /cocktails/{id}` builds `CocktailReadFull` by composing cocktail + explicit ingredient/link queries.
- Ingredient existence validation is best done as a set-based query (`IN` lookup) to avoid N+1 DB round-trips and to return all missing IDs in one 400 error.
- For nested detail responses, constructing the nested payload in the route layer avoids mutating SQLModel instances with undeclared dynamic fields.

### QA Results

- `uv run ruff check src` passes.
- `uv run pytest -q` passes with cocktail nested create test included.
- Manual curl flow verified: create/list/detail/update/delete, 404 for missing cocktail, and 400 for invalid ingredient ID.
- Evidence:
  - `.sisyphus/evidence/task-7-cocktail-crud.txt`
  - `.sisyphus/evidence/task-7-nested-structure.json`
  - `.sisyphus/evidence/task-7-pytest.txt`

## Task 5: Ingredient CRUD Routes + Service Layer

### Service Layer Pattern
- Service functions accept `session: Session` as first parameter
- Service functions return SQLModel instances (not Pydantic)
- Routes convert service results to Pydantic schemas via `.model_validate()`
- Clear separation: service = business logic, routes = HTTP concerns

### Route Registration
- Router created with `APIRouter(tags=["ingredients"])`
- Mounted in main.py: `app.include_router(ingredients.router, prefix="/api/v1")`
- All routes automatically prefixed with `/api/v1`

### Schema Selection Pattern
- **List endpoints** (`GET /ingredients`): Use flat `IngredientRead` schema (no relationships)
- **Detail endpoints** (`GET /ingredients/{id}`): Use nested `IngredientReadWithTags` schema (includes flavor_tags)
- Prevents SQLAlchemy lazy-load errors outside session scope

### HTTP Status Codes
- POST (create): 201 Created
- GET (read): 200 OK
- PUT (update): 200 OK
- DELETE: 204 No Content
- Not found: 404 with HTTPException

### Dependency Injection
- `session: Session = Depends(get_session)` in all route handlers
- FastAPI automatically provides session from dependency
- Session lifecycle managed by generator (auto-cleanup)

### Error Handling
- Service returns `None` for not found (read_by_id, update, delete)
- Route raises `HTTPException(status_code=404, detail="...")` when None
- Consistent error message format: "Ingredient with id {id} not found"

### Testing Insights
- 10 test functions covering all CRUD + error cases
- Tests use conftest.py fixtures (session, client with dependency override)
- All 20 tests pass (including existing model tests)
- Manual curl verification confirms nested schema behavior

### What Worked Well
- Clean separation between service and route layers
- Pydantic `.model_validate()` seamlessly converts SQLModel to schema
- FastAPI OpenAPI docs auto-generated from route signatures
- Dependency injection eliminates boilerplate session management

---

## Task 8: Seed Script with 20+ Real Cocktails

### Key Learnings

**1. Idempotency Pattern with IntegrityError**
- Seed scripts must be safe to run multiple times without creating duplicates
- Use `try/except IntegrityError` pattern with unique constraints (NOT manual checks)
- Commit immediately after each INSERT to trigger constraint validation early
- Pattern:
  ```python
  from sqlalchemy.exc import IntegrityError
  
  try:
      obj = Model(**data)
      session.add(obj)
      session.commit()
      created += 1
  except IntegrityError:
      session.rollback()  # Skip existing record
  ```
- Running seed script twice: first run creates 12 tags, 39 ingredients, 22 cocktails; second run creates 0 of each (fully idempotent)

**2. Data Creation Order (Respect Foreign Key Dependencies)**
- Create entities in strict order:
  1. FlavorTag (no dependencies)
  2. Ingredient (no dependencies)
  3. IngredientFlavorTag links (depends on FlavorTag + Ingredient)
  4. Cocktail (no dependencies)
  5. CocktailIngredient links (depends on Cocktail + Ingredient)
- Creating links before entities they reference causes foreign key violations
- Must call `session.refresh(obj)` after commit to get auto-generated IDs for linking

**3. Querying by Name for Link Tables**
- Link tables need entity IDs, not names
- Cannot hardcode IDs (they're auto-generated during seed)
- Query strategy: `session.exec(select(Ingredient).where(Ingredient.name == "Gin")).first()`
- Only add link if entity exists (check for None)
- Pattern:
  ```python
  ingredient = session.exec(select(Ingredient).where(Ingredient.name == "Gin")).first()
  if ingredient:
      link = CocktailIngredient(
          cocktail_id=cocktail.id,
          ingredient_id=ingredient.id,
          amount="2 oz",
          is_optional=False
      )
      session.add(link)
      session.commit()
  ```

**4. Real Cocktail Data & Recipes**
- Use accurate IBA standards and classic recipes (not placeholder data)
- Essential cocktails: Negroni, Old Fashioned, Martini, Daiquiri, Margarita, Mojito, Manhattan, Cosmopolitan, Sazerac
- Modern classics: Espresso Martini, Penicillin, Aperol Spritz, Moscow Mule, Dark & Stormy
- IBA official: Mai Tai, Clover Club, Aviation, Last Word, Boulevardier, Sidecar, Pisco Sour
- Each cocktail includes: name, description, instructions (full recipe), glass type, difficulty (1-5)
- Ingredient amounts in standard units (oz/ml): e.g., "2 oz", "0.75 oz", "12 leaves", "1 sprig"
- 22 cocktails ≥ 20 target, covering difficulty range 1-4 and diverse glass types

**5. Flavor Tag Association Strategy**
- Ingredients tagged with 1-3 flavor tags based on taste profile
- Examples:
  - Gin: Citrus, Herbal, Floral
  - Bourbon: Sweet, Smoky, Spicy
  - Rum Light: Fruity, Fresh
  - Lime Juice: Citrus, Fresh
  - Mint: Minty, Fresh
- 12 total tags across categories: Fresh, Aromatic, Complex, Bold
- Enables future recipe filtering by flavor profile (e.g., "show me citrus-forward cocktails")

**6. Ingredient Categorization**
- Spirit (gin, vodka, rum, bourbon, whiskey, tequila, mezcal, brandy, cognac, scotch)
- Fortified/Liqueur (vermouth, Campari, Cointreau, Kahlua, Chartreuse, Fernet-Branca)
- Juice (lime, lemon, orange, cranberry)
- Mixer (ginger beer, tonic, soda water, cola, simple syrup, espresso)
- Garnish (mint, lime wheel, lemon twist, orange peel, olive, cherry)
- Spice (bitters, sugar)
- 39 total ingredients ≥ 30 target

**7. Script Structure & Output**
- Use `get_db_url()` to respect `SQLMODEL_DATABASE` env var for test isolation
- Call `create_engine(get_db_url())` directly (not session.engine from app)
- Print progress messages: "Created X flavor tags", "Created Y ingredients", "Created Z cocktails"
- Use emoji for visual appeal: 🍹 🥃 ✓ ✨
- Executable via: `uv run python scripts/seed.py`
- Entry point: `if __name__ == "__main__": main()`

### QA Results

✓ **Scenario 1: First run (Database seeding)**
- Script creates 12 flavor tags
- Script creates 39 ingredients with flavor associations
- Script creates 22 cocktails with full recipes
- Exit code 0, no errors
- Evidence: `.sisyphus/evidence/task-8-seed-run.txt`

✓ **Scenario 2: Idempotency (Second run)**
- Same script run twice
- Second run creates 0 of each entity (all already exist)
- Exit code 0, no errors, no duplicates
- No warnings from IntegrityError backoff

✓ **Scenario 3: Data counts verification**
- 22 Cocktails in database (≥20 required)
- 39 Ingredients in database (≥30 required)
- 12 Flavor Tags in database (≥10 required)
- All entities correctly linked via foreign keys

✓ **Scenario 4: Sample cocktail verification**
- Negroni: 3 ingredients (Gin 1 oz, Campari 1 oz, Sweet Vermouth 1 oz, Orange Peel)
- Difficulty 1 (easy), Rocks glass
- Accurate instructions present
- Espresso Martini: 4 ingredients (Vodka 1.5 oz, Kahlua 1 oz, Simple Syrup 0.5 oz, Espresso 1 oz)
- Difficulty 3 (challenging), Coupe glass
- Evidence: `.sisyphus/evidence/task-8-data-verification.txt`

✓ **Scenario 5: Flavor tag associations**
- Gin tagged with: Citrus (Fresh), Herbal (Aromatic), Floral (Aromatic)
- Links correctly stored in IngredientFlavorTag table
- Queryable and usable for flavor-based filtering

### Files Created

- `scripts/__init__.py`: Package marker
- `scripts/seed.py`: 475 lines, 22 cocktails, 39 ingredients, 12 flavor tags

### Patterns Established

1. **Seed Pattern**: Idempotent with IntegrityError handling, creation order, transaction management
2. **Data Organization**: Category-based ingredient grouping, flavor tag associations, cocktail metadata
3. **Real-World Data**: Accurate IBA cocktails with proper measurements and instructions
4. **Environment Respect**: Uses get_db_url() for test isolation, respects SQLMODEL_DATABASE env var

### Next Task Blockers

Tasks 9+ (API routes, Streamlit UI, etc.) can now:
- Query pre-populated cocktails ✓
- Filter by flavor tags ✓
- Demonstrate real data in endpoints ✓
- Show real recipes and ingredients ✓
- All data infrastructure complete


## Task 6: FlavorTag CRUD Implementation

### Service Layer Pattern
- Service functions accept `session: Session` parameter
- Service functions return SQLModel instances (not Pydantic schemas)
- Routes handle conversion from SQLModel → Pydantic schemas using `.model_validate()`
- CRUD operations use:
  - `session.get(Model, id)` for single lookups
  - `session.exec(select(Model))` for list queries
  - Standard commit/refresh cycle for persistence

### Unique Constraint Error Handling
- FlavorTag.name has unique constraint at DB level
- Catch `IntegrityError` from sqlalchemy.exc in route handlers
- Wrap service calls in try/except blocks for POST and PUT
- Call `session.rollback()` before raising HTTPException
- Return 409 Conflict status with descriptive message:
  ```python
  except IntegrityError:
      session.rollback()
      raise HTTPException(
          status_code=status.HTTP_409_CONFLICT,
          detail=f"FlavorTag with name '{flavor_tag_in.name}' already exists",
      )
  ```

### HTTP Status Code Conventions
- POST create → 201 Created + response body
- GET list/single → 200 OK + response body
- PUT update → 200 OK + response body
- DELETE → 204 No Content (empty response)
- Not found → 404 Not Found
- Unique constraint violation → 409 Conflict

### Testing Strategy
- Unit tests cover all CRUD operations (create, list, get, update, delete)
- Test error paths: 404 for missing resources, 409 for duplicates
- Use TestClient fixture with dependency override for isolated DB
- Manual curl tests verify end-to-end behavior with actual HTTP calls

### Differences from Ingredient Routes
- FlavorTag simpler: no nested relationships or flavor_tag_ids field
- No separate ReadWithTags schema needed
- Single FlavorTagRead schema serves both list and detail endpoints
- Update endpoint still needs IntegrityError handling (name uniqueness)

## Task 9: Comprehensive Test Suite Expansion (96% Coverage Achieved)

### Test Coverage Strategy
- **Total Tests**: 48 (exceeded ≥30 target)
- **Coverage**: 96% (exceeded ≥80% target)
- **Breakdown**:
  - API endpoints: 13 tests for cocktails (CRUD + error paths)
  - Service layer: 13 tests for business logic validation
  - Existing: 22 tests for ingredients, flavor-tags, health, models

### Test Patterns Used

#### 1. Error Path Testing (Critical for Business Logic)
```python
def test_create_cocktail_with_invalid_ingredient_id(client: TestClient):
    """Test POST returns 400 for invalid ingredient_id."""
    payload = {
        "name": "Bad Cocktail",
        "ingredients": [{"ingredient_id": 9999, "amount": "1 oz", "is_optional": False}]
    }
    response = client.post("/api/v1/cocktails", json=payload)
    assert response.status_code == 400
    assert "not found" in response.json()["detail"].lower()
```

#### 2. Parametrized Tests (Boundary Conditions)
```python
@pytest.mark.parametrize("difficulty", [0, 6, -1])
def test_create_cocktail_invalid_difficulty(client: TestClient, difficulty: int):
    """Test POST returns 422 for invalid difficulty values."""
    # Validates Pydantic schema constraints (difficulty: 1-5)
```

#### 3. Service Layer Unit Tests (Business Logic Without HTTP)
```python
def test_create_cocktail_validates_ingredient_ids(session: Session):
    """Test create_cocktail raises ValueError for invalid ingredient_id."""
    cocktail_in = CocktailCreate(
        name="Bad Cocktail",
        ingredients=[CocktailIngredientCreate(ingredient_id=9999, amount="1 oz")]
    )
    with pytest.raises(ValueError, match="Ingredient id.*not found"):
        create_cocktail(session, cocktail_in)
```

### Coverage Insights

**High Coverage Areas (100%)**:
- `app/api/v1/ingredients.py`: All CRUD operations tested
- `app/api/v1/flavor_tags.py`: All CRUD operations tested
- `app/services/ingredient.py`: All service functions tested
- `app/services/flavor_tag.py`: All service functions tested
- All models and schemas: 100%

**Good Coverage Areas (89-93%)**:
- `app/api/v1/cocktails.py`: 89% (uncovered: IntegrityError edge cases, 500 error path)
- `app/services/cocktail.py`: 93% (uncovered: empty ingredient list validation, RuntimeError path)
- `app/main.py`: 88% (uncovered: uvicorn startup lines)

**Acceptable Coverage Areas (77%)**:
- `app/db/session.py`: 77% (uncovered: lifespan context manager, startup/shutdown hooks)

### Key Learnings

1. **Service Layer Testing is Essential**:
   - Tests business logic independently of HTTP layer
   - Validates ValueError exceptions for invalid ingredient_ids
   - Ensures atomic updates (delete old ingredients, add new ones)
   - Easier to test edge cases without HTTP overhead

2. **Error Testing Matters**:
   - 404: Resource not found (GET/PUT/DELETE with invalid ID)
   - 400: Business logic errors (invalid ingredient_id in cocktail)
   - 422: Validation errors (Pydantic schema failures like difficulty out of range)
   - IntegrityError: Database constraint violations (duplicate names)

3. **Parametrize Reduces Duplication**:
   - Single test function validates multiple boundary values
   - Example: `@pytest.mark.parametrize("difficulty", [0, 6, -1])` tests all invalid difficulty values

4. **Fixtures Enable Isolation**:
   - `session` fixture: Fresh in-memory SQLite database per test
   - `client` fixture: TestClient with overridden dependencies
   - No shared state between tests = reliable, repeatable results

5. **Coverage Gaps Are Acceptable**:
   - Lifespan hooks (startup/shutdown) not easily testable without integration tests
   - RuntimeError paths in services (defensive programming, unlikely to trigger)
   - IntegrityError in API layer (already tested at service layer)

### Test Organization

```
tests/
├── api/
│   ├── test_health.py          # 1 test
│   ├── test_ingredients.py     # 10 tests (CRUD + 404/409)
│   ├── test_flavor_tags.py     # 10 tests (CRUD + 404/409)
│   └── test_cocktails.py       # 13 tests (CRUD + 400/404/422, parametrized)
├── services/
│   └── test_cocktail_service.py  # 13 tests (business logic validation)
└── test_models.py              # 1 test (composite PK)
```

### Commands Used

```bash
# Run all tests
uv run pytest -q --tb=short
# Output: 48 passed, 1 warning

# Run with coverage
uv run coverage run -m pytest -q
uv run coverage report -m
# Output: 96% coverage (405 statements, 16 missed)

# Count tests
uv run pytest --collect-only -q | grep -E "test_" | wc -l
# Output: 48 tests
```

### Evidence Files Created

- `.sisyphus/evidence/task-9-pytest-results.txt`: Full pytest output
- `.sisyphus/evidence/task-9-coverage-report.txt`: Coverage report with line numbers
- `.sisyphus/evidence/task-9-test-count.txt`: Total test count

### Next Steps (For Future Tasks)

- Consider adding integration tests for lifespan hooks if needed
- Monitor coverage trends as new features are added
- Refactor tests if duplication emerges (extract helper functions)
- Add performance tests if API latency becomes a concern
