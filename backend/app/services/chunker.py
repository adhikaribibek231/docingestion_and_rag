"""Chunking utilities to split text before embedding."""
import logging
from typing import List

from app.schema.document import ChunkStrategy
# https://www.nb-data.com/p/9-chunking-strategis-to-improve-rag

logger = logging.getLogger(__name__)


def chunk_fixed(text: str, chunk_size: int = 500) -> List[str]:
    """Split text by word count, no overlap."""
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]


def chunk_sentence(text: str) -> List[str]:
    """Use spaCy sentence boundaries to chunk."""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
    except Exception as exc:
        raise RuntimeError("spaCy model 'en_core_web_sm' is not available. Please install it before using sentence chunking.") from exc
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]


def chunk_sliding(text: str, chunk_size: int = 500, overlap: int = 200) -> List[str]:
    """Sliding window chunks with overlap to preserve context."""
    words = text.split()
    chunks = []
    step = chunk_size - overlap
    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks


def chunk_text(text: str, strategy: ChunkStrategy) -> List[str]:
    """Route to the chosen chunking strategy."""
    if strategy == ChunkStrategy.fixed:
        return chunk_fixed(text)
    if strategy == ChunkStrategy.sliding:
        return chunk_sliding(text)
    if strategy == ChunkStrategy.sentence:
        return chunk_sentence(text)
    logger.error("Unknown chunking strategy: %s", strategy)
    raise ValueError("Unknown chunking strategy")
