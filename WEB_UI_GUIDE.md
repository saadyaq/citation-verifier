# Citation Verifier - Web Interface Guide

Une interface web interactive pour vérifier les citations dans vos documents.

## 🚀 Démarrage Rapide

### 1. Installation

```bash
# Installer les dépendances
pip install -e .

# Ou installer juste Streamlit si déjà installé
pip install streamlit
```

### 2. Configuration

Assurez-vous que votre clé API Anthropic est définie:

```bash
export ANTHROPIC_API_KEY=your-key-here
```

Ou créez un fichier `.env`:

```bash
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

### 3. Lancer l'application

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse: `http://localhost:8501`

---

## 📖 Guide d'utilisation

### Interface Principale

L'interface est divisée en deux onglets:

#### 📄 Upload Document
- Glissez-déposez ou sélectionnez un fichier
- Formats supportés: **Markdown (.md)**, **PDF (.pdf)**, **HTML (.html)**
- Cliquez sur "🔍 Verify Citations" pour lancer la vérification

#### 🔗 Verify URL
- Collez l'URL d'un document en ligne
- Cliquez sur "🔍 Verify Citations" pour lancer la vérification

### ⚙️ Configuration (Barre latérale)

**LLM Model:**
- `claude-3-5-haiku-20241022` - Rapide et économique (recommandé)
- `claude-3-5-sonnet-20241022` - Plus précis, plus cher
- `claude-3-opus-20240229` - Le plus précis, le plus cher

**Enable RAG:**
- ✅ Activé: Utilise RAG pour les documents longs (>15,000 caractères)
- ❌ Désactivé: Tronque les documents longs (recommandé pour systèmes avec peu de RAM)

**Output Format:**
- **Interactive Display** - Affichage interactif avec statistiques et détails
- **JSON** - Format structuré pour intégrations
- **Markdown** - Format texte lisible

---

## 🎨 Fonctionnalités

### Vue Interactive (par défaut)

#### Statistiques en temps réel
- Total de citations trouvées
- Nombre de citations supportées ✓
- Nombre de citations non-supportées ✗
- Nombre de citations partielles ⚠

#### Résultats détaillés
Pour chaque citation:
- **Affirmation complète** - Le texte de la citation
- **Source** - Lien vers la source citée
- **Verdict** - supported / not_supported / partial / inconclusive
- **Confiance** - Barre de progression (0-100%)
- **Explication** - Pourquoi ce verdict
- **Citation source** - Extrait pertinent de la source

#### Téléchargements
- 📥 **Download JSON** - Télécharger les résultats en JSON
- 📥 **Download Markdown** - Télécharger le rapport en Markdown

---

## 💡 Exemples d'utilisation

### Exemple 1: Vérifier un PDF

1. Cliquez sur l'onglet "📄 Upload Document"
2. Uploadez votre fichier PDF avec citations
3. Configurez:
   - Model: `claude-3-5-haiku-20241022`
   - RAG: Désactivé (si petit document ou peu de RAM)
   - Format: Interactive Display
4. Cliquez sur "🔍 Verify Citations"
5. Consultez les résultats et téléchargez le rapport

### Exemple 2: Vérifier un article en ligne

1. Cliquez sur l'onglet "🔗 Verify URL"
2. Collez l'URL de l'article
3. Configurez les options
4. Cliquez sur "🔍 Verify Citations"
5. Analysez les résultats

### Exemple 3: Export JSON pour intégration

1. Uploadez votre document
2. Format de sortie: **JSON**
3. Vérifiez
4. Téléchargez le JSON
5. Utilisez dans votre pipeline CI/CD

---

## 🎯 Codes couleur des verdicts

| Verdict | Couleur | Icône | Signification |
|---------|---------|-------|---------------|
| **Supported** | 🟢 Vert | ✓ | La source supporte l'affirmation |
| **Not Supported** | 🔴 Rouge | ✗ | La source contredit ou ne mentionne pas l'affirmation |
| **Partial** | 🟠 Orange | ⚠ | La source supporte partiellement (nuances, chiffres différents) |
| **Inconclusive** | ⚪ Gris | ? | Impossible de déterminer avec certitude |
| **Source Unavailable** | ⚪ Gris | ! | Source inaccessible |

