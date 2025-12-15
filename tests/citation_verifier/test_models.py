import pytest
from citation_verifier.models import (
    Verdict,
    ClaimCitation,
    SourceContent,
    VerificationResult
)


def test_verdict_enum():
    """Test Verdict enum values"""
    assert Verdict.SUPPORTED.value == "supported"
    assert Verdict.NOT_SUPPORTED.value == "not_supported"
    assert Verdict.PARTIAL.value == "partial"
    assert Verdict.INCONCLUSIVE.value == "inconclusive"
    assert Verdict.SOURCE_UNAVAILABLE.value == "source_unavailable"


def test_claim_citation_creation():
    """Test creating a ClaimCitation"""
    claim = ClaimCitation(
        claim_text="Test claim",
        citation_url="https://example.com",
        original_context="This is a test claim from example.com"
    )

    assert claim.claim_text == "Test claim"
    assert claim.citation_url == "https://example.com"
    assert claim.has_url is True


def test_claim_citation_optional_url():
    """Test ClaimCitation with optional URL"""
    claim = ClaimCitation(
        claim_text="Test claim",
        citation_ref="[1]",
        original_context="Test claim [1]"
    )

    assert claim.citation_url is None
    assert claim.citation_ref == "[1]"
    assert claim.has_url is False


def test_source_content_creation():
    """Test creating a SourceContent"""
    source = SourceContent(
        url="https://example.com",
        content="Test content",
        fetch_status="success"
    )

    assert source.url == "https://example.com"
    assert source.content == "Test content"
    assert source.fetch_status == "success"


def test_source_content_defaults():
    """Test SourceContent default values"""
    source = SourceContent(url="https://example.com")

    assert source.content is None
    assert source.fetch_status == "pending"


def test_verification_result_creation():
    """Test creating a VerificationResult"""
    claim = ClaimCitation(
        claim_text="Test claim",
        citation_url="https://example.com",
        original_context="Test context"
    )

    result = VerificationResult(
        claim=claim,
        verdict=Verdict.SUPPORTED,
        confidence=0.95,
        explanation="The source supports the claim"
    )

    assert result.claim == claim
    assert result.verdict == Verdict.SUPPORTED
    assert result.confidence == 0.95
    assert result.explanation == "The source supports the claim"
    assert result.source_quote is None


def test_verification_result_confidence_validation():
    """Test that confidence is validated between 0 and 1"""
    claim = ClaimCitation(
        claim_text="Test",
        original_context="Test"
    )

    # Valid confidence
    result = VerificationResult(
        claim=claim,
        verdict=Verdict.SUPPORTED,
        confidence=0.5,
        explanation="Test"
    )
    assert result.confidence == 0.5

    # Invalid confidence > 1
    with pytest.raises(Exception):  # Pydantic ValidationError
        VerificationResult(
            claim=claim,
            verdict=Verdict.SUPPORTED,
            confidence=1.5,
            explanation="Test"
        )

    # Invalid confidence < 0
    with pytest.raises(Exception):  # Pydantic ValidationError
        VerificationResult(
            claim=claim,
            verdict=Verdict.SUPPORTED,
            confidence=-0.5,
            explanation="Test"
        )
