# PotionLab — Cocktail Recipe Engine & Flavor Chemistry Workbench

PotionLab is a specialized backend service for mixologists and flavor scientists. It manages cocktail recipes, ingredients, and complex flavor profiles, allowing for sophisticated beverage management and flavor chemistry analysis.

## Prerequisites

- Python 3.12+
- `uv` (modern Python package manager)

## Setup

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   mkdir -p data
   ```

## Running the Application

### Start the API Server
Run the FastAPI application with Uvicorn:
```bash
uv run uvicorn app.main:app --reload --app-dir src
```
The API will be available at `http://localhost:8000`.

### Seed the Database
Populate the database with a curated selection of 22 cocktails and their ingredients:
```bash
uv run python scripts/seed.py
```

## API Endpoints

The API is versioned under `/api/v1/`.

| Method | Path | Description |
| :--- | :--- | :--- |
| **GET** | `/health` | Liveness check (returns `{"status": "ok"}`) |
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

## EX2: Streamlit Dashboard

The Streamlit dashboard provides a visual interface for the PotionLab API, enabling flavor discovery and recipe management.

### Launching the Application
To run the full stack, you'll need two terminal windows:

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

To start all services (API, AI Service, Postgres, Redis):

```bash
docker compose up --build -d
```

The services will be available at:
- **API**: `http://localhost:8000`
- **AI Mixologist**: `http://localhost:8001`
- **Streamlit Dashboard**: `http://localhost:8501` (Run via `uv run streamlit run streamlit_app.py`)

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

For detailed operational procedures, refer to the [Docker Compose Runbook](docs/runbooks/compose.md) and [EX3 Architecture Notes](docs/EX3-notes.md).

## Testing

Run the full test suite (48 tests covering CRUD operations and business logic):
```bash
uv run pytest -q
```

To check test coverage:
```bash
uv run pytest --cov=src --cov-report=term-missing
```

## REST Client Playground

An `examples.http` file is provided for use with the [VS Code REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) extension. It contains ready-to-run requests for all primary API operations.

## AI Assistance

This project was developed using AI-assisted engineering practices. 

- **Architectural Design**: AI was used to draft the initial SQLModel schema and many-to-many relationship structures.
- **Implementation**: Core service logic, FastAPI route handlers, and the Streamlit UI (including Plotly visualizations and dynamic forms) were generated and refined based on project-specific requirements.
- **AI Mixologist Microservice**: A standalone FastAPI microservice (`ai_service/`) was developed with Google Gemini integration for sophisticated cocktail recipe generation and ingredient substitutions.
- **Testing**: The comprehensive test suite was automated to ensure high coverage and edge-case handling.
- **Documentation**: This README and the API documentation were drafted with AI assistance to ensure clarity and adherence to submission guidelines.

All AI-generated code has been manually reviewed, tested, and integrated into the final PotionLab service.

