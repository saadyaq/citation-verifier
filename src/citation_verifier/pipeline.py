from pathlib import Path
from parsers.markdown import parse_document as parse_markdown, resolve_references
from parsers.html_parser import parse_url, parse_html_file
from parsers.pdf import parse_pdf
from extractors.claim_extractor import extract_claims
from .models import ClaimCitation

def process_document(source : str) -> list[ClaimCitation]:
    """ Process a document, either a local file or a URL, and return the claims.

        Args:
        source: Path to a file (.md, .html, .pdf) or a URL.

        Returns:
        List of ClaimCitation with resolved URLs."""
    
    if source.startswith("http://") or source.startswith("https://"):
        page=parse_url(source)
        if page.fetch_status !="success":
            raise ValueError(f"Failed to fetch url : {page.fetch_status}")
        
        text=page.text
        references={}
    else:
        path=Path(source)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {source}")
        
        suffix= path.suffix.lower()
        if suffix==".md":
            doc=parse_markdown(source)
            text=doc.text
            references=doc.references
        elif suffix in [".html", ".htm"]:
            page= parse_html_file(source)
            text=page.text
            references={}
        
        elif suffix==".pdf":
            doc = parse_pdf(source)
            text = doc.text
            references = doc.references
        else:
            text=path.read_text(encoding="utf-8")
            references={}

    claims=extract_claims(text)
    claims=resolve_references(claims, references)

    verifiable_claims= [c for c in claims if c.citation_url]
    return verifiable_claims