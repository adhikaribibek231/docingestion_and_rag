"""RAG pipeline: grab history, retrieve context, and ask the LLM for an answer."""
import logging
from typing import Any, Dict, Optional

from app.services.chat_memory import append_message, get_history
from app.services.retriever import retrieve_chunks
from app.services.prompt_builder import build_prompt
from app.services.llm import call_llm

logger = logging.getLogger(__name__)


async def answer_question(session_id: str, question: str, document_id: Optional[str], db: Any) -> Dict[str, Any]:
    """Retrieve relevant context and ask the LLM to answer the user's question."""
    # db is accepted for interface symmetry; the flow is read-only right now.
    logger.info("Answering question for session %s", session_id)
    # Treat empty/whitespace IDs as absent so we only restrict when a real ID is provided.
    doc_id = document_id.strip() if document_id and document_id.strip() else None

    append_message(session_id, "user", question)
    # Always use the session history so multi-turn flows work even when switching documents.
    history = get_history(session_id)

    try:
        retrieved_chunks = await retrieve_chunks(question, document_id=doc_id)
    except Exception as exc:
        logger.error("Retrieval failed for session %s: %s", session_id, exc)
        raise RuntimeError(f"Retrieval failed: {exc}") from exc

    messages = build_prompt(history, retrieved_chunks, question)

    try:
        answer = await call_llm(messages)
    except Exception as exc:
        logger.error("LLM call failed for session %s: %s", session_id, exc)
        raise RuntimeError(f"LLM call failed: {exc}") from exc

    append_message(session_id, "assistant", answer)
    logger.debug("RAG answer produced for session %s", session_id)
    return {
        "answer": answer,
        "sources": retrieved_chunks
    }
