import pytest
from citation_verifier.fetcher import fetch_source


@pytest.mark.asyncio
async def test_fetch_source_valid_url():
    """Test fetching a valid URL"""
    result = await fetch_source("https://httpbin.org/html")

    assert result.fetch_status == "success"
    assert result.content is not None
    assert len(result.content) > 0


@pytest.mark.asyncio
async def test_fetch_source_invalid_url():
    """Test fetching with invalid URL scheme"""
    result = await fetch_source("ftp://example.com")

    assert result.fetch_status == "error: invalid_url_scheme"
    assert result.content is None


@pytest.mark.asyncio
async def test_fetch_source_404():
    """Test fetching a non-existent page"""
    result = await fetch_source("https://httpbin.org/status/404")

    assert result.fetch_status == "not_found"
    assert result.content is None


@pytest.mark.asyncio
async def test_fetch_source_timeout():
    """Test fetch with very short timeout"""
    result = await fetch_source("https://httpbin.org/delay/10", timeout=1)

    assert result.fetch_status == "timeout"


@pytest.mark.asyncio
async def test_fetch_source_max_size():
    """Test that content size limit works"""
    # httpbin.org/bytes/N returns N random bytes
    result = await fetch_source(
        "https://httpbin.org/bytes/1048576",  # 1MB
        max_size_mb=0.5  # Limit to 0.5MB
    )

    assert "content_too_large" in result.fetch_status
