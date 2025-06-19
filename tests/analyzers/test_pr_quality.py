"""
Tests for the PR quality analyzer.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from codeguardian.analyzers.pr_quality import (PRQualityAnalyzer,
                                               PRQualityResult)


@pytest.fixture
def mock_github():
    """Create a mock GitHub instance."""
    return Mock()


@pytest.fixture
def mock_pr_context():
    """Create a mock PR context."""
    return {
        "repository": "owner/repo",
        "number": 123,
        "base": "main",
        "head": "feature-branch",
    }


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    return {
        "pr_quality": {
            "require_issue_link": True,
            "require_test_summary": True,
            "min_description_length": 50,
        }
    }


@pytest.fixture
def mock_pr():
    """Create a mock PR object."""
    pr = Mock()
    pr.body = """
    # Feature Implementation
    
    This PR implements feature X.
    
    ## Testing
    - Unit tests added
    - Integration tests passing
    
    Fixes #123
    """
    pr.created_at = datetime.utcnow() - timedelta(hours=2)
    return pr


def test_analyze_description_quality(
    mock_github, mock_pr_context, mock_config, mock_pr
):
    """Test PR description quality analysis."""
    analyzer = PRQualityAnalyzer(mock_github, mock_pr_context, mock_config)

    with patch.object(analyzer, "_get_pr_details", return_value=mock_pr):
        result = analyzer.analyze()

        assert isinstance(result, PRQualityResult)
        assert result.description_score > 60  # Good description
        assert result.review_time is not None
        assert result.review_time > 0
        assert "#123" in result.issue_links
        assert not result.missing_elements  # All required elements present


def test_analyze_poor_description(mock_github, mock_pr_context, mock_config):
    """Test analysis of a poor PR description."""
    mock_pr = Mock()
    mock_pr.body = "Fixes bug"
    mock_pr.created_at = datetime.utcnow()

    analyzer = PRQualityAnalyzer(mock_github, mock_pr_context, mock_config)

    with patch.object(analyzer, "_get_pr_details", return_value=mock_pr):
        result = analyzer.analyze()

        assert result.description_score < 40  # Poor description
        assert "Detailed PR description" in result.missing_elements
        assert "Linked issue(s)" in result.missing_elements
        assert "Testing information" in result.missing_elements


def test_analyze_long_review_time(mock_github, mock_pr_context, mock_config, mock_pr):
    """Test analysis of PR with long review time."""
    mock_pr.created_at = datetime.utcnow() - timedelta(hours=49)

    analyzer = PRQualityAnalyzer(mock_github, mock_pr_context, mock_config)

    with patch.object(analyzer, "_get_pr_details", return_value=mock_pr):
        result = analyzer.analyze()

        assert result.review_time > 48
        assert any("48 hours" in s for s in result.suggestions)


def test_analyze_missing_pr_details(mock_github, mock_pr_context, mock_config):
    """Test handling of missing PR details."""
    analyzer = PRQualityAnalyzer(mock_github, mock_pr_context, mock_config)

    with patch.object(analyzer, "_get_pr_details", return_value=None):
        result = analyzer.analyze()

        assert result.description_score == 0
        assert result.review_time is None
        assert "Could not fetch PR details" in result.missing_elements
