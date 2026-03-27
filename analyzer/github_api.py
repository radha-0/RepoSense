"""
github_api.py — Fetch repository data from the GitHub REST API.

Handles:
  - Repository metadata (stars, forks, issues, etc.)
  - Commit history
  - README content
  - Repository file tree (root-level contents)
"""

import base64
import os
from datetime import datetime, timezone

import requests


# GitHub API base URL
BASE_URL = "https://api.github.com"

# Read optional token from environment variable
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


def _get_headers() -> dict:
    """Build request headers, optionally including auth token."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "RepoSense-Analyzer",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers


def _handle_response(response: requests.Response, resource: str) -> dict | list | None:
    """
    Check response status and return JSON, or raise descriptive errors.

    Args:
        response: The HTTP response object.
        resource: Human-readable name of the resource (for error messages).

    Returns:
        Parsed JSON as dict/list, or None for 404s.

    Raises:
        ConnectionError: On rate limiting or server errors.
        FileNotFoundError: On 404 (resource not found).
    """
    if response.status_code == 200:
        return response.json()

    if response.status_code == 404:
        return None

    if response.status_code == 403:
        # Check if rate-limited
        remaining = response.headers.get("X-RateLimit-Remaining", "?")
        reset_time = response.headers.get("X-RateLimit-Reset", "")
        reset_str = ""
        if reset_time:
            try:
                reset_dt = datetime.fromtimestamp(int(reset_time), tz=timezone.utc)
                reset_str = f" (resets at {reset_dt.strftime('%H:%M:%S UTC')})"
            except (ValueError, OSError):
                pass
        raise ConnectionError(
            f"GitHub API rate limit hit (remaining: {remaining}){reset_str}.\n"
            "💡 Set GITHUB_TOKEN environment variable to increase your limit.\n"
            "   export GITHUB_TOKEN=your_personal_access_token"
        )

    if response.status_code == 401:
        raise ConnectionError(
            "GitHub API authentication failed. Check your GITHUB_TOKEN."
        )

    raise ConnectionError(
        f"GitHub API error fetching {resource}: "
        f"HTTP {response.status_code} — {response.reason}"
    )


def fetch_repo_metadata(owner: str, repo: str) -> dict:
    """
    Fetch core repository metadata.

    Returns a dict with keys:
        name, full_name, description, stars, forks, open_issues,
        language, license, created_at, updated_at, default_branch, topics
    """
    url = f"{BASE_URL}/repos/{owner}/{repo}"
    response = requests.get(url, headers=_get_headers(), timeout=15)
    data = _handle_response(response, f"repository '{owner}/{repo}'")

    if data is None:
        raise FileNotFoundError(f"Repository '{owner}/{repo}' not found on GitHub.")

    # Extract the license name safely
    license_info = data.get("license")
    license_name = license_info.get("spdx_id", "Unknown") if license_info else None

    return {
        "name": data.get("name", ""),
        "full_name": data.get("full_name", ""),
        "description": data.get("description", ""),
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "open_issues": data.get("open_issues_count", 0),
        "language": data.get("language", "Unknown"),
        "license": license_name,
        "created_at": data.get("created_at", ""),
        "updated_at": data.get("updated_at", ""),
        "default_branch": data.get("default_branch", "main"),
        "topics": data.get("topics", []),
    }


def fetch_commits(owner: str, repo: str, max_pages: int = 3) -> list[dict]:
    """
    Fetch recent commits (up to max_pages * 30).

    Returns a list of dicts with keys: sha, message, date, author.
    """
    commits = []
    for page in range(1, max_pages + 1):
        url = f"{BASE_URL}/repos/{owner}/{repo}/commits"
        params = {"per_page": 30, "page": page}
        response = requests.get(url, headers=_get_headers(), params=params, timeout=15)
        data = _handle_response(response, "commits")

        if not data:
            break

        for commit in data:
            commit_info = commit.get("commit", {})
            author_info = commit_info.get("author", {})
            commits.append({
                "sha": commit.get("sha", "")[:7],
                "message": commit_info.get("message", "").split("\n")[0],  # First line only
                "date": author_info.get("date", ""),
                "author": author_info.get("name", "Unknown"),
            })

        # If we got fewer than 30 results, no more pages
        if len(data) < 30:
            break

    return commits


def fetch_readme(owner: str, repo: str) -> str | None:
    """
    Fetch the README content (decoded from base64).

    Returns the README text, or None if no README exists.
    """
    url = f"{BASE_URL}/repos/{owner}/{repo}/readme"
    response = requests.get(url, headers=_get_headers(), timeout=15)
    data = _handle_response(response, "README")

    if data is None:
        return None

    content = data.get("content", "")
    encoding = data.get("encoding", "base64")

    if encoding == "base64" and content:
        try:
            return base64.b64decode(content).decode("utf-8", errors="replace")
        except Exception:
            return None

    return content if content else None


def fetch_repo_contents(owner: str, repo: str, path: str = "") -> list[dict] | None:
    """
    Fetch the file listing at a given path in the repo (default: root).

    Returns a list of dicts with keys: name, type ('file' or 'dir'), size.
    """
    url = f"{BASE_URL}/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url, headers=_get_headers(), timeout=15)
    data = _handle_response(response, f"contents at '{path or '/'}'")

    if data is None or not isinstance(data, list):
        return None

    return [
        {
            "name": item.get("name", ""),
            "type": item.get("type", ""),
            "size": item.get("size", 0),
        }
        for item in data
    ]
