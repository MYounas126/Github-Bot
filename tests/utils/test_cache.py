import json
import os
import time
from pathlib import Path

import pytest

from codeguardian.utils.cache import Cache, cached, default_cache


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Create a temporary cache directory for testing."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir


@pytest.fixture
def cache(temp_cache_dir):
    """Create a Cache instance with a temporary directory."""
    return Cache(cache_dir=str(temp_cache_dir), ttl=60)


def test_cache_set_get(cache):
    """Test basic cache set and get operations."""
    # Test setting and getting a value
    cache.set("test_key", {"data": "test_value"})
    result = cache.get("test_key")
    assert result == {"data": "test_value"}


def test_cache_expiry(cache):
    """Test cache expiration behavior."""
    # Set a value with short TTL
    cache.ttl = 1
    cache.set("expiry_test", {"data": "will_expire"})

    # Value should be available immediately
    assert cache.get("expiry_test") == {"data": "will_expire"}

    # Wait for expiration
    time.sleep(1.1)

    # Value should be expired
    assert cache.get("expiry_test") is None


def test_cache_miss(cache):
    """Test cache miss behavior."""
    # Try to get non-existent key
    assert cache.get("non_existent") is None


def test_cache_corrupted_file(cache, temp_cache_dir):
    """Test handling of corrupted cache files."""
    # Create a corrupted cache file
    cache_file = temp_cache_dir / "corrupted.json"
    with open(cache_file, "w") as f:
        f.write("invalid json content")

    # Should handle corrupted file gracefully
    assert cache.get("corrupted") is None


def test_cache_missing_file(cache):
    """Test handling of missing cache files."""
    # Should handle missing file gracefully
    assert cache.get("missing") is None


def test_cache_decorator(cache):
    """Test the @cached decorator functionality."""
    call_count = 0

    @cached(cache)
    def test_function(arg1, arg2):
        nonlocal call_count
        call_count += 1
        return {"result": arg1 + arg2}

    # First call should execute function
    result1 = test_function(1, 2)
    assert result1 == {"result": 3}
    assert call_count == 1

    # Second call with same args should use cache
    result2 = test_function(1, 2)
    assert result2 == {"result": 3}
    assert call_count == 1

    # Different args should execute function again
    result3 = test_function(2, 3)
    assert result3 == {"result": 5}
    assert call_count == 2


def test_cache_cleanup(cache, temp_cache_dir):
    """Test cache cleanup functionality."""
    # Set some test values
    cache.set("key1", {"data": "value1"})
    cache.set("key2", {"data": "value2"})

    # Create an expired cache file
    expired_file = temp_cache_dir / "expired.json"
    with open(expired_file, "w") as f:
        json.dump({"data": "expired", "expires_at": time.time() - 1000}, f)

    # Run cleanup
    cache.cleanup()

    # Check that expired file was removed
    assert not expired_file.exists()

    # Check that valid cache files remain
    assert cache.get("key1") == {"data": "value1"}
    assert cache.get("key2") == {"data": "value2"}


def test_cache_max_size(cache, temp_cache_dir):
    """Test cache size limiting functionality."""
    cache.max_size = 2

    # Set three values
    cache.set("key1", {"data": "value1"})
    cache.set("key2", {"data": "value2"})
    cache.set("key3", {"data": "value3"})

    # Oldest value should be removed
    assert cache.get("key1") is None
    assert cache.get("key2") == {"data": "value2"}
    assert cache.get("key3") == {"data": "value3"}


def test_cache_serialization(cache):
    """Test cache serialization of different data types."""
    test_data = {
        "string": "test",
        "number": 42,
        "boolean": True,
        "list": [1, 2, 3],
        "dict": {"nested": "value"},
        "none": None,
    }

    cache.set("complex_data", test_data)
    result = cache.get("complex_data")
    assert result == test_data


def test_cache_concurrent_access(cache):
    """Test cache behavior under concurrent access."""
    import threading

    def worker():
        for i in range(10):
            cache.set(f"key_{i}", {"data": f"value_{i}"})
            time.sleep(0.01)

    # Create multiple threads accessing cache
    threads = [threading.Thread(target=worker) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Verify all values were set correctly
    for i in range(10):
        assert cache.get(f"key_{i}") == {"data": f"value_{i}"}
