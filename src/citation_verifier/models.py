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

class ClaimCitation(str,Enum):
    """Infos about the citation"""
    claim_text: str = Field(description="L'affirmation faite dans le document")
    citation_url: str= Field(description=" URL de la source citée")
    original_context: str=Field(description= "Phrase complète dans la citation")

class SourceContent(BaseModel):
    url : str
    content : Optional[str] =None
    fetch_status : str ="pending" # success, failed, timeout, paywalled


class VerificationResult(BaseModel):
    claim: ClaimCitation
    verdict: Verdict
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str
    source_quote: Optional[str] = None