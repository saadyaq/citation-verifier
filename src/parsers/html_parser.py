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

def parse_html_file(file_path:str)-> ParsedWebPage:
    """Parse a local html file"""

    from pathlib import Path

    path=Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    html=path.readt_text(encoding= "utf-8")

    extracted= trafilatura.extract(
        html,
        include_comments=False,
        include_tables=True
    )

    metadata= trafilatura.extract_metadata(html)
    title=metadata.titile if metadata else None
    return ParsedWebPage(
        url=f"file://{path.absolute()}",
        text=extracted or "",
        title=title,
        fetch_status="success" if extracted else "extraction_failed"
    )