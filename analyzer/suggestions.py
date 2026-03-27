"""
suggestions.py — Generate prioritized, actionable suggestions for improvement.

Collects issues from all analysis modules and ranks them by impact.
Also collects strengths for positive reinforcement.
"""


# Priority tiers: higher tier = more impactful to fix
PRIORITY_MAP = {
    # Critical — these affect first impressions the most
    "README file is missing": 1,
    "No LICENSE file": 1,
    "Missing .gitignore": 1,
    "No dependency file": 2,
    "Add a repository description": 2,

    # Important — recruiters notice these
    "Missing installation": 2,
    "Missing usage": 2,
    "README is too short": 2,
    "No topic tags": 3,
    "No screenshots": 3,

    # Nice to have
    "No stars yet": 4,
    "Commit history is thin": 3,
    "Very few commits": 3,
    "appears abandoned": 3,
}


def _get_priority(issue: str) -> int:
    """
    Determine the priority of an issue string (lower = more urgent).
    Defaults to priority 3 if no keyword match is found.
    """
    for keyword, priority in PRIORITY_MAP.items():
        if keyword.lower() in issue.lower():
            return priority
    return 3


def generate_suggestions(
    readme_result: dict,
    structure_result: dict,
    activity_result: dict,
    popularity_result: dict,
    best_practices_result: dict,
) -> dict:
    """
    Combine all analysis results into prioritized suggestions and strengths.

    Args:
        readme_result: From readme_checker.analyze_readme().
        structure_result: From structure.analyze_structure().
        activity_result: From scoring.calculate_activity_score().
        popularity_result: From scoring.calculate_popularity_score().
        best_practices_result: From structure.analyze_best_practices().

    Returns:
        A dict with:
            suggestions (list[dict]): Each has 'text' and 'priority' (1=critical, 4=minor).
            strengths (list[str]): All positive aspects found.
            top_priority (str): The single most important thing to fix.
    """
    # --- Collect all issues ---
    all_issues = []
    all_issues.extend(readme_result.get("issues", []))
    all_issues.extend(structure_result.get("issues", []))
    all_issues.extend(activity_result.get("issues", []))
    all_issues.extend(popularity_result.get("issues", []))
    all_issues.extend(best_practices_result.get("issues", []))

    # Deduplicate while preserving order
    seen = set()
    unique_issues = []
    for issue in all_issues:
        normalized = issue.lower().strip()
        if normalized not in seen:
            seen.add(normalized)
            unique_issues.append(issue)

    # Assign priority and sort (most urgent first)
    suggestions = [
        {"text": issue, "priority": _get_priority(issue)}
        for issue in unique_issues
    ]
    suggestions.sort(key=lambda s: s["priority"])

    # --- Collect all strengths ---
    all_strengths = []
    all_strengths.extend(readme_result.get("strengths", []))
    all_strengths.extend(structure_result.get("strengths", []))
    all_strengths.extend(activity_result.get("strengths", []))
    all_strengths.extend(popularity_result.get("strengths", []))
    all_strengths.extend(best_practices_result.get("strengths", []))

    # Deduplicate strengths
    seen_strengths = set()
    unique_strengths = []
    for strength in all_strengths:
        normalized = strength.lower().strip()
        if normalized not in seen_strengths:
            seen_strengths.add(normalized)
            unique_strengths.append(strength)

    # --- Top priority ---
    top = suggestions[0]["text"] if suggestions else "Your repo looks great!"

    return {
        "suggestions": suggestions,
        "strengths": unique_strengths,
        "top_priority": top,
    }
