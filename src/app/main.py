from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import cocktails, flavor_tags, ingredients
from app.core.config import settings
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore
    """Lifespan context manager for app startup/shutdown."""
    init_db()
    yield


app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    lifespan=lifespan,
)

app.include_router(ingredients.router, prefix="/api/v1")
app.include_router(flavor_tags.router, prefix="/api/v1")
app.include_router(cocktails.router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health endpoint for liveness checks."""
    return {"status": "ok"}
