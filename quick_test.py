import asyncio
import sys
import os

# Ajouter src au path
sys.path.insert(0, '/home/user/citation-verifier/src')

from citation_verifier.models import ClaimCitation, SourceContent
from citation_verifier.verifier import verify_claim

async def test_simple():
    """Test simple sans extraire les claims."""
    
    print("🧪 Test de vérification simple...")
    
    # Créer une claim manuellement
    claim = ClaimCitation(
        claim_text="Python is a programming language",
        citation_url="https://www.python.org/about/",
        original_context="Python is a programming language."
    )
    
    # Source simulée (petit contenu)
    source = SourceContent(
        url="https://www.python.org/about/",
        content="Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability.",
        fetch_status="success"
    )
    
    print("✓ Claim et source créés")
    print(f"  Claim: {claim.claim_text}")
    print(f"  Source: {len(source.content)} chars")
    
    # Vérifier
    print("\n🔍 Vérification en cours...")
    try:
        result = await verify_claim(claim, source)
        
        print("\n✅ Résultat:")
        print(f"  Verdict: {result.verdict.value}")
        print(f"  Confidence: {result.confidence:.0%}")
        print(f"  Explanation: {result.explanation}")
        
        return result
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Vérifier l'API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY non trouvée!")
        print("   Exporter avec: export ANTHROPIC_API_KEY=votre-clé")
        sys.exit(1)
    
    print(f"✓ API Key trouvée: {api_key[:20]}...")
    
    asyncio.run(test_simple())
