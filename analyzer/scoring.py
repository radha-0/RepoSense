"""
scoring.py — Calculate the overall repository score and grade.

Scoring weights (total = 100):
  - README quality:   25 points
  - Activity:         20 points
  - Structure:        20 points
  - Popularity:       10 points
  - Best practices:   25 points

Grades:
  - A  → 80–100
  - B  → 60–79
  - C  → 40–59
  - D  → 20–39
  - F  → 0–19
"""

from datetime import datetime, timezone


def calculate_activity_score(commits: list[dict], metadata: dict) -> dict:
    """
    Score the repository's activity level based on commits and recency.

    Args:
        commits: List of commit dicts from github_api.fetch_commits().
        metadata: Repo metadata from github_api.fetch_repo_metadata().

    Returns:
        A dict with:
            score (float): Activity score out of 20.
            total_commits (int): Number of commits fetched.
            days_since_update (int): Days since last update.
            commit_frequency (str): 'high', 'moderate', 'low', or 'inactive'.
            issues (list[str])
            strengths (list[str])
    """
    result = {
        "score": 0.0,
        "total_commits": len(commits),
        "days_since_update": -1,
        "commit_frequency": "unknown",
        "issues": [],
        "strengths": [],
    }

    score = 0.0

    # --- Commit count scoring: up to 10 points ---
    num_commits = len(commits)
    if num_commits >= 50:
        score += 10.0
        result["commit_frequency"] = "high"
        result["strengths"].append(f"Strong commit history ({num_commits}+ commits)")
    elif num_commits >= 20:
        score += 7.0
        result["commit_frequency"] = "moderate"
        result["strengths"].append(f"Good commit history ({num_commits} commits)")
    elif num_commits >= 5:
        score += 4.0
        result["commit_frequency"] = "low"
        result["issues"].append("Commit history is thin — aim for more regular commits")
    elif num_commits >= 1:
        score += 2.0
        result["commit_frequency"] = "low"
        result["issues"].append("Very few commits — shows limited project development")
    else:
        result["commit_frequency"] = "inactive"
        result["issues"].append("No commits found")

    # --- Recency scoring: up to 10 points ---
    updated_at = metadata.get("updated_at", "")
    if updated_at:
        try:
            last_update = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            days_since = (now - last_update).days
            result["days_since_update"] = days_since

            if days_since <= 7:
                score += 10.0
                result["strengths"].append("Updated within the last week")
            elif days_since <= 30:
                score += 8.0
                result["strengths"].append("Updated within the last month")
            elif days_since <= 90:
                score += 5.0
                result["issues"].append("Last update was over a month ago")
            elif days_since <= 365:
                score += 2.0
                result["issues"].append("Repository hasn't been updated in months")
            else:
                score += 0.0
                result["issues"].append("Repository appears abandoned (no updates in over a year)")
        except (ValueError, TypeError):
            pass

    result["score"] = min(score, 20.0)
    return result


def calculate_popularity_score(metadata: dict) -> dict:
    """
    Score the repository's popularity based on stars, forks, and issues.

    Args:
        metadata: Repo metadata from github_api.fetch_repo_metadata().

    Returns:
        A dict with:
            score (float): Popularity score out of 10.
            issues (list[str])
            strengths (list[str])
    """
    result = {
        "score": 0.0,
        "issues": [],
        "strengths": [],
    }

    score = 0.0
    stars = metadata.get("stars", 0)
    forks = metadata.get("forks", 0)

    # --- Stars: up to 5 points ---
    if stars >= 50:
        score += 5.0
        result["strengths"].append(f"Popular project — {stars} stars")
    elif stars >= 10:
        score += 3.0
        result["strengths"].append(f"Growing popularity — {stars} stars")
    elif stars >= 1:
        score += 1.5
        result["strengths"].append(f"Has {stars} star(s)")
    else:
        # For student projects, 0 stars is normal — don't penalize too harshly
        score += 0.5
        result["issues"].append("No stars yet — share your project to gain visibility")

    # --- Forks: up to 5 points ---
    if forks >= 10:
        score += 5.0
        result["strengths"].append(f"Project has been forked {forks} times")
    elif forks >= 3:
        score += 3.0
        result["strengths"].append(f"Project has {forks} fork(s)")
    elif forks >= 1:
        score += 1.5
        result["strengths"].append(f"Project has been forked")
    else:
        score += 0.5

    result["score"] = min(score, 10.0)
    return result


def calculate_total_score(
    readme_score: float,
    activity_score: float,
    structure_score: float,
    popularity_score: float,
    best_practices_score: float,
) -> dict:
    """
    Calculate the overall score and assign a grade.

    Args:
        readme_score: Score out of 25.
        activity_score: Score out of 20.
        structure_score: Score out of 20.
        popularity_score: Score out of 10.
        best_practices_score: Score out of 25.

    Returns:
        A dict with:
            total_score (float): Final score out of 100.
            grade (str): Letter grade (A/B/C/D/F).
            breakdown (dict): Individual category scores.
    """
    total = (
        readme_score
        + activity_score
        + structure_score
        + popularity_score
        + best_practices_score
    )

    # Clamp to 0–100
    total = max(0.0, min(100.0, total))

    # Assign grade
    if total >= 80:
        grade = "A"
    elif total >= 60:
        grade = "B"
    elif total >= 40:
        grade = "C"
    elif total >= 20:
        grade = "D"
    else:
        grade = "F"

    return {
        "total_score": round(total, 1),
        "grade": grade,
        "breakdown": {
            "readme_quality": {"score": round(readme_score, 1), "max": 25},
            "activity": {"score": round(activity_score, 1), "max": 20},
            "structure": {"score": round(structure_score, 1), "max": 20},
            "popularity": {"score": round(popularity_score, 1), "max": 10},
            "best_practices": {"score": round(best_practices_score, 1), "max": 25},
        },
    }
