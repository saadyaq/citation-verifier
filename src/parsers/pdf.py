import fitz
from pathlib import Path
from dataclasses import dataclass
import re

@dataclass
class ParsedPDF:
    text : str
    references : dict[str,str]
    page_count : int
    source_path : str

def parse_pdf(file_path : str) -> ParsedPDF:
    """Extract text from a pdf"""

    path=Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"file not found: {file_path}")
    
    doc=fitz.open(file_path)
    text_parts = []
    for page in doc :
        text_parts.append(page.get_text())
    full_text="\n".join(text_parts)

    references={}
    ref_pattern=r'\[(\d+)\]\s*(https?://[^\s]+)'
    for match in re.finditer(ref_pattern, full_text):
        ref_id=f"[{match.group(1)}]"
        url=match.group(2)
        references[ref_id]=url
    doc.close()

    return ParsedPDF(
        text=full_text,
        references=references,
        page_count=len(text_parts),
        source_path=str(path.absolute())
    )
