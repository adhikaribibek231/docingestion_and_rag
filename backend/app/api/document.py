from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query
from app.schema.document import docingest, ChunkStrategy
from app.services.text_extractor import extract_text_from_pdf
from app.services.chunker import chunk_text
from app.services.embedings import embed_chunks
router = APIRouter()

@router.post("/ingestion/", response_model = docingest)
async def ingest_document(
    file: UploadFile = File(...),
    chunking_strategy: ChunkStrategy = Query(default=ChunkStrategy.fixed)
):
    contents = await file.read()
    text = extract_text_from_pdf(contents)
    print ('The length of text is:',len(text))

    chunks = chunk_text(text, chunking_strategy)
    if not chunks:
        raise HTTPException(status_code=400, detail="chunking failed, no chunks created")
    
    embeddings = await embed_chunks(chunks)
    if len(embeddings) != len(chunks):
        raise HTTPException(status_code=500, detail="embedding failed, not same number of embeddings and chunks")
    
    return (
        docingest(
            document_id=file.filename,
            content=text,
            chunking_strategy=chunking_strategy,
            num_chunks= len(chunks)
        )
    )