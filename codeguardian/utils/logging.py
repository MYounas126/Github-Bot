"""
Logging utilities for CodeGuardian bot.
"""

import json
import logging
import time
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, Optional


class StructuredLogger:
    """Structured logger with performance tracking."""

    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Add JSON formatter if no handlers exist
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _format_message(self, message: str, **kwargs) -> str:
        """Format message with additional context as JSON."""
        log_data = {
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs,
        }
        return json.dumps(log_data)

    def info(self, message: str, **kwargs) -> None:
        """Log info level message with context."""
        self.logger.info(self._format_message(message, **kwargs))

    def warning(self, message: str, **kwargs) -> None:
        """Log warning level message with context."""
        self.logger.warning(self._format_message(message, **kwargs))

    def error(self, message: str, **kwargs) -> None:
        """Log error level message with context."""
        self.logger.error(self._format_message(message, **kwargs))

    def debug(self, message: str, **kwargs) -> None:
        """Log debug level message with context."""
        self.logger.debug(self._format_message(message, **kwargs))

    def performance(self, message: str, duration_ms: float, **kwargs) -> None:
        """Log performance metrics."""
        self.info(message, duration_ms=duration_ms, performance_metric=True, **kwargs)


def track_performance(logger: StructuredLogger):
    """Decorator to track function performance."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.performance(
                    f"Function {func.__name__} completed",
                    duration_ms=duration_ms,
                    function=func.__name__,
                    success=True,
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"Function {func.__name__} failed",
                    duration_ms=duration_ms,
                    function=func.__name__,
                    error=str(e),
                    success=False,
                )
                raise

        return wrapper

    return decorator


# Create default logger instance
logger = StructuredLogger("codeguardian")
