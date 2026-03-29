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
