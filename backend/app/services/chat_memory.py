import json
from app.core.redis_client import redis_client
def append_message(session_id: str, role: str, content: str):
    key = f"chat:{session_id}"
    message = json.dumps({"role": role, "content": content})
    redis_client.rpush(key, message)

def get_history(session_id: str):
    key = f"chat:{session_id}"
    messages = redis_client.lrange(key, 0, -1)
    return [json.loads(message) for message in messages]