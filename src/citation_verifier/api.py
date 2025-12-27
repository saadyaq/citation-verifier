"""REST API for Citation Verifier."""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from enum import Enum
import asyncio
from datetime import datetime
import uuid

from .main import verify_document
from .models import Verdict as VerdictEnum
from .fetcher import fetch_source
from .verifier import verify_claim as verify_single_claim
from .models import ClaimCitation, SourceContent

app = FastAPI(
    title="Citation Verifier API",
    description="AI-powered citation verification API. Verify citations in documents or individual claims.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class VerifyDocumentRequest(BaseModel):
    """Request to verify all citations in a document."""
    source: str = Field(..., description="URL or file path to the document")
    model: str = Field(default="claude-3-5-haiku-20241022", description="LLM model to use")


class VerifyClaimRequest(BaseModel):
    """Request to verify a single claim against a source."""
    claim: str = Field(..., description="The claim to verify")
    source_url: HttpUrl = Field(..., description="URL of the source to check against")
    model: str = Field(default="claude-3-5-haiku-20241022", description="LLM model to use")


class Verdict(str, Enum):
    """Verification verdict."""
    SUPPORTED = "supported"
    NOT_SUPPORTED = "not_supported"
    PARTIAL = "partial"
    INCONCLUSIVE = "inconclusive"
    SOURCE_UNAVAILABLE = "source_unavailable"


class VerificationResponse(BaseModel):
    """Response for a single verification."""
    claim: str
    source_url: Optional[str] = None
    verdict: Verdict
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str
    source_quote: Optional[str] = None


class DocumentVerificationResponse(BaseModel):
    """Response for document verification."""
    summary: dict
    results: List[VerificationResponse]
    processing_time_seconds: float


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime


# Endpoints
@app.get("/", tags=["General"])
async def root():
    """Root endpoint."""
    return {
        "message": "Citation Verifier API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.utcnow()
    )


@app.post("/verify/document", response_model=DocumentVerificationResponse, tags=["Verification"])
async def verify_document_endpoint(request: VerifyDocumentRequest):
    """Verify all citations in a document.
    
    Supports:
    - Markdown files (.md)
    - PDF files (.pdf)
    - HTML files or URLs
    """
    import time
    start_time = time.time()
    
    try:
        # Run verification
        results = await verify_document(request.source)
        
        # Calculate summary
        verdict_counts = {}
        for result in results:
            key = result.verdict.value
            verdict_counts[key] = verdict_counts.get(key, 0) + 1
        
        summary = {
            "total_citations": len(results),
            **verdict_counts
        }
        
        # Convert results to response format
        verification_results = [
            VerificationResponse(
                claim=r.claim.claim_text,
                source_url=getattr(r.claim, 'citation_url', None),
                verdict=Verdict(r.verdict.value),
                confidence=r.confidence,
                explanation=r.explanation,
                source_quote=r.source_quote
            )
            for r in results
        ]
        
        processing_time = time.time() - start_time
        
        return DocumentVerificationResponse(
            summary=summary,
            results=verification_results,
            processing_time_seconds=round(processing_time, 2)
        )
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {request.source}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@app.post("/verify/claim", response_model=VerificationResponse, tags=["Verification"])
async def verify_claim_endpoint(request: VerifyClaimRequest):
    """Verify a single claim against a source URL."""
    try:
        # Fetch the source
        source = await fetch_source(str(request.source_url))
        
        if source.fetch_status != "success":
            return VerificationResponse(
                claim=request.claim,
                source_url=str(request.source_url),
                verdict=Verdict.SOURCE_UNAVAILABLE,
                confidence=1.0,
                explanation=f"Source unavailable: {source.fetch_status}",
                source_quote=None
            )
        
        # Create claim object
        claim = ClaimCitation(
            claim_text=request.claim,
            citation_url=str(request.source_url),
            original_context=request.claim
        )
        
        # Verify the claim
        result = await verify_single_claim(claim, source, model=request.model)
        
        return VerificationResponse(
            claim=result.claim.claim_text if hasattr(result.claim, 'claim_text') else request.claim,
            source_url=str(request.source_url),
            verdict=Verdict(result.verdict.value),
            confidence=result.confidence,
            explanation=result.explanation,
            source_quote=result.source_quote
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
