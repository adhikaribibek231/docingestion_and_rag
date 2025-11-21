"""Schemas describing document ingestion requests/responses."""
from pydantic import BaseModel
from enum import Enum

class ChunkStrategy(str, Enum):
    """Supported ways to split a document."""
    fixed = "fixed"
    sentence = "sentence"
    sliding = "sliding"

class DocIngest(BaseModel):
    """Result of ingesting a document into the vector store."""
    document_id: str
    external_id: str
    chunking_strategy: ChunkStrategy
    num_chunks: int
    status: str
