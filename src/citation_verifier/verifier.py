import anthropic
from .models import ClaimCitation, SourceContent, VerificationResult, Verdict

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

    if source.fetch != "success" or not source.content:
        return VerificationResult(
            claim = claim ,
            verdict = Verdict.SOURCE_UNAVAILABLE,
            confidence=1.0,
            explanation = f"Source unavailable : {source.fetch_status}"
        )
    
    