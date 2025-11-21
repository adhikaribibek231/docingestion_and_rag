Absolutely — here is a **clean, polished, company-neutral README.md** you can use for:

✔ Your GitHub
✔ Your resume portfolio
✔ Technical interviews
✔ Showcasing backend, RAG, and LLM engineering skills

No Palm Mind references.
Professional, simple, clean.

---

# 📚 Document Ingestion + RAG Backend

*A modular backend that ingests documents, stores embeddings, answers questions using a custom RAG pipeline, supports multi-turn chat memory, and performs LLM-powered interview booking.*

Built with **FastAPI**, **Qdrant**, **Redis**, **SQLite**, and **DeepSeek-R1:1.5B via Ollama**.

---

# 🌟 Features

### ✔ Document Ingestion API

Upload PDFs or TXT files → extract text → chunk → embed → store in Qdrant.

### ✔ Conversational RAG API

Custom retrieval-augmented generation pipeline built without FAISS, Chroma, or LangChain RetrievalQAChain.

### ✔ Multi-turn Chat Memory

Each conversation uses a session ID, and history is stored in Redis.

### ✔ LLM-Powered Booking System

Extracts name, email, date, and time from natural language and stores bookings in SQLite.

### ✔ Clean, Modular Architecture

Services for embeddings, chunking, vector store, LLM access, intent detection, booking, etc.

---

# 🧩 Tech Stack

**Backend Framework:** FastAPI
**LLM:** DeepSeek-R1:1.5B via Ollama
**Embeddings:** MiniLM (HuggingFace)
**Vector Store:** Qdrant
**Memory:** Redis
**Database:** SQLite (SQLModel ORM)

All components run locally — no cloud services required.

---

# 🛠️ 1. First-Time Setup

### Clone the repository

```
git clone https://github.com/adhikaribibek231/docingestion_and_rag.git
cd docingestion_and_rag/backend
```

### Create & activate a Python virtual environment

```
python -m venv .venv
.\.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Install Ollama + DeepSeek-R1 model

```
ollama pull deepseek-r1:1.5b
```

### Install Docker Desktop

Required for Qdrant and Redis.

---

# 🔁 2. How to Run (Every Session)

Start each service in its own terminal window.

### Terminal 1 — Qdrant (Vector DB)

```
docker run -p 6333:6333 qdrant/qdrant
```

### Terminal 2 — Redis (Chat Memory)

```
docker run -p 6379:6379 redis
```

### Terminal 3 — Ollama Server

```
ollama serve
```

### Terminal 4 — DeepSeek Model

```
ollama run deepseek-r1:1.5b
```

### Terminal 5 — FastAPI Server

```
cd docingestion_and_rag/backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload
```

API documentation:
👉 [http://localhost:8000/docs](http://localhost:8000/docs)

---

# 🧪 3. API Usage

## Health Check

```
GET /health
```

---

## A) Ingest a document

```
POST /documents/ingest?chunk_strategy=fixed
```

Supports:
• PDF
• TXT

Example:

```
curl -X POST "http://localhost:8000/documents/ingest?chunk_strategy=fixed" ^
-F "file=@C:/path/to/document.txt"
```

Response:

```
{
  "document_id": "abc123",
  "num_chunks": 5,
  "chunk_strategy": "fixed"
}
```

---

## B) Ask a question (RAG)

```
POST /chat/message
```

Example:

```
{
  "session_id": "demo1",
  "query": "What does the document say?",
  "document_id": "abc123"
}
```

The backend:
• retrieves relevant chunks from Qdrant
• builds a custom prompt
• generates answers using DeepSeek-R1
• maintains chat history in Redis

---

## C) Book an interview (LLM extraction)

```
{
  "session_id": "book1",
  "query": "Book an interview tomorrow at 10am for Alex. Email alex@example.com"
}
```

Response:

```
{
  "answer": "Your interview with Alex (alex@example.com) is booked on 2025-11-19 at 10:00.",
  "session_id": "book1"
}
```

Booking is saved in SQLite.

---

# 📂 4. Data Storage

**SQLite (`backend/PMrag.db`)**
Stores:
• Document metadata
• Bookings

**Qdrant** ([http://localhost:6333](http://localhost:6333))
Stores:
• Embeddings
• Chunk metadata

**Redis**
Stores:
• Chat history
• Booking drafts

---

# 🔍 5. Example Queries to Try

### Document comprehension

“Summarize this document.”
“What are the main points?”
“What does the last section mean?”

### Follow-up questions (same session_id)

“Explain that more simply.”
“Give me an example.”

### Booking

“Schedule an interview at 3pm tomorrow.”
“It’s for Maya, email [maya@example.com](mailto:maya@example.com).”

---

---

# ✅ 6. Completed Capabilities

| Capability                | Status |
| ------------------------- | ------ |
| PDF/TXT ingestion         | ✔      |
| Text extraction           | ✔      |
| Chunking (fixed + window) | ✔      |
| Embeddings generation     | ✔      |
| Qdrant storage            | ✔      |
| Custom RAG pipeline       | ✔      |
| Redis multi-turn memory   | ✔      |
| LLM-powered booking       | ✔      |
| SQLite persistence        | ✔      |
| No Chroma / No FAISS      | ✔      |
| No RetrievalQAChain       | ✔      |

---

