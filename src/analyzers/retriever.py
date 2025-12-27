"""RAG retriever for finding relevant passages in source documents."""
from typing import List, Optional
from dataclasses import dataclass
import os


@dataclass
class RelevantPassage:
    """Represents a relevant passage found in the source."""
    text: str
    chunk_id: int
    relevance_score: float


class EmbeddingRetriever:
    """Retrieves relevant passages using embeddings and similarity search."""
    
    def __init__(self, use_local: bool = True):
        """Initialize the retriever.
        
        Args:
            use_local: If True, use local embeddings (sentence-transformers).
                      If False, use OpenAI embeddings (requires API key).
        """
        self.use_local = use_local
        self._model = None
        self._embeddings = None
        
    def _load_model(self):
        """Lazy load the embedding model."""
        if self._model is not None:
            return
            
        if self.use_local:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. "
                    "Install with: pip install sentence-transformers"
                )
        else:
            # TODO: Implement OpenAI embeddings
            raise NotImplementedError("OpenAI embeddings not yet implemented")
    
    def _embed_texts(self, texts: List[str]) -> List:
        """Generate embeddings for a list of texts."""
        self._load_model()
        return self._model.encode(texts, convert_to_numpy=True)
    
    def find_relevant_passages(
        self,
        query: str,
        chunks: List,  # List of TextChunk
        top_k: int = 3,
        min_score: float = 0.3
    ) -> List[RelevantPassage]:
        """Find the most relevant passages for a query.
        
        Args:
            query: The search query (e.g., the claim to verify)
            chunks: List of TextChunk objects to search
            top_k: Number of top results to return
            min_score: Minimum relevance score (0-1) to include
            
        Returns:
            List of RelevantPassage objects, sorted by relevance
        """
        if not chunks:
            return []
        
        # Generate embeddings for chunks
        chunk_texts = [chunk.text for chunk in chunks]
        chunk_embeddings = self._embed_texts(chunk_texts)
        
        # Generate embedding for query
        query_embedding = self._embed_texts([query])[0]
        
        # Calculate cosine similarity
        from numpy import dot
        from numpy.linalg import norm
        
        similarities = []
        for i, chunk_emb in enumerate(chunk_embeddings):
            similarity = dot(query_embedding, chunk_emb) / (norm(query_embedding) * norm(chunk_emb))
            similarities.append((i, float(similarity)))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Build result list
        results = []
        for chunk_idx, score in similarities[:top_k]:
            if score >= min_score:
                results.append(RelevantPassage(
                    text=chunks[chunk_idx].text,
                    chunk_id=chunks[chunk_idx].chunk_id,
                    relevance_score=score
                ))
        
        return results


def get_relevant_context(
    claim: str,
    source_text: str,
    max_context_chars: int = 4000,
    use_local_embeddings: bool = True
) -> str:
    """Get relevant context from source text for a claim.
    
    This is a convenience function that chunks the source and finds relevant passages.
    
    Args:
        claim: The claim to verify
        source_text: The full source text
        max_context_chars: Maximum characters to return
        use_local_embeddings: Whether to use local embeddings
        
    Returns:
        Combined relevant passages from the source
    """
    from .chunker import chunk_text
    
    # Chunk the source text
    chunks = chunk_text(source_text, chunk_size=500, overlap=50)
    
    # Find relevant passages
    retriever = EmbeddingRetriever(use_local=use_local_embeddings)
    passages = retriever.find_relevant_passages(claim, chunks, top_k=5)
    
    # Combine passages up to max_context_chars
    combined_text = []
    total_chars = 0
    
    for passage in passages:
        if total_chars + len(passage.text) > max_context_chars:
            break
        combined_text.append(passage.text)
        total_chars += len(passage.text) + 2  # +2 for \n\n separator
    
    return '\n\n'.join(combined_text) if combined_text else source_text[:max_context_chars]
