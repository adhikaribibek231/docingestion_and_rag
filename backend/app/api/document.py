from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query
from app.schema.document import docingest, ChunkStrategy
from app.services.text_extractor import extract_text_from_pdf
from app.services.chunker import chunk_text
from app.services.embedings import embed_chunks
from app.services.vector_store import store_vector, ensure_collection
router = APIRouter()

ensure_collection()

@router.post("/ingestion/", response_model = docingest)
async def ingest_document(
    file: UploadFile = File(...),
    chunking_strategy: ChunkStrategy = Query(default=ChunkStrategy.fixed)
):
    contents = await file.read()
    text = extract_text_from_pdf(contents)
    # print ('The length of text is:',len(text))

    chunks = chunk_text(text, chunking_strategy)
    if not chunks:
        raise HTTPException(status_code=400, detail="chunking failed, no chunks created")
    
    embeddings = await embed_chunks(chunks)
    if len(embeddings) != len(chunks):
        raise HTTPException(status_code=500, detail="embedding failed, not same number of embeddings and chunks")
    
    for i in range(len(chunks)):
        store_vector(
            id = i,
            vector = embeddings[i],
            payload = {
                "filename":file.filename,
                "chunk":chunks[i]
            }
        )
    print(f"Stored chunk {i} in Qdrant")

    return (
        docingest(
            document_id=file.filename,
            content=text,
            chunking_strategy=chunking_strategy,
            num_chunks= len(chunks)
        )
    )