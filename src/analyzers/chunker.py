"""Document chunking utilities for RAG."""
from dataclasses import dataclass
from typing import List


@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""
    text: str
    chunk_id: int
    start_char: int
    end_char: int


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> List[TextChunk]:
    """Split text into overlapping chunks for better context preservation.
    
    Args:
        text: The text to chunk
        chunk_size: Target size for each chunk in characters
        overlap: Number of overlapping characters between chunks
        
    Returns:
        List of TextChunk objects
    """
    if not text or len(text) <= chunk_size:
        return [TextChunk(text=text, chunk_id=0, start_char=0, end_char=len(text))]
    
    chunks = []
    chunk_id = 0
    start = 0
    
    while start < len(text):
        # Calculate end position for this chunk
        end = min(start + chunk_size, len(text))
        
        # Try to break at a sentence or word boundary
        if end < len(text):
            # Look for sentence end (.  ! ?)
            last_period = text.rfind('. ', start, end)
            last_exclaim = text.rfind('! ', start, end)
            last_question = text.rfind('? ', start, end)
            
            sentence_end = max(last_period, last_exclaim, last_question)
            
            if sentence_end > start:
                end = sentence_end + 2  # Include the punctuation and space
            else:
                # Fall back to word boundary
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space
        
        chunk_text = text[start:end].strip()
        
        if chunk_text:  # Only add non-empty chunks
            chunks.append(TextChunk(
                text=chunk_text,
                chunk_id=chunk_id,
                start_char=start,
                end_char=end
            ))
            chunk_id += 1
        
        # Move start position (with overlap)
        start = end - overlap if end < len(text) else end
        
        # Avoid infinite loop
        if start == end:
            break
    
    return chunks


def chunk_by_paragraphs(text: str, max_chunk_size: int = 1000) -> List[TextChunk]:
    """Chunk text by paragraphs, combining small paragraphs.
    
    Args:
        text: The text to chunk
        max_chunk_size: Maximum size for combined paragraphs
        
    Returns:
        List of TextChunk objects
    """
    # Split by double newlines (paragraphs)
    paragraphs = text.split('\n\n')
    
    chunks = []
    chunk_id = 0
    current_chunk = []
    current_size = 0
    start_char = 0
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        para_size = len(para)
        
        # If adding this paragraph exceeds max size, save current chunk
        if current_size + para_size > max_chunk_size and current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append(TextChunk(
                text=chunk_text,
                chunk_id=chunk_id,
                start_char=start_char,
                end_char=start_char + len(chunk_text)
            ))
            chunk_id += 1
            start_char += len(chunk_text) + 2  # +2 for \n\n
            current_chunk = []
            current_size = 0
        
        current_chunk.append(para)
        current_size += para_size + 2  # +2 for \n\n separator
    
    # Add remaining chunk
    if current_chunk:
        chunk_text = '\n\n'.join(current_chunk)
        chunks.append(TextChunk(
            text=chunk_text,
            chunk_id=chunk_id,
            start_char=start_char,
            end_char=start_char + len(chunk_text)
        ))
    
    return chunks if chunks else [TextChunk(text=text, chunk_id=0, start_char=0, end_char=len(text))]
