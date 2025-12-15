import pytest
from parsers.html_parser import parse_url, parse_html_file


@pytest.mark.asyncio
async def test_parse_url_wikipedia():
    """Test parsing a Wikipedia URL"""
    # Note: This test makes a real HTTP request
    page = parse_url('https://en.wikipedia.org/wiki/Python_(programming_language)')

    assert page.fetch_status == "success"
    assert page.title is not None
    assert len(page.text) > 0
    assert "Python" in page.text


def test_parse_html_file_not_found():
    """Test that FileNotFoundError is raised for non-existent HTML file"""
    with pytest.raises(FileNotFoundError):
        parse_html_file("nonexistent_file.html")
