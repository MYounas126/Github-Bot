"""
Code quality analysis module for CodeGuardian bot.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from radon.complexity import cc_visit
from radon.metrics import h_visit
from radon.raw import analyze


@dataclass
class CodeQualityResult:
    """Container for code quality analysis results."""

    complexity: Dict[str, float]  # File -> complexity score
    maintainability: Dict[str, float]  # File -> maintainability index
    issues: Dict[str, List[str]]  # File -> list of issues
    suggestions: List[str]  # General suggestions for improvement

    def format_report(self) -> str:
        """Format the code quality results as a markdown report."""
        report = []

        # Overall metrics
        if self.complexity:
            avg_complexity = sum(self.complexity.values()) / len(self.complexity)
            report.append(f"**Average Complexity**: {avg_complexity:.1f}")

        if self.maintainability:
            avg_maintainability = sum(self.maintainability.values()) / len(
                self.maintainability
            )
            report.append(f"**Average Maintainability**: {avg_maintainability:.1f}")

        # File-specific issues
        if self.issues:
            report.append("\n**Code Quality Issues**:")
            for file, issues in self.issues.items():
                report.append(f"\n**{file}**:")
                for issue in issues:
                    report.append(f"- {issue}")

        # General suggestions
        if self.suggestions:
            report.append("\n**Suggestions for Improvement**:")
            for suggestion in self.suggestions:
                report.append(f"- {suggestion}")

        return "\n".join(report)


class CodeQualityAnalyzer:
    """Analyzes code quality for a pull request."""

    def __init__(self, github, pr_context, config):
        self.github = github
        self.pr_context = pr_context
        self.config = config

    def analyze(self) -> CodeQualityResult:
        """Run code quality analysis on the PR."""
        # Get changed files
        changed_files = self._get_changed_files()

        # Analyze each file
        complexity = {}
        maintainability = {}
        issues = {}
        suggestions = []

        for file in changed_files:
            file_content = self._get_file_content(file)
            if not file_content:
                continue

            # Calculate complexity
            complexity[file] = self._calculate_complexity(file_content)

            # Calculate maintainability
            maintainability[file] = self._calculate_maintainability(file_content)

            # Find issues
            issues[file] = self._find_issues(file_content)

        # Generate general suggestions
        suggestions = self._generate_suggestions(complexity, maintainability, issues)

        return CodeQualityResult(
            complexity=complexity,
            maintainability=maintainability,
            issues=issues,
            suggestions=suggestions,
        )

    def _get_changed_files(self) -> List[str]:
        """Get list of files changed in the PR."""
        # Implementation would use GitHub API to get changed files
        return []

    def _get_file_content(self, file_path: str) -> Optional[str]:
        """Get the content of a file from the PR."""
        # Implementation would use GitHub API to get file content
        return None

    def _calculate_complexity(self, content: str) -> float:
        """Calculate cyclomatic complexity for a file."""
        try:
            results = list(cc_visit(content))
            return sum(r.complexity for r in results)
        except Exception:
            return 0.0

    def _calculate_maintainability(self, content: str) -> float:
        """Calculate maintainability index for a file."""
        try:
            results = list(h_visit(content))
            return sum(r.maintainability_index for r in results)
        except Exception:
            return 0.0

    def _find_issues(self, content: str) -> List[str]:
        """Find code quality issues in a file."""
        issues = []

        # Check for long functions
        for block in cc_visit(content):
            if block.complexity > self.config.get("max_complexity", 10):
                issues.append(
                    f"Function '{block.name}' is too complex (complexity: {block.complexity})"
                )

        # Check for long files
        raw_metrics = analyze(content)
        if raw_metrics.loc > self.config.get("max_lines", 300):
            issues.append(f"File is too long ({raw_metrics.loc} lines)")

        return issues

    def _generate_suggestions(
        self,
        complexity: Dict[str, float],
        maintainability: Dict[str, float],
        issues: Dict[str, List[str]],
    ) -> List[str]:
        """Generate general suggestions based on analysis results."""
        suggestions = []

        # Check overall complexity
        if complexity:
            avg_complexity = sum(complexity.values()) / len(complexity)
            if avg_complexity > 15:
                suggestions.append(
                    "Consider breaking down complex functions into smaller, more manageable pieces"
                )

        # Check maintainability
        if maintainability:
            avg_maintainability = sum(maintainability.values()) / len(maintainability)
            if avg_maintainability < 50:
                suggestions.append(
                    "Consider improving code maintainability by reducing complexity and improving documentation"
                )

        return suggestions
