#!/usr/bin/env python3
"""
CodeGuardian Bot - Main entry point
"""

import os
import sys

from dotenv import load_dotenv
from github import Github

from codeguardian.analyzers.code_quality import CodeQualityAnalyzer
from codeguardian.analyzers.coverage import CoverageAnalyzer
from codeguardian.analyzers.pr_quality import PRQualityAnalyzer
from codeguardian.utils.config import load_config
from codeguardian.utils.github import get_pr_context
from codeguardian.utils.logging import logger, track_performance


@track_performance(logger)
def main():
    """Main entry point for the CodeGuardian bot."""
    # Load environment variables
    load_dotenv()

    # Get GitHub token
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        logger.error("GITHUB_TOKEN environment variable is required")
        sys.exit(1)

    # Initialize GitHub client
    github = Github(github_token)

    # Get PR context from environment
    pr_context = get_pr_context()
    if not pr_context:
        logger.error("Not running in a pull request context")
        sys.exit(1)

    logger.info(
        "Starting analysis",
        repository=pr_context["repository"],
        pr_number=pr_context["number"],
    )

    # Load configuration
    config = load_config()

    # Initialize analyzers
    coverage_analyzer = CoverageAnalyzer(github, pr_context, config)
    code_quality_analyzer = CodeQualityAnalyzer(github, pr_context, config)
    pr_quality_analyzer = PRQualityAnalyzer(github, pr_context, config)

    # Run analysis
    logger.info("Running coverage analysis")
    coverage_results = coverage_analyzer.analyze()

    logger.info("Running code quality analysis")
    code_quality_results = code_quality_analyzer.analyze()

    logger.info("Running PR quality analysis")
    pr_quality_results = pr_quality_analyzer.analyze()

    # Generate and post comment
    logger.info("Generating analysis report")
    comment = generate_comment(
        coverage_results, code_quality_results, pr_quality_results
    )

    logger.info("Posting analysis report")
    post_comment(github, pr_context, comment)

    logger.info("Analysis complete")


@track_performance(logger)
def generate_comment(coverage_results, code_quality_results, pr_quality_results):
    """Generate a formatted comment with analysis results."""
    comment = "## 🤖 CodeGuardian Analysis Report\n\n"

    # Add coverage section
    comment += "### 📊 Coverage Analysis\n"
    comment += coverage_results.format_report()

    # Add code quality section
    comment += "\n### 🔍 Code Quality Analysis\n"
    comment += code_quality_results.format_report()

    # Add PR quality section
    comment += "\n### ✅ PR Quality Assessment\n"
    comment += pr_quality_results.format_report()

    return comment


@track_performance(logger)
def post_comment(github, pr_context, comment):
    """Post the analysis comment to the PR."""
    repo = github.get_repo(pr_context["repository"])
    pr = repo.get_pull(pr_context["number"])

    # Check for existing bot comment
    existing_comments = pr.get_issue_comments()
    for existing in existing_comments:
        if existing.user.login == github.get_user().login:
            logger.info("Updating existing comment", comment_id=existing.id)
            existing.edit(comment)
            return

    # Post new comment if none exists
    logger.info("Creating new comment")
    pr.create_issue_comment(comment)


if __name__ == "__main__":
    main()
