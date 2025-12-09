import httpx
import trafilatura
from dataclasses import dataclass
from typing import Optional 

@dataclass
class ParseWebPage:
    url : str
    text : str 
    title : Optional[str]
    fetch_status : str

def parse_url(url : str , timeout : int = 30) -> ParseWebPage:
