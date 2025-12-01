from pydantic import BaseModel, Field 
from enum import Enum
from typing import Optional 

class Verdict(str, Enum):
    """List of potential verdicts"""
    SUPPORTED="supported"
    NOT_SUPPORTED="not_supported"
    PARTIAL="partial"
    INCONCLUSIVE="inconclusive"
    SOURCE_UNAVAILABLE="source_unavailable"

