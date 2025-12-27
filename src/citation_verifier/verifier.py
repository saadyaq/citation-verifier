import anthropic
from .models import ClaimCitation, SourceContent, VerificationResult, Verdict
from dotenv import load_dotenv
import os

load_dotenv()

# Verify API key exists
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

client = anthropic.Anthropic(api_key=api_key)
print("✓ Claude API client initialized successfully")

VERIFICATION_PROMPT= """Tu es un vérificateur de citations. Ta tâche est de déterminer si une source citée supporte réellement l'affirmation faite.

AFFIRMATION À VÉRIFIER:
{claim}

CONTENU DE LA SOURCE CITÉE:
{source_content}

Analyse si la source supporte l'affirmation. Réponds en JSON avec ce format exact:
{{
    "verdict": "supported|not_supported|partial|inconclusive",
    "confidence": 0.0-1.0,
    "explanation": "Explication claire de ton verdict",
    "source_quote": "Citation exacte de la source qui justifie ton verdict (ou null)"
}}

Critères:
- SUPPORTED: La source dit explicitement ce que l'affirmation prétend
- NOT_SUPPORTED: La source contredit l'affirmation ou ne mentionne pas le sujet
- PARTIAL: La source supporte partiellement (chiffres différents, nuances omises)
- INCONCLUSIVE: Impossible de déterminer avec certitude

Réponds UNIQUEMENT avec le JSON, rien d'autre."""

async def verify_claim(
        claim : ClaimCitation,
        source : SourceContent,
        model : str ="claude-3-5-haiku-20241022"
) -> VerificationResult:
    """Verify if a source support the claim """

    if source.fetch_status != "success" or not source.content:
        return VerificationResult(
            claim = claim ,
            verdict = Verdict.SOURCE_UNAVAILABLE,
            confidence=1.0,
            explanation = f"Source unavailable : {source.fetch_status}"
        )

    # Use RAG for long documents
    if len(source.content) > 8000:
        try:
            from analyzers.retriever import get_relevant_context
            content = get_relevant_context(claim.claim_text, source.content, max_context_chars=6000)
            print(f"  Using RAG: Retrieved {len(content)} chars of relevant context")
        except Exception as e:
            # Fallback to truncation if RAG fails
            print(f"  RAG retrieval failed: {e}, falling back to truncation")
            content = source.content[:8000]
    else:
        content = source.content
    client = anthropic.Anthropic(api_key=api_key)
    print("Claude API client initialized successfully")

    response = client.messages.create(
        model = model ,
        max_tokens = 1024 ,
        messages = [{
            "role" : "user",
            "content" : VERIFICATION_PROMPT.format(
                claim = claim.claim_text,
                source_content = content
            )
        }]
    )

    import json
    result_data = json.loads(response.content[0].text)

    return VerificationResult(
        claim=claim.model_dump(),
        verdict=Verdict(result_data["verdict"]),
        confidence=result_data["confidence"],
        explanation=result_data["explanation"],
        source_quote=result_data.get("source_quote")
    )