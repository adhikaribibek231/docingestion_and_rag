from pydantic import BaseModel
from enum import Enum

class ChunkStrategy(str, Enum):
    fixed = "fixed"
    sentence = "sentence"
    sliding = "sliding"

class DocIngest(BaseModel):
    document_id: str
    external_id: str
    chunking_strategy: ChunkStrategy
    num_chunks: int
    status: str
