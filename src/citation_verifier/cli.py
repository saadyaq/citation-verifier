"""Citation Verifier CLI interface."""
import asyncio
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

from .main import verify_document
from reporters.json_report import format_json_report
from reporters.markdown_report import format_markdown_report
from reporters.terminal_report import display_terminal_report

load_dotenv()

app = typer.Typer(
    name="cite-verify",
    help="AI-powered citation verification tool. Stop AI hallucinations by verifying every citation.",
    add_completion=False,
)

console = Console()


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
    no_rag: bool = typer.Option(
        False,
        "--no-rag",
        help="Disable RAG (Retrieval-Augmented Generation) for long documents. Use this on systems with limited memory."
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
        results = asyncio.run(_verify_with_progress(source, verbose, use_rag=not no_rag))
    except KeyboardInterrupt:
        console.print("\n[yellow]Verification cancelled by user[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)

    # Display results using appropriate reporter
    if output_format == "terminal":
        display_terminal_report(results, console)
    elif output_format == "json":
        console.print(format_json_report(results))
    elif output_format == "markdown":
        print(format_markdown_report(results))
    else:
        console.print(f"[red]Unknown output format: {output_format}[/red]")
        raise typer.Exit(1)


async def _verify_with_progress(source: str, verbose: bool, use_rag: bool = True) -> list:
    """Run verification with progress display."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=not verbose,
    ) as progress:
        task = progress.add_task(f"Verifying citations in {source}...", total=None)
        results = await verify_document(source, use_rag=use_rag)
        progress.update(task, completed=True)

    return results


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
