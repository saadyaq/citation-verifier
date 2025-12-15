import pytest
from pathlib import Path
from parsers.markdown import parse_document, resolve_references
from citation_verifier.models import ClaimCitation


def test_parse_markdown_basic():
    """Test parsing a basic markdown file"""
    # Create a temporary markdown file
    test_content = """# Test Document

This is a test with a reference [1].

[1]: https://example.com
"""
    test_file = Path("test_temp.md")
    test_file.write_text(test_content)

    try:
        doc = parse_document(str(test_file))

        assert doc.text == test_content
        assert "[1]" in doc.references
        assert doc.references["[1]"] == "https://example.com"
        assert doc.source_path == str(test_file.absolute())
    finally:
        test_file.unlink()


def test_parse_markdown_file_not_found():
    """Test that FileNotFoundError is raised for non-existent file"""
    with pytest.raises(FileNotFoundError):
        parse_document("nonexistent_file.md")


def test_resolve_references():
    """Test resolving citation references to URLs"""
    claims = [
        ClaimCitation(
            claim_text="Test claim",
            citation_ref="[1]",
            citation_url=None,
            original_context="Test claim [1]"
        )
    ]

    references = {"[1]": "https://example.com"}

    resolved = resolve_references(claims, references)

    assert resolved[0].citation_url == "https://example.com"


def test_resolve_references_no_brackets():
    """Test resolving references without brackets"""
    claims = [
        ClaimCitation(
            claim_text="Test claim",
            citation_ref="1",
            citation_url=None,
            original_context="Test claim [1]"
        )
    ]

    references = {"[1]": "https://example.com"}

    resolved = resolve_references(claims, references)

    assert resolved[0].citation_url == "https://example.com"
