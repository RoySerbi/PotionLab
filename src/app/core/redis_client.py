from typing import cast

from redis import Redis

from app.core.config import settings


def get_redis() -> Redis | None:
    """Get Redis client. Returns None if Redis unavailable."""
    try:
        client = Redis.from_url(settings.redis_url, decode_responses=True)
        client.ping()
        return client
    except Exception:
        return None


def cache_get(key: str) -> str | None:
    """Get cached value. Returns None if Redis unavailable or key missing."""
    try:
        client = get_redis()
        if client is None:
            return None
        result = client.get(key)
        return str(result) if result is not None else None
    except Exception:
        return None


def cache_set(key: str, value: str, ttl: int = 3600) -> bool:
    """Set cached value with TTL. Returns True on success, False on failure."""
    try:
        client = get_redis()
        if client is None:
            return False
        client.setex(key, ttl, value)
        return True
    except Exception:
        return False


def cache_delete(key: str) -> bool:
    """Delete cached key. Returns True on success, False on failure."""
    try:
        client = get_redis()
        if client is None:
            return False
        client.delete(key)
        return True
    except Exception:
        return False


def is_processed(idempotency_key: str) -> bool:
    """Check if operation already processed (for async worker idempotency)."""
    try:
        client = get_redis()
        if client is None:
            return False
        result = cast(int, client.exists(f"processed:{idempotency_key}"))
        return result > 0
    except Exception:
        return False


def mark_processed(idempotency_key: str, ttl: int = 86400) -> bool:
    """Mark operation as processed. Returns True on success."""
    try:
        client = get_redis()
        if client is None:
            return False
        client.setex(f"processed:{idempotency_key}", ttl, "1")
        return True
    except Exception:
        return False
