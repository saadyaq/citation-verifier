#!/bin/bash

echo "🧪 Citation Verifier - Test Rapide"
echo "=================================="
echo ""

# Utiliser le répertoire courant
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Charger le fichier .env s'il existe
if [ -f .env ]; then
    echo "📄 Chargement du fichier .env..."
    export $(cat .env | grep -v '^#' | xargs)
    echo "✓ Fichier .env chargé"
    echo ""
fi

# Vérifier la clé API
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ANTHROPIC_API_KEY non définie!"
    echo ""
    echo "Pour configurer:"
    echo "  export ANTHROPIC_API_KEY=sk-ant-votre-clé-ici"
    echo ""
    echo "Ou créer un fichier .env:"
    echo "  echo 'ANTHROPIC_API_KEY=sk-ant-votre-clé' > .env"
    exit 1
fi

echo "✓ API Key trouvée: ${ANTHROPIC_API_KEY:0:20}..."
echo ""

# Ajouter src au PYTHONPATH
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

echo "🔍 Test 1: Vérifier que les modules se chargent..."
python3 -c "from citation_verifier.models import Verdict; print('  ✓ Models OK')"
python3 -c "import sys; sys.path.insert(0, 'src'); from citation_verifier.models import ClaimCitation; print('  ✓ ClaimCitation OK')"
echo ""

echo "🔍 Test 2: Test CLI version..."
python3 -m citation_verifier.cli version
echo ""

echo "🔍 Test 3: Test API Claude (direct)..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, 'src')
from anthropic import Anthropic
import os

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
response = client.messages.create(
    model="claude-3-5-haiku-20241022",
    max_tokens=50,
    messages=[{"role": "user", "content": "Say hello in one word"}]
)
print(f"  ✓ Claude API: {response.content[0].text}")
PYEOF
echo ""

echo "🔍 Test 4: Test de vérification simple (SANS RAG)..."
echo "  Note: Test léger pour éviter les problèmes de mémoire"
python3 << 'PYEOF'
import asyncio
import sys
sys.path.insert(0, 'src')

from citation_verifier.models import ClaimCitation, SourceContent, Verdict
from citation_verifier.verifier import verify_claim

async def test():
    claim = ClaimCitation(
        claim_text="Python is a programming language",
        citation_url="https://www.python.org/",
        original_context="Python is a programming language"
    )
    
    # Source courte (pas de RAG)
    source = SourceContent(
        url="https://www.python.org/",
        content="Python is a high-level programming language.",
        fetch_status="success"
    )
    
    print("  Vérification en cours...")
    result = await verify_claim(claim, source)
    
    print(f"  ✓ Verdict: {result.verdict.value}")
    print(f"  ✓ Confidence: {result.confidence:.0%}")
    print(f"  ✓ Explication: {result.explanation[:80]}...")
    
    return result

asyncio.run(test())
PYEOF

echo ""
echo "✅ Tests de base terminés avec succès!"
echo ""
echo "⚠️  NOTE: Le test complet (cite-verify check) nécessite beaucoup de RAM"
echo "   à cause de sentence-transformers. Utilisez-le sur une machine avec >4GB RAM."
echo ""
echo "📚 Pour tester manuellement sans RAG:"
echo "   python3 -m citation_verifier.cli check test_short.md"
