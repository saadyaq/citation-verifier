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

class ClaimCitation(BaseModel):
    """Infos about the citation"""
    claim_text: str
    citation_url: Optional[str] = None      
    citation_ref: Optional[str] = None      
    original_context: str
    
    @property
    def has_url(self) -> bool:
        return self.citation_url is not None

class SourceContent(BaseModel):
    url : str
    content : Optional[str] =None
    fetch_status : str ="pending" # success, failed, timeout, paywalled


class VerificationResult(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    claim: ClaimCitation
    verdict: Verdict
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str
    source_quote: Optional[str] = None