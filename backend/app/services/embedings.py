"""Embedding helper using sentence-transformers."""
import logging
from typing import Iterable, Union

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as exc:
    model = None
    logger.error("Failed to load embedding model: %s", exc)


async def embed_chunks(chunks: Union[str, Iterable[str]]):
    """Encode text or chunks into dense vectors."""
    if model is None:
        raise RuntimeError("Embedding model is not available. Ensure sentence-transformers assets are installed.")

    try:
        embeddings = model.encode(chunks)
        return embeddings
    except Exception as exc:
        logger.error("Failed to generate embeddings: %s", exc)
        raise RuntimeError(f"Failed to generate embeddings: {exc}") from exc
