from typing import Iterable, List, Union

from sentence_transformers import SentenceTransformer

try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as exc:
    model = None
    print(f"Failed to load embedding model: {exc}")


async def embed_chunks(chunks: Union[str, Iterable[str]]):
    if model is None:
        raise RuntimeError("Embedding model is not available. Ensure sentence-transformers assets are installed.")

    try:
        embeddings = model.encode(chunks)
        return embeddings
    except Exception as exc:
        raise RuntimeError(f"Failed to generate embeddings: {exc}") from exc
