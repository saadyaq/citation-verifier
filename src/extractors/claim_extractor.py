import json
from anthropic import Anthropic
from citation_verifier.models import ClaimCitation
from dotenv import load_dotenv
import os 
load_dotenv()

# Verify API key exists
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")


EXTRACTION_PROMPT="""Analyse ce document et extrais TOUTES les affirmations qui citent une source externe.

DOCUMENT:
{document_text}

Pour chaque affirmation qui cite une source (URL, référence, étude mentionnée), retourne:
- claim_text: l'affirmation exacte faite dans le document
- citation_url: l'URL de la source (si disponible)
- citation_ref: la référence si pas d'URL (ex: "[1]", "selon McKinsey", "une étude de Harvard")
- original_context: la phrase complète contenant l'affirmation

Réponds UNIQUEMENT en JSON avec ce format:
{{
    "claims": [
        {{
            "claim_text": "...",
            "citation_url": "https://..." ou null,
            "citation_ref": "..." ou null,
            "original_context": "..."
        }}
    ]
}}

Règles:
- Ignore les affirmations sans source citée
- Ignore les liens internes (navigation, ancres)
- Inclus les références de type [1], [2] si elles pointent vers des sources
- Si une URL est dans le texte, extrais-la exactement

Réponds UNIQUEMENT avec le JSON."""

def extract_claims( document_text:str , model : str ="claude-3-5-haiku-20241022") -> list[ClaimCitation]:

    """Extract claim/citation pairs of a document"""

    client = Anthropic(api_key=api_key)

    text = document_text[:15000] if len(document_text) > 15000 else document_text
    
    try:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": EXTRACTION_PROMPT.format(document_text=text)
            }]
        )

        result = json.loads(response.content[0].text)

        claims = []
        for item in result.get("claims", []):
            # Skip items without required fields
            if "claim_text" not in item or "original_context" not in item:
                continue

            claims.append(ClaimCitation(
                claim_text=item["claim_text"],
                citation_url=item.get("citation_url"),
                citation_ref=item.get("citation_ref"),
                original_context=item["original_context"]
            ))

        return claims

    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON response from Claude: {e}")
        return []
    except KeyError as e:
        print(f"Error: Missing expected field in response: {e}")
        return []
    except Exception as e:
        print(f"Error during claim extraction: {e}")
        return []