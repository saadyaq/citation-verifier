import pytest
from pathlib import Path
from parsers.pdf import parse_pdf


def test_parse_pdf_file_not_found():
    """Test that FileNotFoundError is raised for non-existent PDF"""
    with pytest.raises(FileNotFoundError):
        parse_pdf("nonexistent_file.pdf")


def test_parse_pdf_structure():
    """Test that parse_pdf returns correct structure"""
    # This test requires a real PDF file
    # For now, we just test the structure with a mock
    pytest.skip("Requires a test PDF file")


def test_parse_pdf_extracts_references():
    """Test that PDF parsing extracts reference patterns"""
    # This would require a test PDF with references
    pytest.skip("Requires a test PDF file with references")
