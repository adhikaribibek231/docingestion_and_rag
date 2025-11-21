def build_prompt(history, retrieved_chunks, question):
    system_message = {
            "role": "system",
            "content": (
                "You are a helpful assistant that answers ONLY using the provided context. "
                "Use chat history only for conversational continuity, not as a factual source. "
                "If the context does not contain the answer, reply: 'I don't have information about that.'"
            )
        }
    chunk_text = [chunk['text'] for chunk in retrieved_chunks]
    context_str="\n\n---\n\n".join(chunk_text)
    context_message = {
            "role": "system",
            "content": f"Context:\n\n{context_str}"
        }
    history_messages = []
    recent_history = history[-6:]
    for item in recent_history:
        history_messages.append({
            "role": item['role'],
            "content": item['content']
        })
    user_message = {
            "role": "user",
            "content": question
        }
    return [system_message, context_message] + history_messages + [user_message]
