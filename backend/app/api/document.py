from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query
from app.schema.document import DocIngest, ChunkStrategy
from app.services.text_extractor import extract_text
from app.services.chunker import chunk_text
from app.services.embedings import embed_chunks
from app.services.vector_store import store_vector, ensure_collection
from app.db.session import get_session
from sqlmodel import Session
from uuid import uuid4
from app.models.document import Document

router = APIRouter()

try:
    ensure_collection()
except Exception as exc:
    print(f"Qdrant collection bootstrap failed: {exc}")

@router.post("/ingestion/", response_model = DocIngest)
async def ingest_document(
    file: UploadFile = File(...),
    chunking_strategy: ChunkStrategy = Query(default=ChunkStrategy.fixed),
    session: Session = Depends(get_session)
):
    contents = await file.read()
    try:
        text = extract_text(contents, content_type=file.content_type, filename=file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to extract text from file")
    # print ('The length of text is:',len(text))

    try:
        ensure_collection()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Vector store unavailable: {exc}")

    try:
        chunks = chunk_text(text, chunking_strategy)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chunking failed: {exc}")
    if not chunks:
        raise HTTPException(status_code=400, detail="chunking failed, no chunks created")
    
    try:
        embeddings = await embed_chunks(chunks)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {exc}")
    if len(embeddings) != len(chunks):
        raise HTTPException(status_code=500, detail="embedding failed, not same number of embeddings and chunks")
    
    external_id = str(uuid4())
    doc = Document(
        filename=file.filename,
        external_id=external_id,
        content_type=file.content_type
    )
    try:
        session.add(doc)
        session.commit()
    except Exception as exc:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to persist document metadata: {exc}")

    for i in range(len(chunks)):
        try:
            store_vector(
                id=str(uuid4()),
                vector=embeddings[i],
                payload={
                    "text": chunks[i],
                    "document_id": external_id,
                    "chunk_id": i,
                    "filename": file.filename
                }
            )
        except Exception as exc:
            session.rollback()
            raise HTTPException(status_code=503, detail=f"Failed to store vector: {exc}")


    return DocIngest(
        document_id=external_id,
        external_id=external_id,
        chunking_strategy=chunking_strategy,
        num_chunks=len(chunks),
        status="Document ingested successfully"
    )