---

## ⚡ Performance et optimisations

### Systèmes avec peu de mémoire

Si vous rencontrez des erreurs "Killed" ou des ralentissements:

1. **Désactivez le RAG** - Décochez "Enable RAG for long documents"
2. **Utilisez Haiku** - Choisissez `claude-3-5-haiku-20241022`
3. **Documents courts** - Divisez les gros documents en sections

### Documents longs (>15,000 caractères)

Pour de meilleurs résultats:

1. **Activez le RAG** - Si vous avez >4GB RAM disponible
2. **Utilisez Sonnet** - Pour une meilleure compréhension
3. **Format interactif** - Pour naviguer facilement dans les résultats

---

## 🐛 Dépannage

### L'application ne démarre pas

```bash
# Vérifier l'installation de Streamlit
pip install streamlit

# Vérifier les dépendances
pip install -e .

# Lancer avec verbose
streamlit run app.py --logger.level=debug
```

### "ANTHROPIC_API_KEY not found"

```bash
# Vérifier la variable d'environnement
echo $ANTHROPIC_API_KEY

# Définir la clé
export ANTHROPIC_API_KEY=your-key-here

# Ou créer .env
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

### Erreur "Killed" pendant la vérification

➡️ Désactivez le RAG dans la configuration (barre latérale)

### L'upload de fichier ne fonctionne pas

- Vérifiez que le fichier est au bon format (.md, .pdf, .html)
- Vérifiez la taille du fichier (<200MB limite Streamlit par défaut)
- Essayez de redémarrer l'application

---

## 🔧 Configuration avancée

### Changer le port

```bash
streamlit run app.py --server.port 8080
```

### Mode dark/light

Utilisez le menu ⋮ en haut à droite de l'interface Streamlit.

### Limites d'upload

Créez un fichier `.streamlit/config.toml`:

```toml
[server]
maxUploadSize = 500

[theme]
primaryColor = "#0066CC"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
```

---

## 📊 Structure des résultats

### JSON

```json
{
  "summary": {
    "total_citations": 5,
    "supported": 3,
    "not_supported": 1,
    "partial": 1
  },
  "results": [
    {
      "claim": {
        "claim_text": "...",
        "citation_url": "..."
      },
      "verdict": "supported",
      "confidence": 0.95,
      "explanation": "...",
      "source_quote": "..."
    }
  ]
}
```

### Markdown

```markdown
# Citation Verification Report

**Summary:** 5 total citations | 3 supported ✓ | 1 not supported ✗ | 1 partial ⚠

## Results

### Citation 1: [SUPPORTED] ✓

**Claim:** ...
**Source:** https://...
**Confidence:** 95%
**Explanation:** ...
```

---

## 🚀 Déploiement en production

### Streamlit Cloud (Gratuit)

1. Poussez votre code sur GitHub
2. Allez sur [share.streamlit.io](https://share.streamlit.io)
3. Connectez votre repo
4. Ajoutez `ANTHROPIC_API_KEY` dans les secrets
5. Déployez!

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

```bash
docker build -t citation-verifier .
docker run -p 8501:8501 -e ANTHROPIC_API_KEY=your-key citation-verifier
```

---

## 📚 Ressources

- [Documentation Streamlit](https://docs.streamlit.io)
- [Documentation Claude API](https://docs.anthropic.com)
- [README du projet](README.md)
- [Guide de test](TESTING_GUIDE.md)

---

## 🤝 Support

Si vous rencontrez des problèmes:

1. Consultez cette documentation
2. Vérifiez les [Issues GitHub](https://github.com/anthropics/claude-code/issues)
3. Ouvrez une nouvelle issue avec les détails de votre problème

---

**Version:** 0.1.0
**Dernière mise à jour:** 2025-12-27
