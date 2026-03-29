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
- **Implementation**: Core service logic and FastAPI route handlers were generated and refined based on project-specific requirements.
- **Testing**: The comprehensive test suite was automated to ensure high coverage and edge-case handling.
- **Documentation**: This README and the API documentation were drafted with AI assistance to ensure clarity and adherence to submission guidelines.

All AI-generated code has been manually reviewed, tested, and integrated into the final PotionLab service.

