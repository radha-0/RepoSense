"""
formatter.py — Beautiful CLI output using the Rich library.

Renders the analysis results with:
  - Color-coded score and grade
  - Section-wise breakdown with progress bars
  - Prioritized suggestions
  - Highlighted strengths
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box


console = Console()


# --- Color helpers ---

def _score_color(score: float, max_score: float) -> str:
    """Return a color based on the percentage of max score achieved."""
    pct = (score / max_score * 100) if max_score > 0 else 0
    if pct >= 75:
        return "green"
    elif pct >= 50:
        return "yellow"
    else:
        return "red"


def _grade_color(grade: str) -> str:
    """Return a color for the letter grade."""
    return {
        "A": "bold green",
        "B": "bold cyan",
        "C": "bold yellow",
        "D": "bold red",
        "F": "bold red",
    }.get(grade, "white")


def _grade_emoji(grade: str) -> str:
    """Return an emoji for the grade."""
    return {
        "A": "🌟",
        "B": "👍",
        "C": "⚠️ ",
        "D": "👎",
        "F": "🚨",
    }.get(grade, "")


def _priority_label(priority: int) -> str:
    """Return a colored priority label."""
    if priority == 1:
        return "[bold red]CRITICAL[/bold red]"
    elif priority == 2:
        return "[bold yellow]IMPORTANT[/bold yellow]"
    elif priority == 3:
        return "[dim cyan]SUGGESTED[/dim cyan]"
    else:
        return "[dim]MINOR[/dim]"


def _progress_bar(score: float, max_score: float, width: int = 20) -> str:
    """Create a simple text-based progress bar."""
    pct = score / max_score if max_score > 0 else 0
    filled = int(pct * width)
    empty = width - filled
    color = _score_color(score, max_score)
    bar = f"[{color}]{'█' * filled}[/{color}][dim]{'░' * empty}[/dim]"
    return bar


def _quality_label(score: float, max_score: float) -> str:
    """Return a quality label based on score percentage."""
    pct = (score / max_score * 100) if max_score > 0 else 0
    if pct >= 80:
        return "[green]Excellent[/green]"
    elif pct >= 60:
        return "[cyan]Good[/cyan]"
    elif pct >= 40:
        return "[yellow]Average[/yellow]"
    else:
        return "[red]Needs Work[/red]"


def display_results(
    metadata: dict,
    score_result: dict,
    readme_result: dict,
    structure_result: dict,
    activity_result: dict,
    suggestions_result: dict,
) -> None:
    """
    Display the full analysis results in the terminal.

    Args:
        metadata: Repo metadata dict.
        score_result: From scoring.calculate_total_score().
        readme_result: From readme_checker.analyze_readme().
        structure_result: From structure.analyze_structure().
        activity_result: From scoring.calculate_activity_score().
        suggestions_result: From suggestions.generate_suggestions().
    """
    console.print()

    # ═══════════════════════════════════════════════════════
    # HEADER
    # ═══════════════════════════════════════════════════════
    repo_name = metadata.get("full_name", "Unknown")
    description = metadata.get("description", "") or "No description"
    language = metadata.get("language", "Unknown") or "Unknown"

    header_text = Text()
    header_text.append("📦 ", style="bold")
    header_text.append(repo_name, style="bold cyan")
    header_text.append(f"\n{description}", style="dim")
    header_text.append(f"\n🔤 {language}", style="dim")

    topics = metadata.get("topics", [])
    if topics:
        header_text.append("  •  🏷️  " + ", ".join(topics), style="dim italic")

    console.print(Panel(header_text, title="[bold]RepoSense Analysis[/bold]", border_style="cyan", box=box.DOUBLE))

    # ═══════════════════════════════════════════════════════
    # OVERALL SCORE
    # ═══════════════════════════════════════════════════════
    total = score_result["total_score"]
    grade = score_result["grade"]
    grade_c = _grade_color(grade)
    emoji = _grade_emoji(grade)

    score_text = Text()
    score_text.append(f"\n  {emoji}  ", style="bold")
    score_text.append(f"{total}", style=f"bold {'green' if total >= 60 else 'yellow' if total >= 40 else 'red'} ")
    score_text.append(" / 100", style="dim")
    score_text.append("     Grade: ", style="bold")
    score_text.append(grade, style=grade_c)
    score_text.append("\n")

    console.print(Panel(score_text, title="[bold]Repository Score[/bold]", border_style="bright_white", box=box.ROUNDED))

    # ═══════════════════════════════════════════════════════
    # SCORE BREAKDOWN TABLE
    # ═══════════════════════════════════════════════════════
    breakdown = score_result["breakdown"]

    table = Table(
        title="Score Breakdown",
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold magenta",
        title_style="bold",
        padding=(0, 2),
    )
    table.add_column("Category", style="bold", width=18)
    table.add_column("Score", justify="right", width=10)
    table.add_column("Bar", width=24)
    table.add_column("Rating", justify="center", width=12)

    category_labels = {
        "readme_quality": "📝 README",
        "activity": "📊 Activity",
        "structure": "📁 Structure",
        "popularity": "⭐ Popularity",
        "best_practices": "✅ Best Practices",
    }

    for key, label in category_labels.items():
        cat = breakdown[key]
        s = cat["score"]
        m = cat["max"]
        color = _score_color(s, m)
        bar = _progress_bar(s, m)
        rating = _quality_label(s, m)
        table.add_row(label, f"[{color}]{s}[/{color}] / {m}", bar, rating)

    console.print(table)
    console.print()

    # ═══════════════════════════════════════════════════════
    # QUICK STATS
    # ═══════════════════════════════════════════════════════
    stats_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 3))
    stats_table.add_column("Label", style="dim")
    stats_table.add_column("Value", style="bold")

    stats_table.add_row("⭐ Stars", str(metadata.get("stars", 0)))
    stats_table.add_row("🍴 Forks", str(metadata.get("forks", 0)))
    stats_table.add_row("🐛 Open Issues", str(metadata.get("open_issues", 0)))
    stats_table.add_row("📝 Commits (fetched)", str(activity_result.get("total_commits", 0)))

    days = activity_result.get("days_since_update", -1)
    if days >= 0:
        if days == 0:
            recency = "Today"
        elif days == 1:
            recency = "Yesterday"
        else:
            recency = f"{days} days ago"
        stats_table.add_row("🕐 Last Updated", recency)

    stats_table.add_row("📄 Root Files", str(structure_result.get("total_files", 0)))
    stats_table.add_row("📁 Root Dirs", str(structure_result.get("total_dirs", 0)))

    freq = activity_result.get("commit_frequency", "unknown")
    freq_color = {"high": "green", "moderate": "cyan", "low": "yellow"}.get(freq, "red")
    stats_table.add_row("📈 Commit Frequency", f"[{freq_color}]{freq.capitalize()}[/{freq_color}]")

    console.print(Panel(stats_table, title="[bold]Quick Stats[/bold]", border_style="blue", box=box.ROUNDED))

    # ═══════════════════════════════════════════════════════
    # README DETAILS
    # ═══════════════════════════════════════════════════════
    readme_text = Text()
    if readme_result.get("exists"):
        readme_text.append(f"  ✅ README exists  •  ", style="green")
        readme_text.append(f"{readme_result['word_count']} words  •  ", style="dim")
        readme_text.append(f"Quality: ", style="dim")

        q = readme_result["quality"]
        q_color = {"excellent": "green", "good": "cyan", "fair": "yellow", "poor": "red"}.get(q, "white")
        readme_text.append(q.capitalize(), style=f"bold {q_color}")

        # Sections found
        sections = readme_result.get("sections_found", {})
        if sections:
            readme_text.append("\n\n  Sections: ", style="bold")
            for section, found in sections.items():
                icon = "✅" if found else "❌"
                readme_text.append(f"  {icon} {section.replace('_', ' ').title()}", style="dim")
    else:
        readme_text.append("  ❌ No README found", style="bold red")

    console.print(Panel(readme_text, title="[bold]README Analysis[/bold]", border_style="magenta", box=box.ROUNDED))

    # ═══════════════════════════════════════════════════════
    # SUGGESTIONS (prioritized)
    # ═══════════════════════════════════════════════════════
    suggestions = suggestions_result.get("suggestions", [])
    if suggestions:
        sugg_table = Table(
            box=box.SIMPLE,
            show_header=True,
            header_style="bold red",
            padding=(0, 1),
        )
        sugg_table.add_column("#", style="dim", width=3)
        sugg_table.add_column("Priority", width=12)
        sugg_table.add_column("Suggestion", style="white")

        for i, s in enumerate(suggestions, 1):
            sugg_table.add_row(str(i), _priority_label(s["priority"]), s["text"])

        console.print(Panel(
            sugg_table,
            title="[bold]💡 Suggestions for Improvement[/bold]",
            border_style="yellow",
            box=box.ROUNDED,
        ))
    else:
        console.print(Panel(
            "[bold green]No issues found — your repo is in great shape! 🎉[/bold green]",
            title="[bold]💡 Suggestions[/bold]",
            border_style="green",
            box=box.ROUNDED,
        ))

    # ═══════════════════════════════════════════════════════
    # STRENGTHS
    # ═══════════════════════════════════════════════════════
    strengths = suggestions_result.get("strengths", [])
    if strengths:
        strengths_text = Text()
        for s in strengths:
            strengths_text.append(f"  ✅ {s}\n", style="green")

        console.print(Panel(
            strengths_text,
            title="[bold]🏆 Strengths[/bold]",
            border_style="green",
            box=box.ROUNDED,
        ))

    # ═══════════════════════════════════════════════════════
    # FOOTER
    # ═══════════════════════════════════════════════════════
    top = suggestions_result.get("top_priority", "")
    if suggestions:
        console.print(
            f"\n  [bold yellow]🎯 Top Priority:[/bold yellow] [white]{top}[/white]\n"
        )

    console.print(
        "[dim]  Powered by RepoSense — See your repo like a recruiter sees it.[/dim]\n"
    )
