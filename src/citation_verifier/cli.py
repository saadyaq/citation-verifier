"""Citation Verifier CLI interface."""
import asyncio
import sys
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

from .main import verify_document
from .models import Verdict

load_dotenv()

app = typer.Typer(
    name="cite-verify",
    help="AI-powered citation verification tool. Stop AI hallucinations by verifying every citation.",
    add_completion=False,
)

console = Console()


def verdict_color(verdict: Verdict) -> str:
    """Return color for verdict display."""
    colors = {
        Verdict.SUPPORTED: "green",
        Verdict.NOT_SUPPORTED: "red",
        Verdict.PARTIAL: "yellow",
        Verdict.INCONCLUSIVE: "blue",
        Verdict.SOURCE_UNAVAILABLE: "grey50",
    }
    return colors.get(verdict, "white")


def verdict_symbol(verdict: Verdict) -> str:
    """Return symbol for verdict."""
    symbols = {
        Verdict.SUPPORTED: "[+]",
        Verdict.NOT_SUPPORTED: "[X]",
        Verdict.PARTIAL: "[!]",
        Verdict.INCONCLUSIVE: "[?]",
        Verdict.SOURCE_UNAVAILABLE: "[-]",
    }
    return symbols.get(verdict, "[ ]")


@app.command()
def check(
    source: str = typer.Argument(
        ...,
        help="Path to document (.md, .pdf, .html) or URL to verify"
    ),
    output_format: str = typer.Option(
        "terminal",
        "--output",
        "-o",
        help="Output format: terminal, json, markdown"
    ),
    model: str = typer.Option(
        "claude-3-5-haiku-20241022",
        "--model",
        "-m",
        help="LLM model to use for verification"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed progress"
    ),
):
    """Verify citations in a document."""

    # Validate source
    if not source.startswith(("http://", "https://")):
        path = Path(source)
        if not path.exists():
            console.print(f"[red]Error: File not found: {source}[/red]")
            raise typer.Exit(1)

    # Run verification
    try:
        results = asyncio.run(_verify_with_progress(source, verbose))
    except KeyboardInterrupt:
        console.print("\n[yellow]Verification cancelled by user[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)

    # Display results
    if output_format == "terminal":
        display_terminal_results(results)
    elif output_format == "json":
        display_json_results(results)
    elif output_format == "markdown":
        display_markdown_results(results)
    else:
        console.print(f"[red]Unknown output format: {output_format}[/red]")
        raise typer.Exit(1)


async def _verify_with_progress(source: str, verbose: bool) -> list:
    """Run verification with progress display."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=not verbose,
    ) as progress:
        task = progress.add_task(f"Verifying citations in {source}...", total=None)
        results = await verify_document(source)
        progress.update(task, completed=True)

    return results


def display_terminal_results(results: list):
    """Display results in terminal with Rich formatting."""
    if not results:
        console.print("[yellow]No verifiable citations found.[/yellow]")
        return

    # Summary
    console.print("\n[bold]Verification Summary[/bold]\n")

    verdict_counts = {}
    for result in results:
        verdict_counts[result.verdict] = verdict_counts.get(result.verdict, 0) + 1

    summary_table = Table(show_header=False, box=None)
    summary_table.add_column("Metric", style="bold")
    summary_table.add_column("Count", justify="right")

    summary_table.add_row("Total Citations", str(len(results)))
    for verdict, count in verdict_counts.items():
        color = verdict_color(verdict)
        symbol = verdict_symbol(verdict)
        summary_table.add_row(
            f"{symbol} {verdict.value.replace('_', ' ').title()}",
            f"[{color}]{count}[/{color}]"
        )

    console.print(summary_table)

    # Detailed results
    console.print("\n[bold]Detailed Results[/bold]\n")

    for i, result in enumerate(results, 1):
        color = verdict_color(result.verdict)
        symbol = verdict_symbol(result.verdict)

        console.print(f"[bold]{i}. {symbol} {result.verdict.value.upper()}[/bold] "
                     f"(confidence: {result.confidence:.0%})")

        console.print(f"   [dim]Claim:[/dim] {result.claim.claim_text}")

        if hasattr(result.claim, 'citation_url') and result.claim.citation_url:
            console.print(f"   [dim]Source:[/dim] {result.claim.citation_url}")

        console.print(f"   [dim]Explanation:[/dim] {result.explanation}")

        if result.source_quote:
            console.print(f"   [dim]Quote:[/dim] [italic]\"{result.source_quote}\"[/italic]")

        console.print()


def display_json_results(results: list):
    """Display results as JSON."""
    # Calculate summary
    verdict_counts = {}
    for result in results:
        key = result.verdict.value
        verdict_counts[key] = verdict_counts.get(key, 0) + 1

    output = {
        "summary": {
            "total_citations": len(results),
            **verdict_counts
        },
        "results": [
            {
                "claim": result.claim.claim_text,
                "source_url": getattr(result.claim, 'citation_url', None),
                "verdict": result.verdict.value,
                "confidence": result.confidence,
                "explanation": result.explanation,
                "source_quote": result.source_quote,
            }
            for result in results
        ]
    }

    console.print(json.dumps(output, indent=2))


def display_markdown_results(results: list):
    """Display results as Markdown."""
    if not results:
        print("No verifiable citations found.")
        return

    # Summary
    print("# Citation Verification Report\n")
    print("## Summary\n")

    verdict_counts = {}
    for result in results:
        verdict_counts[result.verdict] = verdict_counts.get(result.verdict, 0) + 1

    print(f"- **Total Citations**: {len(results)}")
    for verdict, count in verdict_counts.items():
        symbol = verdict_symbol(verdict)
        print(f"- {symbol} **{verdict.value.replace('_', ' ').title()}**: {count}")

    # Detailed results
    print("\n## Detailed Results\n")

    for i, result in enumerate(results, 1):
        symbol = verdict_symbol(result.verdict)
        print(f"### {i}. {symbol} {result.verdict.value.upper()}")
        print(f"\n**Confidence**: {result.confidence:.0%}\n")
        print(f"**Claim**: {result.claim.claim_text}\n")

        if hasattr(result.claim, 'citation_url') and result.claim.citation_url:
            print(f"**Source**: {result.claim.citation_url}\n")

        print(f"**Explanation**: {result.explanation}\n")

        if result.source_quote:
            print(f"**Quote**: \"{result.source_quote}\"\n")

        print("---\n")


@app.command()
def version():
    """Show version information."""
    console.print("[bold]Citation Verifier[/bold] v0.1.0")
    console.print("AI-powered citation verification tool")


def main():
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
