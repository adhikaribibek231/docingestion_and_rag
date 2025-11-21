from app.services.embedings import embed_chunks
from app.services.vector_store import qdrant
from qdrant_client import models


async def retrieve_chunks(query: str, document_id: str | None = None, top_k: int = 5):
    # 1. Embed query → convert numpy → python list
    query_embedding = await embed_chunks(query)
    vector = query_embedding.tolist()
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

    # 4. Query Qdrant
    response = qdrant.query_points(
        collection_name="palm_docs",
        query=vector,              
        limit=top_k,
        with_payload=True,
        query_filter=q_filter       
    )

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
