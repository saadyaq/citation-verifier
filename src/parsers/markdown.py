import re 
from pathlib import Path
from dataclasses import dataclass

@dataclass
class ParsedDocument :
    text: str 
    references : dict[str , str] 
    source_path : str