# Citation Verifier

An AI agent that verifies whether cited sources actually support the claims made in documents.

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

# Verify a URL
cite-verify check https://example.com/article

# Output as JSON
cite-verify check document.pdf --output json

# Use a specific model
cite-verify check document.md --model gpt-4o
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
uvicorn src.citation_verifier.api:app --reload

# Make a request
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{"claim": "80% of companies use AI", "source_url": "https://..."}'
```

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

## Project Structure

```
citation-verifier/
├── src/
│   └── citation_verifier/
│       ├── models.py          # Data models
│       ├── cli.py             # CLI interface
│       ├── api.py             # REST API
│       ├── parsers/           # Document parsers
│       ├── extractors/        # Claim extraction
│       ├── fetchers/          # Source fetching
│       ├── analyzers/         # RAG for long sources
│       ├── verifier/          # Core verification logic
│       └── reporters/         # Output formatting
├── tests/
├── examples/
└── README.md
```

## Roadmap

- [x] Core verification engine
- [x] CLI interface
- [x] Markdown parser
- [x] PDF parser
- [x] JSON/Markdown reports
- [ ] REST API
- [ ] Web UI
- [ ] DOI/ArXiv support
- [ ] Source caching
- [ ] Batch processing

## Contributing

Contributions welcome. Please open an issue first to discuss what you want to change.

1. Fork the repo
2. Create your branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT