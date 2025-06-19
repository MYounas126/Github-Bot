"""
GitHub utilities for CodeGuardian bot.
"""

import os
from typing import Dict, Optional

from github import GithubException

from codeguardian.utils.cache import cached, default_cache
from codeguardian.utils.logging import logger, track_performance
from codeguardian.utils.retry import retry_with_backoff


@track_performance(logger)
def get_pr_context() -> Optional[Dict]:
    """
    Get PR context from environment variables.
    Returns None if not running in a PR context.
    """
    # GitHub Actions sets these environment variables
    event_name = os.getenv("GITHUB_EVENT_NAME")
    if event_name != "pull_request":
        logger.warning("Not running in a pull request context", event_name=event_name)
        return None

    # Get repository and PR number from environment
    repository = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("GITHUB_EVENT_NUMBER")

    if not repository or not pr_number:
        logger.error(
            "Missing required environment variables",
            repository=repository,
            pr_number=pr_number,
        )
        return None

    # Get base and head refs
    base_ref = os.getenv("GITHUB_BASE_REF")
    head_ref = os.getenv("GITHUB_HEAD_REF")

    context = {
        "repository": repository,
        "number": int(pr_number),
        "base": base_ref,
        "head": head_ref,
    }

    logger.info(
        "PR context retrieved",
        repository=repository,
        pr_number=pr_number,
        base_ref=base_ref,
        head_ref=head_ref,
    )

    return context


@cached(default_cache)
@retry_with_backoff(
    max_retries=3, base_delay=1.0, max_delay=30.0, exceptions=(GithubException,)
)
@track_performance(logger)
def get_changed_files(github, pr_context: Dict) -> list:
    """Get list of files changed in the PR."""
    try:
        repo = github.get_repo(pr_context["repository"])
        pr = repo.get_pull(pr_context["number"])

        files = [file.filename for file in pr.get_files()]
        logger.info("Retrieved changed files", file_count=len(files), files=files)
        return files
    except GithubException as e:
        logger.error(
            "Failed to get changed files",
            error=str(e),
            repository=pr_context["repository"],
            pr_number=pr_context["number"],
        )
        raise


@cached(default_cache)
@retry_with_backoff(
    max_retries=3, base_delay=1.0, max_delay=30.0, exceptions=(GithubException,)
)
@track_performance(logger)
def get_file_content(github, pr_context: Dict, file_path: str) -> Optional[str]:
    """Get the content of a file from the PR."""
    try:
        repo = github.get_repo(pr_context["repository"])
        pr = repo.get_pull(pr_context["number"])

        # Get the file content from the PR branch
        content = repo.get_contents(file_path, ref=pr.head.sha)
        if content:
            logger.info(
                "Retrieved file content",
                file=file_path,
                size=len(content.decoded_content),
            )
            return content.decoded_content.decode("utf-8")
    except GithubException as e:
        logger.error(
            "Failed to get file content",
            error=str(e),
            file=file_path,
            repository=pr_context["repository"],
            pr_number=pr_context["number"],
        )
        raise

    return None


@retry_with_backoff(
    max_retries=3, base_delay=1.0, max_delay=30.0, exceptions=(GithubException,)
)
@track_performance(logger)
def post_comment(github, pr_context: Dict, comment: str) -> None:
    """Post a comment to the PR."""
    try:
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
    except GithubException as e:
        logger.error(
            "Failed to post comment",
            error=str(e),
            repository=pr_context["repository"],
            pr_number=pr_context["number"],
        )
        raise
