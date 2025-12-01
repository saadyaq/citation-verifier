# Citation Verification Agent - Architecture Technique

## Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              INPUT                                       │
│         Document (PDF, Markdown, URL, texte brut)                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        1. DOCUMENT PARSER                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ PDF Parser  │  │ MD Parser   │  │ HTML Parser │  │ URL Fetcher │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                                          │
│  Output: Texte brut structuré + métadonnées                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      2. CLAIM EXTRACTOR (LLM)                            │
│                                                                          │
│  - Identifie les affirmations qui citent des sources                    │
│  - Extrait les paires (claim, citation)                                 │
│  - Détecte le type de citation (URL, DOI, référence biblio)             │
│                                                                          │
│  Output: List[ClaimCitation]                                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       3. SOURCE FETCHER                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │  Web Scraper    │  │  PDF Downloader │  │  API Clients    │         │
│  │  (URLs)         │  │  (Academic)     │  │  (ArXiv, etc.)  │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
│                                                                          │
│  Gère: timeouts, paywalls, rate limiting, retry logic                   │
│  Output: List[SourceContent] avec statut (fetched/failed/paywalled)     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      4. SOURCE ANALYZER                                  │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │                    Chunking + Embeddings                     │        │
│  │  - Découpe les sources longues en chunks                     │        │
│  │  - Génère embeddings pour recherche sémantique               │        │
│  └─────────────────────────────────────────────────────────────┘        │
│                              │                                           │
│                              ▼                                           │
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │                   Relevant Passage Finder                    │        │
│  │  - Trouve les passages pertinents pour chaque claim          │        │
│  │  - Utilise similarity search (RAG)                           │        │
│  └─────────────────────────────────────────────────────────────┘        │
│                                                                          │
│  Output: List[RelevantPassages] par claim                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    5. VERIFICATION ENGINE (LLM)                          │
│                                                                          │
│  Input: (claim, relevant_passages)                                      │
│                                                                          │
│  Prompt structuré:                                                      │
│  - Compare le claim aux passages sources                                │
│  - Identifie les contradictions, exagérations, déformations             │
│  - Génère une explication                                               │
│                                                                          │
│  Output: VerificationResult                                             │
│    - verdict: SUPPORTED | NOT_SUPPORTED | PARTIAL | INCONCLUSIVE        │
│    - confidence: 0.0 - 1.0                                              │
│    - explanation: string                                                │
│    - source_quote: passage exact de la source                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      6. REPORT GENERATOR                                 │
│                                                                          │
│  Formats de sortie:                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │   JSON   │  │ Markdown │  │   HTML   │  │ Terminal │                │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘                │
│                                                                          │
│  Inclut: résumé, détails par citation, statistiques                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              OUTPUT                                      │
│                                                                          │
│  {                                                                       │
│    "summary": { "total": 12, "supported": 8, "issues": 4 },            │
│    "results": [                                                         │
│      {                                                                   │
│        "claim": "80% des devs préfèrent Python",                        │
│        "source_url": "https://...",                                     │
│        "verdict": "NOT_SUPPORTED",                                      │
│        "explanation": "La source dit 62%, pas 80%",                     │
│        "source_quote": "62% of respondents indicated..."                │
│      }                                                                   │
│    ]                                                                     │
│  }                                                                       │
└─────────────────────────────────────────────────────────────────────────┘


## Data Models

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class Verdict(Enum):
    SUPPORTED = "supported"           # La source confirme le claim
    NOT_SUPPORTED = "not_supported"   # La source contredit le claim
    PARTIAL = "partial"               # Partiellement vrai/exagéré
    INCONCLUSIVE = "inconclusive"     # Impossible de déterminer
    SOURCE_UNAVAILABLE = "unavailable" # Source inaccessible

@dataclass
class ClaimCitation:
    claim_text: str                   # L'affirmation dans le document
    citation_ref: str                 # URL, DOI, ou référence
    location: str                     # Position dans le document original
    citation_type: str                # "url", "doi", "bibliography"

@dataclass
class SourceContent:
    url: str
    content: Optional[str]            # None si fetch failed
    fetch_status: str                 # "success", "failed", "paywalled"
    content_type: str                 # "html", "pdf", "text"

