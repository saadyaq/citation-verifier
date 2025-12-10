import asyncio
from dotenv import load_dotenv
from .pipeline import process_document
from .fetcher import fetch_source
from .verifier import verify_claim

load_dotenv()

async def verify_document(source: str) -> list:
    """Vérifie toutes les citations d'un document."""
    
    print(f"Processing: {source}")
    
    # Extraire les claims
    claims = process_document(source)
    print(f"Found {len(claims)} verifiable claims")
    
    results = []
    
    for i, claim in enumerate(claims, 1):
        print(f"\n[{i}/{len(claims)}] Verifying: {claim.claim_text[:50]}...")
        
        # Fetch la source
        source_content = await fetch_source(claim.citation_url)
        
        if source_content.fetch_status != "success":
            print(f"  Source unavailable: {source_content.fetch_status}")
            continue
        
        # Vérifier
        result = await verify_claim(claim, source_content)
        results.append(result)
        
        print(f"  Verdict: {result.verdict.value}")
    
    return results


async def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m src.citation_verifier.main <file_or_url>")
        sys.exit(1)
    
    source = sys.argv[1]
    results = await verify_document(source)
    
    # Résumé
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    for r in results:
        print(f"\nClaim: {r.claim.claim_text[:60]}...")
        print(f"Verdict: {r.verdict.value.upper()}")
        print(f"Explanation: {r.explanation}")


if __name__ == "__main__":
    asyncio.run(main())