import pytest
from extractors.claim_extractor import extract_claims
from citation_verifier.models import ClaimCitation


@pytest.mark.api
async def test_extract_claims_basic():
    """Test extracting claims from a simple document"""
    document = """
    # AI Report

    According to a McKinsey study, 85% of companies use AI [1].

    [1]: https://www.mckinsey.com/ai-report
    """

    claims = extract_claims(document)

    assert len(claims) > 0
    assert isinstance(claims[0], ClaimCitation)
    assert "85%" in claims[0].claim_text or "companies" in claims[0].claim_text


def test_extract_claims_empty_document():
    """Test extracting claims from an empty document"""
    # Note: This might still call the API, which could return empty results
    # In a real test suite, you'd mock the Anthropic client
    pytest.skip("Requires mocking the Anthropic API")


def test_extract_claims_no_citations():
    """Test document with no citations"""
    document = "This is a document with no citations."

    # This would require mocking to avoid API calls
    pytest.skip("Requires mocking the Anthropic API")
