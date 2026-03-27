"""
parser.py — Extract owner and repo name from a GitHub URL.

Supports formats like:
  - https://github.com/owner/repo
  - https://github.com/owner/repo.git
  - github.com/owner/repo
  - owner/repo
"""

import re


def parse_github_url(url: str) -> tuple[str, str]:
    """
    Parse a GitHub repository URL and return (owner, repo_name).

    Args:
        url: A GitHub repo URL or shorthand like 'owner/repo'.

    Returns:
        A tuple of (owner, repo_name).

    Raises:
        ValueError: If the URL cannot be parsed into owner/repo.
    """
    # Strip whitespace and trailing slashes
    url = url.strip().rstrip("/")

    # Remove .git suffix if present
    if url.endswith(".git"):
        url = url[:-4]

    # Pattern 1: Full URL — https://github.com/owner/repo
    full_url_pattern = r"(?:https?://)?github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)"
    match = re.match(full_url_pattern, url)
    if match:
        return match.group(1), match.group(2)

    # Pattern 2: Shorthand — owner/repo
    shorthand_pattern = r"^([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)$"
    match = re.match(shorthand_pattern, url)
    if match:
        return match.group(1), match.group(2)

    raise ValueError(
        f"Invalid GitHub URL: '{url}'\n"
        "Expected formats:\n"
        "  • https://github.com/owner/repo\n"
        "  • github.com/owner/repo\n"
        "  • owner/repo"
    )
