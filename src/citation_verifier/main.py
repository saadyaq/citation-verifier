import asyncio
from dotenv import load_dotenv
from .models import ClaimCitation
from .fetcher import fetch_source
from .verifier import verify_claim

load_dotenv()

async def main():
    
    claim = ClaimCitation(
        claim_text="85% des entreprises utilisent l'IA en 2025",
        citation_url="https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai",
        original_context="Selon McKinsey, 85% des entreprises utilisent l'IA en 2025."
    )
    
    print(f"Vérification: {claim.claim_text}")
    print(f"Source: {claim.citation_url}")
    print("-" * 50)
    
    
    print("Fetching source...")
    source = await fetch_source(claim.citation_url)
    print(f"Status: {source.fetch_status}")
    
    if source.fetch_status == "success":
        
        print("Verifying claim...")
        result = await verify_claim(claim, source)
        
        print(f"\nVERDICT: {result.verdict.value.upper()}")
        print(f"Confidence: {result.confidence}")
        print(f"Explanation: {result.explanation}")
        if result.source_quote:
            print(f"Source quote: {result.source_quote}")

if __name__ == "__main__":
    asyncio.run(main())