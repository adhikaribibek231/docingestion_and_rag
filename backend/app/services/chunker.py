from app.schema.document import ChunkStrategy
# https://www.nb-data.com/p/9-chunking-strategis-to-improve-rag

def chunk_fixed(text:str, chunk_size:int=500):
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def chunk_sentence(text):
    import spacy
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]

def chunk_sliding(text:str, chunk_size:int=500, overlap:int=200):
    words = text.split()
    chunks = []
    step = chunk_size - overlap 
    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

def chunk_text(text:str, strategy: ChunkStrategy):
    if strategy == ChunkStrategy.fixed:
        return chunk_fixed(text)
    if strategy == ChunkStrategy.sliding:
        return chunk_sliding(text)
    if strategy == ChunkStrategy.sentence:
        return chunk_sentence(text)
    raise ValueError("Unknown chunking strategy")