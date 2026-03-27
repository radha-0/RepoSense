"""
structure.py — Analyze repository file structure and best practices.

Checks for:
  - .gitignore presence
  - LICENSE file presence
  - Dependency file (requirements.txt, package.json, Cargo.toml, etc.)
  - Number of files and directories
  - Project organization quality
"""


# Common dependency/manifest files across languages
DEPENDENCY_FILES = {
    "requirements.txt",
    "setup.py",
    "setup.cfg",
    "pyproject.toml",
    "Pipfile",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "Gemfile",
    "composer.json",
}

# Files that indicate good project hygiene
BEST_PRACTICE_FILES = {
    ".gitignore",
    ".editorconfig",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "CHANGELOG.md",
    ".github",
}


def analyze_structure(contents: list[dict] | None) -> dict:
    """
    Analyze the root-level file structure of a repository.

    Args:
        contents: List of file/dir dicts from the GitHub API, each with
                  keys: name, type ('file' or 'dir'), size.
                  Or None if contents couldn't be fetched.

    Returns:
        A dict containing:
            total_files (int): Count of root-level files.
            total_dirs (int): Count of root-level directories.
            has_gitignore (bool)
            has_license (bool)
            has_dependency_file (bool)
            dependency_file_name (str|None): Name of the detected dependency file.
            best_practice_files (list[str]): Which best-practice files were found.
            score (float): Structure score out of 20.
            issues (list[str]): Problems found.
            strengths (list[str]): Positive findings.
    """
    result = {
        "total_files": 0,
        "total_dirs": 0,
        "has_gitignore": False,
        "has_license": False,
        "has_dependency_file": False,
        "dependency_file_name": None,
        "best_practice_files": [],
        "score": 0.0,
        "issues": [],
        "strengths": [],
    }

    if not contents:
        result["issues"].append("Could not fetch repository contents")
        return result

    # --- Count files and directories ---
    file_names = set()
    for item in contents:
        name = item.get("name", "")
        item_type = item.get("type", "")
        file_names.add(name.lower())

        if item_type == "file":
            result["total_files"] += 1
        elif item_type == "dir":
            result["total_dirs"] += 1

    # --- Check for .gitignore ---
    if ".gitignore" in file_names:
        result["has_gitignore"] = True
        result["strengths"].append(".gitignore is present")
    else:
        result["issues"].append("Missing .gitignore — tracked files may include junk")

    # --- Check for LICENSE ---
    license_variants = {"license", "license.md", "license.txt", "licence", "licence.md"}
    if file_names & license_variants:
        result["has_license"] = True
        result["strengths"].append("LICENSE file is present")
    else:
        result["issues"].append("No LICENSE file — this reduces credibility for recruiters")

    # --- Check for dependency/manifest file ---
    for item in contents:
        name = item.get("name", "")
        if name in DEPENDENCY_FILES:
            result["has_dependency_file"] = True
            result["dependency_file_name"] = name
            result["strengths"].append(f"Dependency file found: {name}")
            break

    if not result["has_dependency_file"]:
        result["issues"].append(
            "No dependency file (e.g., requirements.txt, package.json) — "
            "makes it hard for others to set up your project"
        )

    # --- Check for best-practice files ---
    for item in contents:
        name = item.get("name", "")
        if name in BEST_PRACTICE_FILES or name.lower() in {f.lower() for f in BEST_PRACTICE_FILES}:
            result["best_practice_files"].append(name)

    if len(result["best_practice_files"]) >= 2:
        result["strengths"].append("Multiple best-practice files present")

    # --- Evaluate directory organization ---
    if result["total_dirs"] >= 2:
        result["strengths"].append("Code is organized into directories")
    elif result["total_files"] > 5 and result["total_dirs"] == 0:
        result["issues"].append(
            "All files are at root level — consider organizing into folders"
        )

    # --- Calculate score (out of 20) ---
    score = 0.0

    # .gitignore: 5 points
    if result["has_gitignore"]:
        score += 5.0

    # LICENSE: 5 points
    if result["has_license"]:
        score += 5.0

    # Dependency file: 4 points
    if result["has_dependency_file"]:
        score += 4.0

    # Directory structure: 3 points
    if result["total_dirs"] >= 2:
        score += 3.0
    elif result["total_dirs"] >= 1:
        score += 1.5

    # Bonus best-practice files: up to 3 points
    bonus = min(len(result["best_practice_files"]), 3)
    score += bonus

    result["score"] = min(score, 20.0)
    return result


def analyze_best_practices(metadata: dict, structure_result: dict) -> dict:
    """
    Evaluate repository best practices beyond basic structure.

    Args:
        metadata: Repo metadata from github_api.fetch_repo_metadata().
        structure_result: Result from analyze_structure().

    Returns:
        A dict with:
            score (float): Best practices score out of 25.
            issues (list[str])
            strengths (list[str])
    """
    result = {
        "score": 0.0,
        "issues": [],
        "strengths": [],
    }

    score = 0.0

    # Description: 5 points
    description = metadata.get("description", "")
    if description and len(description) > 10:
        score += 5.0
        result["strengths"].append("Repository has a clear description")
    else:
        result["issues"].append("Add a repository description on GitHub")

    # Topics/tags: 4 points
    topics = metadata.get("topics", [])
    if len(topics) >= 3:
        score += 4.0
        result["strengths"].append(f"Good use of topics/tags ({len(topics)} topics)")
    elif len(topics) >= 1:
        score += 2.0
        result["issues"].append("Add more topic tags to improve discoverability")
    else:
        result["issues"].append("No topic tags — add them for better discoverability")

    # License via API: 4 points
    if metadata.get("license"):
        score += 4.0
        result["strengths"].append(f"License: {metadata['license']}")
    elif not structure_result.get("has_license"):
        result["issues"].append("Choose and add an open source license")

    # Language detected: 3 points
    if metadata.get("language") and metadata["language"] != "Unknown":
        score += 3.0
        result["strengths"].append(f"Primary language: {metadata['language']}")

    # .gitignore: 3 points (counted here too for best practices weight)
    if structure_result.get("has_gitignore"):
        score += 3.0

    # Dependency file: 3 points
    if structure_result.get("has_dependency_file"):
        score += 3.0

    result["score"] = min(score, 25.0)
    return result
