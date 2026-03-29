from unittest.mock import MagicMock, patch

import pytest
from redis import Redis

from app.core.redis_client import (
    cache_delete,
    cache_get,
    cache_set,
    get_redis,
    is_processed,
    mark_processed,
)


@pytest.fixture
def mock_redis():
    mock = MagicMock(spec=Redis)
    mock.ping.return_value = True
    return mock


class TestGetRedis:
    def test_get_redis_success(self, mock_redis):
        with patch("app.core.redis_client.Redis.from_url", return_value=mock_redis):
            client = get_redis()
            assert client is not None
            mock_redis.ping.assert_called_once()

    def test_get_redis_connection_failure(self):
        with patch(
            "app.core.redis_client.Redis.from_url",
            side_effect=Exception("Connection refused"),
        ):
            client = get_redis()
            assert client is None

    def test_get_redis_ping_failure(self, mock_redis):
        mock_redis.ping.side_effect = Exception("Ping failed")
        with patch("app.core.redis_client.Redis.from_url", return_value=mock_redis):
            client = get_redis()
            assert client is None


class TestCacheGet:
    def test_cache_get_success(self, mock_redis):
        mock_redis.get.return_value = "test_value"
        with patch("app.core.redis_client.get_redis", return_value=mock_redis):
            result = cache_get("test_key")
            assert result == "test_value"
            mock_redis.get.assert_called_once_with("test_key")

    def test_cache_get_key_not_found(self, mock_redis):
        mock_redis.get.return_value = None
        with patch("app.core.redis_client.get_redis", return_value=mock_redis):
            result = cache_get("nonexistent_key")
            assert result is None

    def test_cache_get_redis_unavailable(self):
        with patch("app.core.redis_client.get_redis", return_value=None):
            result = cache_get("test_key")
            assert result is None

    def test_cache_get_operation_failure(self, mock_redis):
        mock_redis.get.side_effect = Exception("Operation failed")
        with patch("app.core.redis_client.get_redis", return_value=mock_redis):
            result = cache_get("test_key")
            assert result is None


class TestCacheSet:
    def test_cache_set_success(self, mock_redis):
        with patch("app.core.redis_client.get_redis", return_value=mock_redis):
            result = cache_set("test_key", "test_value", 3600)
            assert result is True
            mock_redis.setex.assert_called_once_with("test_key", 3600, "test_value")

    def test_cache_set_default_ttl(self, mock_redis):
        with patch("app.core.redis_client.get_redis", return_value=mock_redis):
            result = cache_set("test_key", "test_value")
            assert result is True
            mock_redis.setex.assert_called_once_with("test_key", 3600, "test_value")

    def test_cache_set_redis_unavailable(self):
        with patch("app.core.redis_client.get_redis", return_value=None):
            result = cache_set("test_key", "test_value")
            assert result is False

    def test_cache_set_operation_failure(self, mock_redis):
        mock_redis.setex.side_effect = Exception("Operation failed")
        with patch("app.core.redis_client.get_redis", return_value=mock_redis):
            result = cache_set("test_key", "test_value")
            assert result is False


class TestCacheDelete:
    def test_cache_delete_success(self, mock_redis):
        with patch("app.core.redis_client.get_redis", return_value=mock_redis):
            result = cache_delete("test_key")
            assert result is True
            mock_redis.delete.assert_called_once_with("test_key")

    def test_cache_delete_redis_unavailable(self):
        with patch("app.core.redis_client.get_redis", return_value=None):
            result = cache_delete("test_key")
            assert result is False

    def test_cache_delete_operation_failure(self, mock_redis):
        mock_redis.delete.side_effect = Exception("Operation failed")
        with patch("app.core.redis_client.get_redis", return_value=mock_redis):
            result = cache_delete("test_key")
            assert result is False


class TestIsProcessed:
    def test_is_processed_true(self, mock_redis):
        mock_redis.exists.return_value = 1
        with patch("app.core.redis_client.get_redis", return_value=mock_redis):
            result = is_processed("test_key")
            assert result is True
            mock_redis.exists.assert_called_once_with("processed:test_key")

    def test_is_processed_false(self, mock_redis):
        mock_redis.exists.return_value = 0
        with patch("app.core.redis_client.get_redis", return_value=mock_redis):
            result = is_processed("test_key")
            assert result is False

    def test_is_processed_redis_unavailable(self):
        with patch("app.core.redis_client.get_redis", return_value=None):
            result = is_processed("test_key")
            assert result is False

    def test_is_processed_operation_failure(self, mock_redis):
        mock_redis.exists.side_effect = Exception("Operation failed")
        with patch("app.core.redis_client.get_redis", return_value=mock_redis):
            result = is_processed("test_key")
            assert result is False


class TestMarkProcessed:
    def test_mark_processed_success(self, mock_redis):
        with patch("app.core.redis_client.get_redis", return_value=mock_redis):
            result = mark_processed("test_key", 86400)
            assert result is True
            mock_redis.setex.assert_called_once_with("processed:test_key", 86400, "1")

    def test_mark_processed_default_ttl(self, mock_redis):
        with patch("app.core.redis_client.get_redis", return_value=mock_redis):
            result = mark_processed("test_key")
            assert result is True
            mock_redis.setex.assert_called_once_with("processed:test_key", 86400, "1")

    def test_mark_processed_redis_unavailable(self):
        with patch("app.core.redis_client.get_redis", return_value=None):
            result = mark_processed("test_key")
            assert result is False

    def test_mark_processed_operation_failure(self, mock_redis):
        mock_redis.setex.side_effect = Exception("Operation failed")
        with patch("app.core.redis_client.get_redis", return_value=mock_redis):
            result = mark_processed("test_key")
            assert result is False