@dataclass
class VerificationResult:
    claim: ClaimCitation
    source: SourceContent
    verdict: Verdict
    confidence: float                 # 0.0 to 1.0
    explanation: str                  # Explication en langage naturel
    source_quote: Optional[str]       # Citation exacte de la source
```


## Flow détaillé pour UN claim

```
Document: "Selon McKinsey, 85% des entreprises utilisent l'IA [1]"
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │     Claim Extractor       │
                    │                           │
                    │ claim: "85% des           │
                    │         entreprises       │
                    │         utilisent l'IA"   │
                    │ source: [1] → URL McKinsey│
                    └───────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │     Source Fetcher        │
                    │                           │
                    │ GET https://mckinsey.com/ │
                    │ → 200 OK                  │
                    │ → HTML content (50KB)     │
                    └───────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │     Source Analyzer       │
                    │                           │
                    │ Chunks: 45 passages       │
                    │ Query: "85% entreprises   │
                    │         utilisent IA"     │
                    │ Top 3 passages trouvés    │
                    └───────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │   Verification Engine     │
                    │                           │
                    │ Compare:                  │
                    │ Claim: "85%"              │
                    │ Source: "78% of companies │
                    │          have adopted AI" │
                    │                           │
                    │ → PARTIAL (exagération)   │
                    │ → Confidence: 0.9         │
                    └───────────────────────────┘
```


## Stack technique recommandé

### Core
- Python 3.11+
- LangChain (orchestration, pas obligatoire)
- Pydantic (validation des data models)

### LLM
- Claude Sonnet 3.5 ou GPT-4o (production)
- Ollama + Llama 3.1 (dev local, gratuit)

### Parsing & Scraping
- BeautifulSoup4 (HTML)
- PyMuPDF ou pdfplumber (PDF)
- httpx (HTTP async)
- trafilatura (extraction de contenu web)

### Embeddings & RAG
- sentence-transformers (embeddings locaux)
- ChromaDB (vector store simple)
- Alternative: OpenAI embeddings si budget OK

### CLI & Output
- Typer (CLI)
- Rich (output terminal)


## Structure du projet

```
citation-verifier/
├── src/
│   └── citation_verifier/
│       ├── __init__.py
│       ├── cli.py                 # Point d'entrée CLI
│       ├── models.py              # Data models (Pydantic)
│       ├── parsers/
│       │   ├── __init__.py
│       │   ├── pdf.py
│       │   ├── markdown.py
│       │   └── html.py
│       ├── extractors/
│       │   ├── __init__.py
│       │   └── claim_extractor.py # LLM-based extraction
│       ├── fetchers/
│       │   ├── __init__.py
│       │   ├── web.py
│       │   └── pdf.py
│       ├── analyzers/
│       │   ├── __init__.py
│       │   ├── chunker.py
│       │   └── retriever.py       # RAG logic
│       ├── verifier/
│       │   ├── __init__.py
│       │   └── engine.py          # Core verification LLM
│       └── reporters/
│           ├── __init__.py
│           ├── json_report.py
│           ├── markdown_report.py
│           └── terminal_report.py
├── tests/
│   ├── fixtures/                  # Documents de test
│   └── ...
├── examples/
│   └── sample_documents/
├── pyproject.toml
├── README.md
└── .env.example
```


## Interfaces utilisateur (MVP)

### 1. CLI (priorité haute)
```bash
# Vérifier un fichier local
cite-verify check document.pdf

# Vérifier une URL
cite-verify check https://example.com/article

# Options
cite-verify check document.md --output json --model gpt-4o
```

### 2. API REST (priorité moyenne)
```python
POST /verify
{
    "content": "...",
    "content_type": "markdown"
}

Response:
{
    "results": [...],
    "summary": {...}
}
```

### 3. Web UI (priorité basse, si temps)
- Streamlit ou Gradio pour un prototype rapide
- Upload de fichier + affichage des résultats


## Considérations importantes

### Gestion des erreurs
- Sources inaccessibles (paywall, 404, timeout)
- Documents mal formatés
- Rate limiting des APIs
- LLM qui hallucine

### Limites connues
- Ne peut pas vérifier les sources derrière paywall
- Les citations de livres physiques sont difficiles
- Dépend de la qualité du LLM pour le raisonnement
- Coût API pour les gros documents

### Métriques à tracker
- Temps de vérification par citation
- Coût tokens par document
- Taux de sources inaccessibles
- Précision (si tu crées un dataset de test)
