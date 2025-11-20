from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query
from app.schema.document import docingest, ChunkStrategy
from app.services.text_extractor import extract_text_from_pdf
router = APIRouter()

@router.post("/ingestion/", response_model = docingest)
async def ingest_document(
    file: UploadFile = File(...),
    chunking_strategy: ChunkStrategy = Query(default=ChunkStrategy.fixed)
):
    contents = await file.read()
    text = extract_text_from_pdf(contents)
    print (len(text))
    return (
        docingest(
            document_id=file.filename,
            content=text,
            chunking_strategy=chunking_strategy
        )
    )