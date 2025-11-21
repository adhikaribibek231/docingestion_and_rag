"""Chat history helpers stored in Redis."""
import logging
import json
from typing import List

from redis import RedisError

from app.core.redis_client import redis_client

logger = logging.getLogger(__name__)


def append_message(session_id: str, role: str, content: str) -> None:
    key = f"chat:{session_id}"
    message = json.dumps({"role": role, "content": content})
    try:
        if redis_client is None:
            raise RuntimeError("Redis client not initialized.")
        redis_client.rpush(key, message)
    except RedisError as exc:
        # Fail closed so we do not crash the request if Redis is down.
        logger.warning("Redis unavailable while appending message: %s", exc)
    except Exception as exc:
        logger.error("Unexpected error while appending message: %s", exc)


def get_history(session_id: str) -> List[dict]:
    key = f"chat:{session_id}"
    try:
        if redis_client is None:
            raise RuntimeError("Redis client not initialized.")
        messages = redis_client.lrange(key, 0, -1)
    except RedisError as exc:
        logger.warning("Redis unavailable while fetching history: %s", exc)
        return []
    except Exception as exc:
        logger.error("Unexpected error while fetching history: %s", exc)
        return []
    return [json.loads(message) for message in messages]
