from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query
from app.schema.document import docingest, ChunkStrategy

router = APIRouter()

@router.post("/ingestion/", response_model = docingest)
async def ingest_document(
    file: UploadFile = File(...),
    chunking_strategy: ChunkStrategy = Query(default=ChunkStrategy.fixed)
):
    return 'dummy response'