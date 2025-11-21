from app.services.embedings import embed_chunks
from app.services.vector_store import qdrant
from qdrant_client import models


async def retrieve_chunks(query: str, document_id: str | None = None, top_k: int = 5):
    # 1. Embed query → returns list, so take first vector
    query_embedding = await embed_chunks(query)
    vector = query_embedding[0]

    # 2. Optional filter
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

    # 3. Build query block
    query_block = models.QueryVector(
        vector=vector
    )

    # 4. Query Qdrant
    response = qdrant.query_points(
        collection_name="palm_docs",
        query=query_block,
        limit=top_k,
        with_payload=True
    )

    results = response.points

    chunks = []
    for item in results:
        chunks.append({
            "text": item.payload.get("chunk", ""),
            "document_id": item.payload.get("document_id"),
            "chunk_id": item.id,
            "score": item.score
        })

    return chunks
