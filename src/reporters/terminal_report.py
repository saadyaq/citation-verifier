"""Terminal reporter with Rich formatting for verification results."""
from typing import List
from rich.console import Console
from rich.table import Table


def verdict_color(verdict) -> str:
    """Return color for verdict display."""
    from citation_verifier.models import Verdict
    
    colors = {
        Verdict.SUPPORTED: "green",
        Verdict.NOT_SUPPORTED: "red",
        Verdict.PARTIAL: "yellow",
        Verdict.INCONCLUSIVE: "blue",
        Verdict.SOURCE_UNAVAILABLE: "grey50",
    }
    return colors.get(verdict, "white")


def verdict_symbol(verdict) -> str:
    """Return symbol for verdict."""
    from citation_verifier.models import Verdict
    
    symbols = {
        Verdict.SUPPORTED: "[+]",
        Verdict.NOT_SUPPORTED: "[X]",
        Verdict.PARTIAL: "[!]",
        Verdict.INCONCLUSIVE: "[?]",
        Verdict.SOURCE_UNAVAILABLE: "[-]",
    }
    return symbols.get(verdict, "[ ]")


def display_terminal_report(results: List, console: Console = None):
    """Display results in terminal with Rich formatting.
    
    Args:
        results: List of VerificationResult objects
        console: Rich Console object (creates new one if not provided)
    """
    if console is None:
        console = Console()
        
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
