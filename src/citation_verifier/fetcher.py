import httpx    
from .models import SourceContent

async def fetch_source(url: str, timeout: int = 30, max_size_mb: int = 10) -> SourceContent:
    """Get the content of an url

    Args:
        url: The URL to fetch
        timeout: Timeout in seconds (default: 30)
        max_size_mb: Maximum content size in MB (default: 10)
    """
    try:
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            return SourceContent(url=url, fetch_status="error: invalid_url_scheme")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                timeout=timeout,
                follow_redirects=True,
                headers={
                    "User-Agent": "CitationVerifier/0.1"
                }
            )

            if response.status_code == 200:
                # Check content size
                content_length = len(response.content)
                max_size_bytes = max_size_mb * 1024 * 1024

                if content_length > max_size_bytes:
                    return SourceContent(
                        url=url,
                        fetch_status=f"error: content_too_large ({content_length / 1024 / 1024:.1f}MB)"
                    )

                return SourceContent(
                    url=url,
                    content=response.text,
                    fetch_status="success"
                )

            elif response.status_code == 403:
                return SourceContent(
                    url=url,
                    fetch_status="access_denied"
                )

            elif response.status_code == 404:
                return SourceContent(
                    url=url,
                    fetch_status="not_found"
                )

            else:
                return SourceContent(
                    url=url,
                    fetch_status=f"failed_{response.status_code}"
                )

    except httpx.TimeoutException:
        return SourceContent(url=url, fetch_status="timeout")
    except httpx.InvalidURL:
        return SourceContent(url=url, fetch_status="error: invalid_url")
    except Exception as e:
        return SourceContent(url=url, fetch_status=f"error: {str(e)}")