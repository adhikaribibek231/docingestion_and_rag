from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query
from app.schema.document import DocIngest, ChunkStrategy
from app.services.text_extractor import extract_text_from_pdf
from app.services.chunker import chunk_text
from app.services.embedings import embed_chunks
from app.services.vector_store import store_vector, ensure_collection
from app.db.session import get_session
from sqlmodel import Session
from uuid import uuid4
from app.models.document import Document

router = APIRouter()

ensure_collection()

@router.post("/ingestion/", response_model = DocIngest)
async def ingest_document(
    file: UploadFile = File(...),
    chunking_strategy: ChunkStrategy = Query(default=ChunkStrategy.fixed),
    session: Session = Depends(get_session)
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
    
    external_id = str(uuid4())
    doc = Document(
        filename=file.filename,
        external_id=external_id,
        content_type=file.content_type
    )
    session.add(doc)
    session.commit()

    for i in range(len(chunks)):
        store_vector(
            # id=f"{external_id}-{i}",
            id=str(uuid4()),
            # id =i,
            vector=embeddings[i],
            payload={
                "text": chunks[i],
                "document_id": external_id,
                "chunk_id": i,
                "filename": file.filename
            }
        )


    return DocIngest(
        document_id=file.filename,
        external_id=external_id,
        chunking_strategy=chunking_strategy,
        num_chunks=len(chunks),
        status="Document ingested successfully"
    )
