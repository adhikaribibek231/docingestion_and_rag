from qdrant_client import QdrantClient, models

qdrant = QdrantClient(url="http://localhost:6333", timeout=20)

def ensure_collection(name = "palm_docs", vector_size = 384):
    if not qdrant.collection_exists(name):
        qdrant.create_collection(
            collection_name = name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE
                            )
        )
    return True
def store_vector (id, vector, payload, name="palm_docs"):
    qdrant.upsert(
        collection_name=name,
        points=[
            models.PointStruct(
                id=id,
                vector=vector,
                payload=payload
            )
        ]
    )