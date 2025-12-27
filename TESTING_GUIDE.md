# 🧪 Guide de Test - Citation Verifier

## Prérequis

### 1. Configuration de l'API Key
```bash
# Créer un fichier .env
echo "ANTHROPIC_API_KEY=votre-clé-api-ici" > .env

# OU exporter directement
export ANTHROPIC_API_KEY=sk-ant-votre-clé-ici
```

### 2. Installation
```bash
pip install -e .
```

---

## Test 1: CLI - Vérification Simple

### Créer un document de test
```bash
cat > test_article.md << 'EOT'
# Article de Test

Python est l'un des langages les plus populaires selon GitHub [1].

Les développeurs préfèrent Python pour l'IA [2].

[1]: https://www.python.org/about/
[2]: https://github.com/features
EOT
```

### Tester le CLI
```bash
# Test basique
cite-verify check test_article.md

# Sortie JSON
cite-verify check test_article.md --output json

# Sortie Markdown
cite-verify check test_article.md --output markdown

# Verbose
cite-verify check test_article.md --verbose
```

**Résultat attendu:**
- Extraction des claims
- Vérification de chaque citation
- Verdict: SUPPORTED / PARTIAL / NOT_SUPPORTED
- Scores de confiance

---

## Test 2: Python API

### Script de test
```python
# test_api.py
import asyncio
from citation_verifier.main import verify_document

async def test_verification():
    # Tester avec le fichier markdown
    results = await verify_document("test_article.md")
    
    print(f"\n📊 Total citations: {len(results)}")
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.verdict.value.upper()}")
        print(f"   Claim: {result.claim.claim_text}")
        print(f"   Confidence: {result.confidence:.0%}")
        print(f"   Explanation: {result.explanation}")

if __name__ == "__main__":
    asyncio.run(test_verification())
```

### Exécuter
```bash
python test_api.py
```

---

## Test 3: REST API

### Démarrer le serveur
```bash
# Terminal 1
uvicorn citation_verifier.api:app --reload --port 8000
```

### Tester les endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Vérifier un document
```bash
curl -X POST http://localhost:8000/verify/document \
  -H "Content-Type: application/json" \
  -d '{"source": "test_article.md"}' | jq
```

#### Vérifier une claim individuelle
```bash
curl -X POST http://localhost:8000/verify/claim \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "Python is popular for AI development",
    "source_url": "https://www.python.org/about/"
  }' | jq
```

#### Documentation interactive
```bash
# Ouvrir dans le navigateur
open http://localhost:8000/docs
```

---

## Test 4: RAG System (Documents Longs)

### Créer un document long
```bash
cat > long_article.md << 'EOT'
# Long Article

Lorem ipsum dolor sit amet... (répéter pour avoir >8000 caractères)

According to research, 85% of companies use AI [1].

[1]: https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai
EOT
```

### Tester avec RAG
```bash
cite-verify check long_article.md --verbose
```

**Ce qui se passe:**
1. Document >8000 chars détecté
2. Chunking automatique (500 chars, 50 overlap)
3. Embedding des chunks
4. Retrieval des 5 passages les plus pertinents
5. Vérification avec seulement le contexte pertinent

**Vérifier les logs:**
```
Using RAG: Retrieved 4523 chars of relevant context
```

---

## Test 5: Différents Formats

### PDF
```bash
cite-verify check sample_with_citations.pdf
```

### URL
```bash
cite-verify check https://example.com/article-with-citations
```

### HTML local
```bash
cite-verify check article.html
```

---

## Test 6: Différents Modèles

```bash
# Claude Sonnet (plus précis, plus cher)
cite-verify check test_article.md --model claude-3-5-sonnet-20241022

# Claude Haiku (plus rapide, moins cher)
cite-verify check test_article.md --model claude-3-5-haiku-20241022

# GPT-4o (nécessite OPENAI_API_KEY)
export OPENAI_API_KEY=sk-...
cite-verify check test_article.md --model gpt-4o
```

---

## Test 7: Tests Unitaires

### Exécuter la suite de tests
```bash
# Tous les tests
pytest

# Tests spécifiques
pytest tests/parsers/test_markdown.py
pytest tests/citation_verifier/test_models.py

# Avec coverage
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

---

## Scénarios de Test Recommandés

### 1. Citation Correcte (SUPPORTED)
```markdown
Python was created by Guido van Rossum [1].
[1]: https://www.python.org/about/
```

### 2. Citation Incorrecte (NOT_SUPPORTED)
```markdown
Python was created in 1995 [1].
[1]: https://www.python.org/about/
# La source dit 1991, pas 1995
```

### 3. Citation Partielle (PARTIAL)
```markdown
85% of developers use Python [1].
[1]: https://survey.stackoverflow.co/2023/
# La source dit peut-être 78%, pas 85%
```

### 4. Source Inaccessible (SOURCE_UNAVAILABLE)
```markdown
Test claim [1].
[1]: https://404.example.com/notfound
```

---

## Débogage

### Activer les logs détaillés
```bash
export LOG_LEVEL=DEBUG
cite-verify check test_article.md --verbose
```

### Vérifier l'API Key
```bash
python -c "import os; print('API Key:', os.getenv('ANTHROPIC_API_KEY')[:20] + '...')"
```

### Tester l'API Claude directement
```python
from anthropic import Anthropic

client = Anthropic()
response = client.messages.create(
    model="claude-3-5-haiku-20241022",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.content[0].text)
```

---

## Métriques à Surveiller

1. **Temps de traitement**: Combien de temps pour vérifier N citations?
2. **Coût**: Tokens consommés par citation
3. **Précision**: Les verdicts sont-ils corrects?
4. **Taux d'erreur**: Sources inaccessibles, timeouts, etc.

---

## Troubleshooting

### Erreur: "ANTHROPIC_API_KEY not found"
```bash
export ANTHROPIC_API_KEY=votre-clé
# Ou créer .env
```

### Erreur: "ModuleNotFoundError: No module named 'citation_verifier'"
```bash
pip install -e .
# Ou ajouter au PYTHONPATH
export PYTHONPATH=/path/to/citation-verifier/src:$PYTHONPATH
```

### Erreur: "Command 'cite-verify' not found"
```bash
# Utiliser python -m
python -m citation_verifier.cli check document.md
```

### RAG ne fonctionne pas
```bash
# Installer sentence-transformers
pip install sentence-transformers
```

---

## Tests Automatisés

### Script de test complet
```bash
#!/bin/bash
# run_all_tests.sh

echo "🧪 Running Citation Verifier Tests..."

# 1. Unit tests
echo "1. Unit tests..."
pytest -v

# 2. CLI tests
echo "2. CLI tests..."
cite-verify check test_article.md
cite-verify check test_article.md --output json > /dev/null
cite-verify version

# 3. API tests
echo "3. API tests..."
uvicorn citation_verifier.api:app --port 8001 &
API_PID=$!
sleep 3
curl http://localhost:8001/health
kill $API_PID

echo "✅ All tests completed!"
```

---

## Résultats Attendus

### Output Terminal
```
Verification Summary

Total Citations     3
[+] Supported       2
[!] Partial         1

Detailed Results

1. [+] SUPPORTED (confidence: 95%)
   Claim: Python was created by Guido van Rossum
   Source: https://www.python.org/about/
   Explanation: The source confirms...
```

### Output JSON
```json
{
  "summary": {
    "total_citations": 3,
    "supported": 2,
    "partial": 1
  },
  "results": [...]
}
```

