import re 
from pathlib import Path
from dataclasses import dataclass

@dataclass
class ParsedDocument :
    text: str 
    references : dict[str , str] 
    source_path : str

def parse_document( file_path :str) -> ParsedDocument :
    """Parsing a markdown and extracting text + reference"""

    path = Path(file_path)
    if not path.exists() :
        raise FileNotFoundError(f"File not found")
    text = path.read_text(encoding = "utf-8")

    references= {}
    ref_pattern = r'\[(\d+)\]:\s*(https?://[^\s]+)'
    for match in re.finditer(ref_pattern, text):
        ref_id = f"[{match.group(1)}]"
        url = match.group(2)
        references[ref_id] = url
    
    
    alt_pattern = r'^\[(\d+)\]\s+(https?://[^\s]+)'
    for match in re.finditer(alt_pattern, text, re.MULTILINE):
        ref_id = f"[{match.group(1)}]"
        url = match.group(2)
        if ref_id not in references:
            references[ref_id] = url
    
    return ParsedDocument(
        text=text,
        references=references,
        source_path=str(path.absolute())
    )


def resolve_references(claims: list, references: dict[str, str]) -> list:
   
    
    for claim in claims:
        if claim.citation_ref and not claim.citation_url:
           
            ref = claim.citation_ref.strip()
            if ref in references:
                claim.citation_url = references[ref]
           
            elif f"[{ref}]" in references:
                claim.citation_url = references[f"[{ref}]"]
    
    return claims