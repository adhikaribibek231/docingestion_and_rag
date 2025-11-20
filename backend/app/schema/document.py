from pydantic import BaseModel
from enum import Enum

class ChunkStrategy(str, Enum):
    fixed = "fixed"
    sentence = "sentence"
    sliding = "sliding"

class docingest(BaseModel):
    document_id: str
    content: str
    chunking_strategy: ChunkStrategy
    num_chunks: int