import json
from typing import List

from redis import RedisError

from app.core.redis_client import redis_client


def append_message(session_id: str, role: str, content: str):
    key = f"chat:{session_id}"
    message = json.dumps({"role": role, "content": content})
    try:
        if redis_client is None:
            raise RuntimeError("Redis client not initialized.")
        redis_client.rpush(key, message)
    except RedisError as exc:
        # Fail closed so we do not crash the request if Redis is down.
        print(f"Redis unavailable while appending message: {exc}")
    except Exception as exc:
        print(f"Unexpected error while appending message: {exc}")


def get_history(session_id: str) -> List[dict]:
    key = f"chat:{session_id}"
    try:
        if redis_client is None:
            raise RuntimeError("Redis client not initialized.")
        messages = redis_client.lrange(key, 0, -1)
    except RedisError as exc:
        print(f"Redis unavailable while fetching history: {exc}")
        return []
    except Exception as exc:
        print(f"Unexpected error while fetching history: {exc}")
        return []
    return [json.loads(message) for message in messages]
