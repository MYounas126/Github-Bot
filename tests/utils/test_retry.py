"""
Tests for the retry utilities.
"""

import time
from unittest.mock import Mock, patch

import pytest
from github import GithubException

from codeguardian.utils.retry import RetryError, retry_with_backoff


def test_retry_success():
    """Test successful retry after failures."""
    mock_func = Mock(side_effect=[Exception(), Exception(), "success"])

    @retry_with_backoff(max_retries=2, base_delay=0.1)
    def test_func():
        return mock_func()

    result = test_func()
    assert result == "success"
    assert mock_func.call_count == 3


def test_retry_max_attempts_exceeded():
    """Test retry failure after max attempts."""
    mock_func = Mock(side_effect=Exception("test error"))

    @retry_with_backoff(max_retries=2, base_delay=0.1)
    def test_func():
        return mock_func()

    with pytest.raises(RetryError) as exc_info:
        test_func()

    assert "Max retries (2) exceeded" in str(exc_info.value)
    assert mock_func.call_count == 3


def test_retry_rate_limit():
    """Test retry with rate limit handling."""
    mock_func = Mock(
        side_effect=[
            GithubException(
                403, "rate limit", {"X-RateLimit-Reset": str(int(time.time()) + 1)}
            ),
            "success",
        ]
    )

    @retry_with_backoff(max_retries=2, base_delay=0.1)
    def test_func():
        return mock_func()

    result = test_func()
    assert result == "success"
    assert mock_func.call_count == 2


def test_retry_exponential_backoff():
    """Test exponential backoff delay calculation."""
    mock_func = Mock(side_effect=[Exception(), Exception(), "success"])
    delays = []

    original_sleep = time.sleep

    def mock_sleep(delay):
        delays.append(delay)
        original_sleep(0)  # Don't actually sleep during tests

    with patch("time.sleep", mock_sleep):

        @retry_with_backoff(max_retries=2, base_delay=1.0, exponential_base=2.0)
        def test_func():
            return mock_func()

        test_func()

    # Check that delays follow exponential backoff
    assert len(delays) == 2
    assert delays[0] == 1.0  # First retry
    assert delays[1] == 2.0  # Second retry


def test_retry_specific_exceptions():
    """Test retry with specific exceptions."""
    mock_func = Mock(side_effect=[ValueError(), ValueError(), "success"])

    @retry_with_backoff(max_retries=2, base_delay=0.1, exceptions=ValueError)
    def test_func():
        return mock_func()

    result = test_func()
    assert result == "success"
    assert mock_func.call_count == 3


def test_retry_unhandled_exception():
    """Test that unhandled exceptions are not retried."""
    mock_func = Mock(side_effect=ValueError("test error"))

    @retry_with_backoff(max_retries=2, base_delay=0.1, exceptions=TypeError)
    def test_func():
        return mock_func()

    with pytest.raises(ValueError) as exc_info:
        test_func()

    assert "test error" in str(exc_info.value)
    assert mock_func.call_count == 1
