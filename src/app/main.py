from contextlib import asynccontextmanager

from fastapi import FastAPI

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


@app.get("/health")
async def health_check():
    """Health endpoint for liveness checks."""
    return {"status": "ok"}
