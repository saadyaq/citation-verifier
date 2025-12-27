"""Markdown reporter for verification results."""
from typing import List


def verdict_symbol(verdict) -> str:
    """Return symbol for verdict."""
    symbols = {
        "supported": "[+]",
        "not_supported": "[X]",
        "partial": "[!]",
        "inconclusive": "[?]",
        "source_unavailable": "[-]",
    }
    return symbols.get(verdict.value if hasattr(verdict, 'value') else verdict, "[ ]")


def format_markdown_report(results: List) -> str:
    """Format verification results as Markdown.
    
    Args:
        results: List of VerificationResult objects
        
    Returns:
        Markdown-formatted string
    """
    if not results:
        return "No verifiable citations found."

    lines = []
    
    # Header
    lines.append("# Citation Verification Report\n")
    lines.append("## Summary\n")

    # Summary stats
    verdict_counts = {}
    for result in results:
        verdict_counts[result.verdict] = verdict_counts.get(result.verdict, 0) + 1

    lines.append(f"- **Total Citations**: {len(results)}")
    for verdict, count in verdict_counts.items():
        symbol = verdict_symbol(verdict)
        lines.append(f"- {symbol} **{verdict.value.replace('_', ' ').title()}**: {count}")

    # Detailed results
    lines.append("\n## Detailed Results\n")

    for i, result in enumerate(results, 1):
        symbol = verdict_symbol(result.verdict)
        lines.append(f"### {i}. {symbol} {result.verdict.value.upper()}")
        lines.append(f"\n**Confidence**: {result.confidence:.0%}\n")
        lines.append(f"**Claim**: {result.claim.claim_text}\n")

        if hasattr(result.claim, 'citation_url') and result.claim.citation_url:
            lines.append(f"**Source**: {result.claim.citation_url}\n")

        lines.append(f"**Explanation**: {result.explanation}\n")

        if result.source_quote:
            lines.append(f"**Quote**: \"{result.source_quote}\"\n")

        lines.append("---\n")

    return "\n".join(lines)
