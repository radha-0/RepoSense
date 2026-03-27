"""
readme_checker.py — Analyze the quality and completeness of a README file.

Checks for:
  - Existence
  - Length (word count)
  - Key sections: description, installation, usage, screenshots
  - Overall quality rating
"""

import re


# Section keywords to search for (case-insensitive)
SECTION_PATTERNS = {
    "description": [
        r"#+\s*(about|description|overview|introduction|what\s+is)",
        r"^[A-Z].*\n={2,}",  # Underline-style heading
    ],
    "installation": [
        r"#+\s*(install|setup|getting\s+started|quick\s+start)",
    ],
    "usage": [
        r"#+\s*(usage|how\s+to\s+use|examples?|demo)",
    ],
    "contributing": [
        r"#+\s*(contribut|how\s+to\s+contribute)",
    ],
    "license_section": [
        r"#+\s*license",
    ],
    "screenshots": [
        r"!\[.*\]\(.*\)",  # Markdown image syntax
        r"<img\s+",        # HTML img tag
        r"#+\s*(screenshot|demo|preview)",
    ],
}


def analyze_readme(readme_content: str | None) -> dict:
    """
    Analyze a README file and return a detailed report.

    Args:
        readme_content: The raw README text, or None if no README exists.

    Returns:
        A dict containing:
            exists (bool): Whether the README exists.
            word_count (int): Number of words.
            length_rating (str): 'short', 'adequate', or 'comprehensive'.
            sections_found (dict[str, bool]): Which key sections were detected.
            has_code_blocks (bool): Whether code examples are present.
            quality (str): Overall quality — 'poor', 'fair', 'good', or 'excellent'.
            score (float): Numeric quality score from 0 to 25 (max weight).
            issues (list[str]): Specific problems found.
            strengths (list[str]): Positive aspects found.
    """
    result = {
        "exists": False,
        "word_count": 0,
        "length_rating": "missing",
        "sections_found": {},
        "has_code_blocks": False,
        "quality": "poor",
        "score": 0.0,
        "issues": [],
        "strengths": [],
    }

    # --- No README ---
    if not readme_content or not readme_content.strip():
        result["issues"].append("README file is missing — this is critical for any project")
        return result

    result["exists"] = True
    text = readme_content.strip()

    # --- Word count & length rating ---
    words = text.split()
    result["word_count"] = len(words)

    if len(words) < 50:
        result["length_rating"] = "short"
        result["issues"].append("README is too short (< 50 words) — add more detail")
    elif len(words) < 200:
        result["length_rating"] = "adequate"
        result["strengths"].append("README has adequate length")
    else:
        result["length_rating"] = "comprehensive"
        result["strengths"].append("README is comprehensive and detailed")

    # --- Section detection ---
    for section_name, patterns in SECTION_PATTERNS.items():
        found = any(
            re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            for pattern in patterns
        )
        result["sections_found"][section_name] = found

    # Check for description in a simpler way:
    # If the README starts with text (not a heading), treat the first paragraph as a description.
    if not result["sections_found"]["description"]:
        # If there's a meaningful first paragraph (> 20 chars), count it as description
        first_paragraph = text.split("\n\n")[0].strip()
        # Remove heading markers
        first_clean = re.sub(r"^#+\s*", "", first_paragraph)
        if len(first_clean) > 20:
            result["sections_found"]["description"] = True

    # --- Code blocks ---
    if "```" in text or "    " in text:
        result["has_code_blocks"] = True
        result["strengths"].append("Includes code examples")

    # --- Generate issues for missing sections ---
    if not result["sections_found"].get("description"):
        result["issues"].append("No clear project description found")
    if not result["sections_found"].get("installation"):
        result["issues"].append("Missing installation/setup instructions")
    if not result["sections_found"].get("usage"):
        result["issues"].append("Missing usage examples or instructions")
    if not result["sections_found"].get("screenshots"):
        result["issues"].append("No screenshots or demo images — visuals help a lot")

    # --- Strengths for found sections ---
    if result["sections_found"].get("description"):
        result["strengths"].append("Has a clear project description")
    if result["sections_found"].get("installation"):
        result["strengths"].append("Includes installation instructions")
    if result["sections_found"].get("usage"):
        result["strengths"].append("Includes usage instructions")
    if result["sections_found"].get("contributing"):
        result["strengths"].append("Has contributing guidelines")
    if result["sections_found"].get("screenshots"):
        result["strengths"].append("Includes screenshots or demo visuals")

    # --- Calculate score (out of 25) ---
    score = 0.0

    # Existence: 5 points
    score += 5.0

    # Length: up to 5 points
    if len(words) >= 200:
        score += 5.0
    elif len(words) >= 100:
        score += 3.5
    elif len(words) >= 50:
        score += 2.0
    else:
        score += 1.0

    # Sections: up to 10 points (2 each for 5 key sections)
    key_sections = ["description", "installation", "usage", "contributing", "screenshots"]
    sections_present = sum(1 for s in key_sections if result["sections_found"].get(s))
    score += sections_present * 2.0

    # Code blocks: 2.5 points
    if result["has_code_blocks"]:
        score += 2.5

    # License section: 2.5 points
    if result["sections_found"].get("license_section"):
        score += 2.5

    # Cap at 25
    result["score"] = min(score, 25.0)

    # --- Overall quality label ---
    if result["score"] >= 20:
        result["quality"] = "excellent"
    elif result["score"] >= 14:
        result["quality"] = "good"
    elif result["score"] >= 8:
        result["quality"] = "fair"
    else:
        result["quality"] = "poor"

    return result
