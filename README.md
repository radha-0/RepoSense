# 🔍 RepoSense

**See your GitHub repo like a recruiter sees it.**

RepoSense is a smart CLI tool that analyzes any public GitHub repository and gives you a quality score (0–100), a letter grade, and actionable suggestions to improve your project's presentation.

Built for students, hackathon participants, and anyone who wants their GitHub profile to stand out.

---

## ✨ Features

- **Repository Scoring** — Get a score out of 100 with a letter grade (A–F)
- **README Analysis** — Checks for key sections (description, installation, usage, screenshots)
- **Structure Checks** — Detects `.gitignore`, LICENSE, dependency files, directory organization
- **Activity Analysis** — Evaluates commit frequency and recency
- **Best Practices** — Checks for repo description, topics, and license
- **Actionable Suggestions** — Prioritized recommendations to improve your repo
- **Beautiful CLI Output** — Color-coded panels, progress bars, and clean formatting

---

## 🚀 Quick Start

### 1. Clone & setup

```bash
git clone <your-repo-url>
cd repo_analyzer
python -m venv venv
source venv/bin/activate      # Linux/macOS
# venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

### 2. Run

```bash
python main.py <github_repo_url>
```

### Examples

```bash
python main.py https://github.com/pallets/flask
python main.py pallets/flask
python main.py github.com/torvalds/linux
```

---

## 🔑 GitHub Token (Optional)

To avoid API rate limits (60 requests/hour without auth), set a personal access token:

```bash
export GITHUB_TOKEN=your_personal_access_token
```

You can generate one at: [github.com/settings/tokens](https://github.com/settings/tokens) — no special scopes needed for public repos.

---

## 📊 Scoring System

| Category        | Weight | What it checks                                    |
|-----------------|--------|---------------------------------------------------|
| README Quality  | 25%    | Existence, length, sections, code blocks          |
| Best Practices  | 25%    | Description, topics, license, gitignore, deps     |
| Activity        | 20%    | Commit count, recency of updates                  |
| Structure       | 20%    | File organization, essential files                |
| Popularity      | 10%    | Stars and forks                                   |

### Grades

| Grade | Score Range |
|-------|-------------|
| A     | 80–100      |
| B     | 60–79       |
| C     | 40–59       |
| D     | 20–39       |
| F     | 0–19        |

---

## 📁 Project Structure

```
repo_analyzer/
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
├── README.md
├── analyzer/
│   ├── __init__.py
│   ├── github_api.py        # GitHub API client
│   ├── readme_checker.py    # README analysis
│   ├── structure.py         # File structure checks
│   ├── scoring.py           # Score calculation
│   └── suggestions.py       # Suggestion engine
├── utils/
│   ├── __init__.py
│   └── parser.py            # URL parsing
└── output/
    ├── __init__.py
    └── formatter.py          # Rich CLI display
```

---

## 🛠️ Tech Stack

- **Python 3.x**
- **requests** — GitHub REST API
- **rich** — Terminal UI

---

## 📜 License

MIT — use it, share it, improve it.
