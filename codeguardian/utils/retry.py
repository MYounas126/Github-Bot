"""
Retry utilities for CodeGuardian bot.
"""

import time
from functools import wraps
from typing import Any, Callable, Optional, Tuple, Type, Union

from github import GithubException

from codeguardian.utils.logging import logger


class RetryError(Exception):
    """Custom exception for retry failures."""

    pass


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
) -> Callable:
    """
    Retry decorator with exponential backoff and rate limit handling.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff
        exceptions: Exception(s) to catch and retry on
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    # Handle GitHub rate limits
                    if isinstance(e, GithubException) and e.status == 403:
                        reset_time = int(e.headers.get("X-RateLimit-Reset", 0))
                        if reset_time:
                            wait_time = max(reset_time - time.time(), 0)
                            logger.warning(
                                "Rate limit hit, waiting for reset",
                                reset_time=reset_time,
                                wait_time=wait_time,
                            )
                            time.sleep(wait_time)
                            continue

                    # Calculate delay with exponential backoff
                    if attempt < max_retries:
                        delay = min(base_delay * (exponential_base**attempt), max_delay)

                        logger.warning(
                            f"Retry attempt {attempt + 1}/{max_retries}",
                            error=str(e),
                            delay=delay,
                            function=func.__name__,
                        )

                        time.sleep(delay)
                    else:
                        logger.error(
                            "Max retries exceeded", error=str(e), function=func.__name__
                        )
                        raise RetryError(
                            f"Max retries ({max_retries}) exceeded for {func.__name__}"
                        ) from last_exception

            raise RetryError(
                f"Max retries ({max_retries}) exceeded for {func.__name__}"
            ) from last_exception

        return wrapper

    return decorator
