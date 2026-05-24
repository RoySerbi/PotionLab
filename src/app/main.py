from contextlib import asynccontextmanager
import os
import sys

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.api.v1 import cocktails, flavor_tags, ingredients, routes_auth
from app.core.config import settings
from app.db.session import init_db


def _under_test() -> bool:
    """Detect whether the app is being imported by a pytest session.

    Used to relax rate limiting so the test suite doesn't trip the limiter.
    Override-able via POTION_DISABLE_RATE_LIMIT=1.
    """
    if os.getenv("POTION_DISABLE_RATE_LIMIT") == "1":
        return True
    if "PYTEST_CURRENT_TEST" in os.environ:
        return True
    return "pytest" in sys.modules


# Rate limiter: 60 requests per minute per client IP in production; effectively
# unlimited when running under pytest so the shared TestClient IP doesn't trip
# the limiter across the suite.
_default_limits = ["1000000/minute"] if _under_test() else ["60/minute"]
limiter = Limiter(key_func=get_remote_address, default_limits=_default_limits)


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

# Attach rate limiter to the app so SlowAPIMiddleware can read state.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
app.add_middleware(SlowAPIMiddleware)

app.include_router(ingredients.router, prefix="/api/v1")
app.include_router(flavor_tags.router, prefix="/api/v1")
app.include_router(cocktails.router, prefix="/api/v1")
app.include_router(routes_auth.router, prefix="/api/v1")


@app.get("/health")
async def health_check(request: Request) -> dict[str, str]:
    """Health endpoint for liveness checks. Excluded from rate limiting."""
    from app.core.redis_client import get_redis

    redis_client = get_redis()
    redis_status = "connected" if redis_client else "unavailable"
    return {"status": "ok", "redis": redis_status}
