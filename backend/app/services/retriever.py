from app.services.embedings import embed_chunks
from app.services.vector_store import qdrant
from qdrant_client import models

async def retrieve_chunks(query: str, top_k: int = 5):
    query_embedding = await embed_chunks(query)
    results = qdrant.search(
        collection_name="palm_docs",
        query_vector=query_embedding,
        limit=top_k,
    )
    chunks = []
    for item in results:
        chunks.append({
            "text": item.payload.get("text", ""),
            "document_id": item.payload.get("document_id"),
            "chunk_id": item.payload.get("chunk_id"),
            "score": item.score
        })
    return chunks
