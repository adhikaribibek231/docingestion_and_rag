from typing import Optional

from qdrant_client import QdrantClient, models
from qdrant_client.http import exceptions as qdrant_exceptions

try:
    qdrant: Optional[QdrantClient] = QdrantClient(url="http://localhost:6333", timeout=40)
except Exception as exc:
    qdrant = None
    print(f"Failed to initialize Qdrant client: {exc}")


def _require_client() -> QdrantClient:
    if qdrant is None:
        raise RuntimeError("Qdrant is unavailable. Ensure the service is running at http://localhost:6333.")
    return qdrant


def ensure_collection(name: str = "palm_docs", vector_size: int = 384):
    client = _require_client()
    try:
        if not client.collection_exists(name):
            client.create_collection(
                collection_name=name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE
                ),
            )
        return True
    except qdrant_exceptions.UnexpectedResponse as exc:
        raise RuntimeError(f"Qdrant rejected the collection request: {exc}") from exc
    except Exception as exc:
        raise RuntimeError(f"Failed to ensure Qdrant collection '{name}': {exc}") from exc


def store_vector(id, vector, payload, name: str = "palm_docs"):
    client = _require_client()
    try:
        client.upsert(
            collection_name=name,
            points=[
                models.PointStruct(
                    id=id,
                    vector=vector,
                    payload=payload
                )
            ]
        )
    except qdrant_exceptions.UnexpectedResponse as exc:
        raise RuntimeError(f"Qdrant upsert rejected: {exc}") from exc
    except Exception as exc:
        raise RuntimeError(f"Failed to store vector in Qdrant: {exc}") from exc
