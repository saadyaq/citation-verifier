#!/bin/bash

echo "🧪 Citation Verifier - Test Rapide"
echo "=================================="
echo ""

# Aller dans le bon répertoire
cd /home/user/citation-verifier

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
export PYTHONPATH=/home/user/citation-verifier/src:$PYTHONPATH

echo "🔍 Test 1: Vérifier que les modules se chargent..."
python3 -c "from citation_verifier.models import Verdict; print('  ✓ Models OK')"
python3 -c "from citation_verifier.verifier import verify_claim; print('  ✓ Verifier OK')"
echo ""

echo "🔍 Test 2: Test CLI version..."
python3 -m citation_verifier.cli version
echo ""

echo "🔍 Test 3: Vérification d'un document simple..."
echo "   Document: test_short.md"
python3 -m citation_verifier.cli check test_short.md

echo ""
echo "✅ Tests terminés!"
