#!/usr/bin/env python3
"""
RepoSense — A smart GitHub repository analyzer for students.

Usage:
    python main.py <github_repo_url>
    python main.py owner/repo
    python main.py https://github.com/owner/repo

Set GITHUB_TOKEN environment variable to avoid rate limits:
    export GITHUB_TOKEN=your_personal_access_token
"""

import sys

from rich.console import Console
from rich.panel import Panel
from rich import box

from utils.parser import parse_github_url
from analyzer.github_api import fetch_repo_metadata, fetch_commits, fetch_readme, fetch_repo_contents
from analyzer.readme_checker import analyze_readme
from analyzer.structure import analyze_structure, analyze_best_practices
from analyzer.scoring import calculate_activity_score, calculate_popularity_score, calculate_total_score
from analyzer.suggestions import generate_suggestions
from output.formatter import display_results


console = Console()


def show_banner() -> None:
    """Display the RepoSense ASCII banner."""
    banner = """
[bold cyan]
  ██████╗ ███████╗██████╗  ██████╗ ███████╗███████╗███╗   ██╗███████╗███████╗
  ██╔══██╗██╔════╝██╔══██╗██╔═══██╗██╔════╝██╔════╝████╗  ██║██╔════╝██╔════╝
  ██████╔╝█████╗  ██████╔╝██║   ██║███████╗█████╗  ██╔██╗ ██║███████╗█████╗
  ██╔══██╗██╔══╝  ██╔═══╝ ██║   ██║╚════██║██╔══╝  ██║╚██╗██║╚════██║██╔══╝
  ██║  ██║███████╗██║     ╚██████╔╝███████║███████╗██║ ╚████║███████║███████╗
  ╚═╝  ╚═╝╚══════╝╚═╝      ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═══╝╚══════╝╚══════╝
[/bold cyan]
[dim]  See your repo like a recruiter sees it.[/dim]
"""
    console.print(banner)


def main() -> None:
    """Main entry point — orchestrate the full analysis pipeline."""

    show_banner()

    # --- Parse CLI argument ---
    if len(sys.argv) < 2:
        console.print(
            Panel(
                "[bold]Usage:[/bold]\n"
                "  python main.py [cyan]<github_repo_url>[/cyan]\n\n"
                "[bold]Examples:[/bold]\n"
                "  python main.py https://github.com/torvalds/linux\n"
                "  python main.py pallets/flask\n"
                "  python main.py github.com/user/repo\n\n"
                "[bold]Tip:[/bold]\n"
                "  Set [cyan]GITHUB_TOKEN[/cyan] env var for higher API limits.",
                title="[bold red]No repository URL provided[/bold red]",
                border_style="red",
                box=box.ROUNDED,
            )
        )
        sys.exit(1)

    repo_input = sys.argv[1]

    # --- Parse owner/repo ---
    try:
        owner, repo = parse_github_url(repo_input)
    except ValueError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        sys.exit(1)

    console.print(f"  [dim]Analyzing:[/dim] [bold cyan]{owner}/{repo}[/bold cyan]\n")

    # --- Fetch data from GitHub API ---
    with console.status("[bold cyan]Fetching repository data from GitHub...[/bold cyan]", spinner="dots"):
        try:
            # 1. Metadata
            metadata = fetch_repo_metadata(owner, repo)
        except FileNotFoundError:
            console.print(
                f"\n[bold red]❌ Repository '{owner}/{repo}' not found.[/bold red]\n"
                "[dim]Double-check the URL and make sure the repo is public.[/dim]\n"
            )
            sys.exit(1)
        except ConnectionError as e:
            console.print(f"\n[bold red]❌ API Error:[/bold red] {e}\n")
            sys.exit(1)
        except Exception as e:
            console.print(f"\n[bold red]❌ Unexpected error:[/bold red] {e}\n")
            sys.exit(1)

        try:
            # 2. Commits
            commits = fetch_commits(owner, repo)
        except Exception:
            commits = []

        try:
            # 3. README
            readme_content = fetch_readme(owner, repo)
        except Exception:
            readme_content = None

        try:
            # 4. File tree
            contents = fetch_repo_contents(owner, repo)
        except Exception:
            contents = None

    console.print("  [green]✓[/green] Data fetched successfully\n")

    # --- Run analysis ---
    with console.status("[bold cyan]Analyzing repository...[/bold cyan]", spinner="dots"):
        # README analysis
        readme_result = analyze_readme(readme_content)

        # Structure analysis
        structure_result = analyze_structure(contents)

        # Best practices analysis
        best_practices_result = analyze_best_practices(metadata, structure_result)

        # Activity scoring
        activity_result = calculate_activity_score(commits, metadata)

        # Popularity scoring
        popularity_result = calculate_popularity_score(metadata)

        # Total score
        score_result = calculate_total_score(
            readme_score=readme_result["score"],
            activity_score=activity_result["score"],
            structure_score=structure_result["score"],
            popularity_score=popularity_result["score"],
            best_practices_score=best_practices_result["score"],
        )

        # Suggestions
        suggestions_result = generate_suggestions(
            readme_result=readme_result,
            structure_result=structure_result,
            activity_result=activity_result,
            popularity_result=popularity_result,
            best_practices_result=best_practices_result,
        )

    console.print("  [green]✓[/green] Analysis complete\n")

    # --- Display results ---
    display_results(
        metadata=metadata,
        score_result=score_result,
        readme_result=readme_result,
        structure_result=structure_result,
        activity_result=activity_result,
        suggestions_result=suggestions_result,
    )


if __name__ == "__main__":
    main()
