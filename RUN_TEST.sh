#!/bin/bash

echo "🧪 Citation Verifier - Test Rapide"
echo "=================================="
echo ""

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

# Aller dans le bon répertoire
cd /home/user/citation-verifier

# Ajouter src au PYTHONPATH
export PYTHONPATH=/home/user/citation-verifier/src:$PYTHONPATH

echo "🔍 Test 1: Vérifier que les modules se chargent..."
python -c "from citation_verifier.models import Verdict; print('  ✓ Models OK')"
python -c "from citation_verifier.verifier import verify_claim; print('  ✓ Verifier OK')"
echo ""

echo "🔍 Test 2: Test CLI version..."
python -m citation_verifier.cli version
echo ""

echo "🔍 Test 3: Vérification d'un document simple..."
python -m citation_verifier.cli check test_short.md --output json

