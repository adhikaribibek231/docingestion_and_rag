from app.services.chat_memory import append_message, get_history
from app.services.retriever import retrieve_chunks
from app.services.prompt_builder import build_prompt
from app.services.llm import call_llm


async def answer_question(session_id: str, question: str, document_id: str | None, db):
    # Treat empty/whitespace IDs as absent so we only restrict when a real ID is provided.
    doc_id = document_id.strip() if document_id and document_id.strip() else None
    use_history = doc_id is None

    append_message(session_id, "user", question)
    history = get_history(session_id) if use_history else []

    try:
        retrieved_chunks = await retrieve_chunks(question, document_id=doc_id)
    except Exception as exc:
        raise RuntimeError(f"Retrieval failed: {exc}") from exc

    messages = build_prompt(history, retrieved_chunks, question)

    try:
        answer = await call_llm(messages)
    except Exception as exc:
        raise RuntimeError(f"LLM call failed: {exc}") from exc

    append_message(session_id, "assistant", answer)
    return {
        "answer": answer,
        "sources": retrieved_chunks
    }
