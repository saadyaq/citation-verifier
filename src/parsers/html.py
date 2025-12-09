import httpx
import trafilatura
from dataclasses import dataclass
from typing import Optional 

@dataclass
class ParsedWebPage:
    url : str
    text : str 
    title : Optional[str]
    fetch_status : str

def parse_url(url : str , timeout : int = 30) -> ParsedWebPage:
    """Fetch an url and extract its content"""

    try :
        response = httpx.get(
            url,
            timeout= timeout,
            follow_redirects=True,
            headers={"User-Agent": "CitationVerifier/0.1"}
        )

        if response.status_code !=200:
            return ParsedWebPage (
                url=url,
                text="",
                title= None,
                fetch_status=f"Error_{response.status_code}"
            )
        
        html=response.text
        extracted = trafilatura.extract(
            html,
            include_comments=False,
            include_tables = True,
            no_fallback=False
        )

        metadata = trafilatura.extract_metadata(html)
        title = metadata.title if metadata else None

        if not extracted :
            return ParsedWebPage(
                url = url ,
                text = "",
                title=title,
                fetch_status="extraction_failed"
            )
        
        return ParsedWebPage(
            url=url,
            text=extracted,
            title=title,
            fetch_status="success"
        )
    except httpx.TimeoutException:
        return ParsedWebPage(url=url, text="", title=None, fetch_status="timeout")
    except Exception as e:
        return ParsedWebPage(url=url, text="", title=None, fetch_status=f"error: {str(e)}")
