"""
PR quality analysis module for CodeGuardian bot.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class PRQualityResult:
    """Container for PR quality analysis results."""

    description_score: float  # 0-100 score for PR description quality
    review_time: Optional[float]  # Time in hours since PR creation
    issue_links: List[str]  # List of linked issues
    missing_elements: List[str]  # List of missing required elements
    suggestions: List[str]  # List of suggestions for improvement

    def format_report(self) -> str:
        """Format the PR quality results as a markdown report."""
        report = []

        # Description quality
        report.append(f"**PR Description Quality**: {self.description_score:.1f}/100")

        # Review time
        if self.review_time is not None:
            report.append(f"**Time Since Creation**: {self.review_time:.1f} hours")

        # Issue links
        if self.issue_links:
            report.append("\n**Linked Issues**:")
            for issue in self.issue_links:
                report.append(f"- {issue}")

        # Missing elements
        if self.missing_elements:
            report.append("\n**Missing Required Elements**:")
            for element in self.missing_elements:
                report.append(f"- {element}")

        # Suggestions
        if self.suggestions:
            report.append("\n**Suggestions**:")
            for suggestion in self.suggestions:
                report.append(f"- {suggestion}")

        return "\n".join(report)


class PRQualityAnalyzer:
    """Analyzes the quality of a pull request."""

    def __init__(self, github, pr_context, config):
        self.github = github
        self.pr_context = pr_context
        self.config = config

    def analyze(self) -> PRQualityResult:
        """Run PR quality analysis."""
        # Get PR details
        pr = self._get_pr_details()
        if not pr:
            return PRQualityResult(
                description_score=0,
                review_time=None,
                issue_links=[],
                missing_elements=["Could not fetch PR details"],
                suggestions=[],
            )

        # Analyze description
        description_score = self._analyze_description(pr.body or "")

        # Get review time
        review_time = self._calculate_review_time(pr.created_at)

        # Find linked issues
        issue_links = self._find_linked_issues(pr.body or "")

        # Check for missing elements
        missing_elements = self._check_required_elements(pr)

        # Generate suggestions
        suggestions = self._generate_suggestions(
            description_score, review_time, issue_links, missing_elements
        )

        return PRQualityResult(
            description_score=description_score,
            review_time=review_time,
            issue_links=issue_links,
            missing_elements=missing_elements,
            suggestions=suggestions,
        )

    def _get_pr_details(self):
        """Get PR details from GitHub API."""
        # Implementation would use GitHub API to get PR details
        return None

    def _analyze_description(self, description: str) -> float:
        """Analyze the quality of the PR description."""
        score = 0
        max_score = 100

        # Check for minimum length
        if len(description) > 50:
            score += 20

        # Check for issue links
        if re.search(r"#\d+", description):
            score += 20

        # Check for code blocks
        if re.search(r"```[\s\S]*?```", description):
            score += 20

        # Check for bullet points or numbered lists
        if re.search(r"^[\s]*[-*]|^[\s]*\d+\.", description, re.MULTILINE):
            score += 20

        # Check for testing information
        if re.search(r"test|testing|verified|validated", description, re.IGNORECASE):
            score += 20

        return score

    def _calculate_review_time(self, created_at: datetime) -> Optional[float]:
        """Calculate time since PR creation in hours."""
        if not created_at:
            return None

        now = datetime.utcnow()
        delta = now - created_at
        return delta.total_seconds() / 3600  # Convert to hours

    def _find_linked_issues(self, description: str) -> List[str]:
        """Find issues linked in the PR description."""
        issues = []
        for match in re.finditer(r"#(\d+)", description):
            issues.append(f"#{match.group(1)}")
        return issues

    def _check_required_elements(self, pr) -> List[str]:
        """Check for required elements in the PR."""
        missing = []

        # Check description
        if not pr.body or len(pr.body.strip()) < 50:
            missing.append("Detailed PR description")

        # Check for issue links
        if not self._find_linked_issues(pr.body or ""):
            missing.append("Linked issue(s)")

        # Check for testing information
        if not re.search(
            r"test|testing|verified|validated", pr.body or "", re.IGNORECASE
        ):
            missing.append("Testing information")

        return missing

    def _generate_suggestions(
        self,
        description_score: float,
        review_time: Optional[float],
        issue_links: List[str],
        missing_elements: List[str],
    ) -> List[str]:
        """Generate suggestions for improving the PR."""
        suggestions = []

        # Description quality
        if description_score < 60:
            suggestions.append("Consider adding more details to the PR description")

        # Review time
        if review_time and review_time > 48:  # 48 hours
            suggestions.append(
                "This PR has been open for more than 48 hours. Consider requesting a review"
            )

        # Missing elements
        for element in missing_elements:
            suggestions.append(f"Add {element.lower()}")

        return suggestions
