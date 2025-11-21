from app.services.chat_memory import append_message, get_history
from app.services.retriever import retrieve_chunks
from app.services.prompt_builder import build_prompt
from app.services.llm import call_llm
async def answer_question(session_id: str, question: str, document_id: str | None, db):
    append_message(session_id, "user", question)
    history = get_history(session_id)
    retrieved_chunks = await retrieve_chunks(question)
    messages = build_prompt(history, retrieved_chunks, question)
    answer = await call_llm(messages)
    append_message(session_id, "assistant", answer)
    return {
        "answer": answer,
        "sources": retrieved_chunks
    }