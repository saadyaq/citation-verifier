# Citation Verifier REST API

A REST API for verifying citations using AI.

## Quick Start

### Start the server

```bash
# Development
uvicorn citation_verifier.api:app --reload

# Production  
uvicorn citation_verifier.api:app --host 0.0.0.0 --port 8000
```

### API Documentation

Once running, visit:
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### Health Check

```bash
curl http://localhost:8000/health
```

### Verify a Document

Verify all citations in a document (Markdown, PDF, or URL):

```bash
curl -X POST http://localhost:8000/verify/document \
  -H "Content-Type: application/json" \
  -d '{
    "source": "path/to/document.md",
    "model": "claude-3-5-haiku-20241022"
  }'
```

Response:
```json
{
  "summary": {
    "total_citations": 5,
    "supported": 3,
    "partial": 1,
    "not_supported": 1
  },
  "results": [
    {
      "claim": "80% of companies use AI",
      "source_url": "https://example.com/study",
      "verdict": "partial",
      "confidence": 0.85,
      "explanation": "Source states 78%, not 80%",
      "source_quote": "78% of surveyed companies..."
    }
  ],
  "processing_time_seconds": 12.34
}
```

### Verify a Single Claim

Verify one claim against a source:

```bash
curl -X POST http://localhost:8000/verify/claim \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "Python is the most popular programming language",
    "source_url": "https://www.python.org/about/",
    "model": "claude-3-5-haiku-20241022"
  }'
```

Response:
```json
{
  "claim": "Python is the most popular programming language",
  "source_url": "https://www.python.org/about/",
  "verdict": "supported",
  "confidence": 0.92,
  "explanation": "The source confirms Python's popularity...",
  "source_quote": "Python is one of the most popular..."
}
```

## Verdicts

| Verdict | Description |
|---------|-------------|
| `supported` | Source confirms the claim |
| `not_supported` | Source contradicts or doesn't mention the claim |
| `partial` | Source partially supports (different numbers, missing nuance) |
| `inconclusive` | Cannot determine with certainty |
| `source_unavailable` | Source is behind paywall, 404, timeout, etc. |

## Configuration

Set your API key:

```bash
export ANTHROPIC_API_KEY=your-key-here
```

Or create a `.env` file:

```env
ANTHROPIC_API_KEY=your-key-here
```

## CORS

The API allows all origins by default. For production, update the CORS settings in `api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specify allowed origins
    ...
)
```

## Error Handling

The API returns standard HTTP status codes:

- `200`: Success
- `404`: File/resource not found  
- `500`: Internal server error (verification failed)

Error response format:

```json
{
  "detail": "Error message here"
}
```
