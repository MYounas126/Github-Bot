"""
Caching utilities for CodeGuardian bot.
"""

import json
import logging
import os
import threading
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from codeguardian.utils.logging import logger

logger = logging.getLogger(__name__)


class Cache:
    """A file-based cache with TTL and size management."""

    def __init__(
        self,
        cache_dir: str = ".cache",
        ttl: int = 3600,
        max_size: int = 1000,
        cleanup_interval: int = 300,
    ):
        """Initialize the cache.

        Args:
            cache_dir: Directory to store cache files
            ttl: Time-to-live for cache entries in seconds
            max_size: Maximum number of cache entries
            cleanup_interval: Interval for automatic cleanup in seconds
        """
        self.cache_dir = Path(cache_dir)
        self.ttl = ttl
        self.max_size = max_size
        self.cleanup_interval = cleanup_interval
        self._lock = threading.Lock()

        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Start cleanup thread
        self._start_cleanup_thread()

    def _start_cleanup_thread(self):
        """Start the background cleanup thread."""

        def cleanup_worker():
            while True:
                time.sleep(self.cleanup_interval)
                try:
                    self.cleanup()
                except Exception as e:
                    logger.error(f"Cache cleanup failed: {e}")

        thread = threading.Thread(target=cleanup_worker, daemon=True)
        thread.start()

    def _get_cache_path(self, key: str) -> Path:
        """Get the cache file path for a key."""
        return self.cache_dir / f"{key}.json"

    def _get_cache_files(self) -> list[Path]:
        """Get all cache files sorted by modification time."""
        return sorted(self.cache_dir.glob("*.json"), key=lambda p: p.stat().st_mtime)

    def set(self, key: str, value: Any) -> None:
        """Set a value in the cache.

        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
        """
        with self._lock:
            # Check cache size and remove oldest entries if needed
            if self.max_size > 0:
                cache_files = self._get_cache_files()
                while len(cache_files) >= self.max_size:
                    oldest_file = cache_files.pop(0)
                    try:
                        oldest_file.unlink()
                    except Exception as e:
                        logger.warning(
                            f"Failed to remove old cache file {oldest_file}: {e}"
                        )

            # Write new cache entry
            cache_path = self._get_cache_path(key)
            try:
                with open(cache_path, "w") as f:
                    json.dump({"data": value, "expires_at": time.time() + self.ttl}, f)
            except Exception as e:
                logger.error(f"Failed to write cache file {cache_path}: {e}")

    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path) as f:
                entry = json.load(f)

            # Check expiration
            if time.time() > entry["expires_at"]:
                cache_path.unlink()
                return None

            return entry["data"]
        except Exception as e:
            logger.warning(f"Failed to read cache file {cache_path}: {e}")
            return None

    def cleanup(self) -> None:
        """Clean up expired cache entries."""
        with self._lock:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file) as f:
                        entry = json.load(f)

                    if time.time() > entry["expires_at"]:
                        cache_file.unlink()
                except Exception as e:
                    logger.warning(f"Failed to process cache file {cache_file}: {e}")
                    # Remove corrupted files
                    try:
                        cache_file.unlink()
                    except Exception as e:
                        logger.error(
                            f"Failed to remove corrupted cache file {cache_file}: {e}"
                        )

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    cache_file.unlink()
                except Exception as e:
                    logger.error(f"Failed to remove cache file {cache_file}: {e}")


def cached(cache: Cache) -> Callable:
    """Decorator to cache function results.

    Args:
        cache: Cache instance to use

    Returns:
        Decorated function that caches its results
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Generate cache key from function name and arguments
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            key = "_".join(key_parts)

            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result

            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result

        return wrapper

    return decorator


# Default cache instance
default_cache = Cache(
    cache_dir=os.getenv("CACHE_DIR", ".cache"),
    ttl=int(os.getenv("CACHE_TTL", "3600")),
    max_size=int(os.getenv("CACHE_MAX_SIZE", "1000")),
    cleanup_interval=int(os.getenv("CACHE_CLEANUP_INTERVAL", "300")),
)
