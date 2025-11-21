"""Vector retrieval against Qdrant with optional document filter."""
import logging
from typing import Any, Dict, List, Optional

from app.services.embedings import embed_chunks
from app.services.vector_store import qdrant
from qdrant_client import models

logger = logging.getLogger(__name__)


async def retrieve_chunks(query: str, document_id: Optional[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
    document_id = document_id.strip() if document_id and document_id.strip() else None

    if qdrant is None:
        raise RuntimeError("Qdrant client is unavailable. Please start Qdrant before querying.")

    try:
        query_embedding = await embed_chunks(query)
        vector = query_embedding.tolist()
    except Exception as exc:
        logger.error("Failed to embed query: %s", exc)
        raise RuntimeError(f"Failed to embed query: {exc}") from exc

    q_filter = None
    if document_id:
        q_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="document_id",
                    match=models.MatchValue(value=document_id)
                )
            ]
        )

    try:
        response = qdrant.query_points(
            collection_name="palm_docs",
            query=vector,
            limit=top_k,
            with_payload=True,
            query_filter=q_filter
        )
    except Exception as exc:
        logger.error("Failed to query Qdrant: %s", exc)
        raise RuntimeError(f"Failed to query Qdrant: {exc}") from exc

    results = response.points

    chunks = []
    for item in results:
        chunks.append({
            "text": item.payload.get("text", ""),
            "document_id": item.payload.get("document_id"),
            "chunk_id": item.payload.get("chunk_id"),
            "score": item.score
        })

    return chunks
