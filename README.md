<div align="center">

# 🔍 Citation Verifier

**Stop AI Hallucinations. Verify Every Citation.**

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

[Features](#features) • [Installation](#installation) • [Quick Start](#quick-start) • [Documentation](#documentation)

</div>

---

## 🎯 Why Citation Verifier?


An AI agent that verifies whether cited sources actually support the claims made in documents.

## ✨ Features

- ✅ **Multiple Format Support** - Markdown, PDF, HTML/URLs, and plain text
- 🤖 **AI-Powered Analysis** - Uses Claude Haiku/Sonnet or GPT-4o for verification
- 🎯 **Precise Verdicts** - SUPPORTED, NOT_SUPPORTED, PARTIAL, INCONCLUSIVE, SOURCE_UNAVAILABLE
- 📊 **Detailed Reports** - JSON, Markdown, or Rich terminal output with confidence scores
- 📦 **Multiple Interfaces** - Full-featured CLI, Python API, and REST API
- ⚡ **RAG for Long Documents** - Automatic embedding-based retrieval for sources >8000 chars
- 🎨 **Beautiful CLI** - Rich terminal formatting with progress indicators and colors
- 🔌 **REST API** - FastAPI server with auto-generated docs and async support

## 🚀 Quick Start

```bash
# Install
pip install -e .
# OR
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY=your-key-here

# Verify a document (CLI)
cite-verify check document.md

# Get JSON output
cite-verify check document.md --output json

# Start REST API server
uvicorn citation_verifier.api:app --reload
```



## The Problem

Research tools like GPT Researcher and Perplexity generate reports with citations. But they never verify if those citations actually support the claims. A source might say "62%" while the document claims "80%". A citation might not mention the topic at all.

Citation Verifier solves this. Give it a document, and it checks every citation against its source.

## How It Works

```
Document with citations
        ↓
Extract claims + their cited sources
        ↓
Fetch original sources
        ↓
Compare each claim against its source
        ↓
Report: SUPPORTED / NOT_SUPPORTED / PARTIAL
```

## Installation

```bash
git clone https://github.com/yourusername/citation-verifier.git
cd citation-verifier
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Create a `.env` file:

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Or use environment variables:

```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## Usage

### Command Line

```bash
# Verify a local file
cite-verify check document.md

# Verify a PDF
cite-verify check document.pdf

# Verify a URL
cite-verify check https://example.com/article

# Output as JSON
cite-verify check document.md --output json

# Output as Markdown
cite-verify check document.md --output markdown

# Use a specific model
cite-verify check document.md --model claude-3-5-sonnet-20241022

# Show version
cite-verify version

# Get help
cite-verify --help
```

### Python API

```python
from citation_verifier import verify_document

results = await verify_document("path/to/document.md")

for result in results:
    print(f"Claim: {result.claim.claim_text}")
    print(f"Verdict: {result.verdict}")
    print(f"Explanation: {result.explanation}")
```

### REST API

```bash
# Start the server
uvicorn citation_verifier.api:app --reload

# Verify a document
curl -X POST http://localhost:8000/verify/document \
  -H "Content-Type: application/json" \
  -d '{"source": "document.md"}'

# Verify a single claim
curl -X POST http://localhost:8000/verify/claim \
  -H "Content-Type: application/json" \
  -d '{"claim": "80% of companies use AI", "source_url": "https://example.com/study"}'

# View API documentation
open http://localhost:8000/docs
```

See [API_README.md](API_README.md) for complete API documentation.

## Supported Formats

| Input | Status |
|-------|--------|
| Markdown (.md) | Supported |
| PDF (.pdf) | Supported |
| HTML / URLs | Supported |
| Plain text (.txt) | Supported |
| Word (.docx) | Planned |

## Verdicts

| Verdict | Meaning |
|---------|---------|
| SUPPORTED | Source confirms the claim |
| NOT_SUPPORTED | Source contradicts the claim or does not mention it |
| PARTIAL | Source partially supports (different numbers, missing nuance) |
| INCONCLUSIVE | Cannot determine with certainty |
| SOURCE_UNAVAILABLE | Source is behind paywall, 404, or timeout |

## Example Output

```json
{
  "summary": {
    "total_citations": 12,
    "supported": 8,
    "not_supported": 2,
    "partial": 1,
    "unavailable": 1
  },
  "results": [
    {
      "claim": "85% of enterprises use AI in 2025",
      "source_url": "https://mckinsey.com/...",
      "verdict": "PARTIAL",
      "confidence": 0.9,
      "explanation": "The source states 78%, not 85%",
      "source_quote": "78% of organizations have adopted AI..."
    }
  ]
}
```

## Limitations

- Cannot access paywalled sources (academic papers behind login, news sites with subscriptions)
- Physical book citations cannot be verified
- Quality depends on the LLM used
- Large documents with many citations cost more in API calls

## Cost Estimation

| Model | Cost per 1M tokens | Typical document (10 citations) |
|-------|-------------------|--------------------------------|
| Claude Sonnet | ~$3 | ~$0.05 |
| GPT-4o | ~$5 | ~$0.08 |
| Ollama (local) | Free | Free |

## Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Lint
ruff check src/

# Format
ruff format src/
```

## RAG System for Long Documents

For source documents longer than 8,000 characters, Citation Verifier automatically uses Retrieval-Augmented Generation (RAG):

1. **Chunking** - Document is split into overlapping chunks (500 chars each, 50 char overlap)
2. **Embedding** - Each chunk is embedded using sentence-transformers (local, no API costs)
3. **Retrieval** - For each claim, the top 5 most relevant chunks are found via cosine similarity
4. **Verification** - Only the relevant passages (up to 6,000 chars) are sent to the LLM

**Benefits:**
- ✅ More accurate verification by focusing on relevant content
- ✅ Lower costs (fewer tokens sent to LLM)
- ✅ Works with sources of any length
- ✅ Local embeddings (no external API required)

**Fallback:** If RAG fails, the system falls back to simple truncation at 8,000 characters.

## Project Structure

```
citation-verifier/
├── src/
│   ├── citation_verifier/
│   │   ├── models.py          # Data models
│   │   ├── cli.py             # CLI interface
│   │   ├── api.py             # REST API
│   │   ├── main.py            # Main verification workflow
│   │   ├── pipeline.py        # Document processing pipeline
│   │   ├── fetcher.py         # Source fetching
│   │   └── verifier.py        # Core verification logic
│   ├── parsers/               # Document parsers (MD, PDF, HTML)
│   ├── extractors/            # Claim extraction with LLM
│   ├── fetchers/              # Source fetching utilities
│   ├── analyzers/             # RAG system (chunker, retriever)
│   └── reporters/             # Output formatters (JSON, MD, terminal)
├── tests/                     # Test suite
├── examples/                  # Example documents
├── API_README.md             # REST API documentation
└── README.md                 # This file
```

## Roadmap

### ✅ Completed
- [x] Core verification engine
- [x] CLI interface with Typer
- [x] Markdown parser
- [x] PDF parser
- [x] HTML/URL parser
- [x] JSON/Markdown/Terminal reporters
- [x] REST API with FastAPI
- [x] RAG system for long documents
- [x] Embedding-based retrieval
- [x] Rich terminal output

### 🚧 Planned
- [ ] Web UI (Streamlit/Gradio)
- [ ] DOI/ArXiv support
- [ ] Source caching
- [ ] Batch processing
- [ ] OpenAI embeddings option
- [ ] Word (.docx) support

## Contributing

Contributions welcome. Please open an issue first to discuss what you want to change.

1. Fork the repo
2. Create your branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT
