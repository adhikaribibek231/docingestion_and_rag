from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

async def embed_chunks(chunks):
    embeddings = model.encode(chunks)
    return embeddings