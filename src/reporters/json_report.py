"""JSON reporter for verification results."""
import json
from typing import List


def generate_json_report(results: List) -> dict:
    """Generate a JSON report from verification results.
    
    Args:
        results: List of VerificationResult objects
        
    Returns:
        Dictionary with summary and detailed results
    """
    # Calculate summary
    verdict_counts = {}
    for result in results:
        key = result.verdict.value
        verdict_counts[key] = verdict_counts.get(key, 0) + 1

    return {
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


def format_json_report(results: List) -> str:
    """Format verification results as JSON string.
    
    Args:
        results: List of VerificationResult objects
        
    Returns:
        JSON-formatted string
    """
    report = generate_json_report(results)
    return json.dumps(report, indent=2)
