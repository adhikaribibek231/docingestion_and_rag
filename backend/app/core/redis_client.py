import redis

from app.core.config import settings

try:
    redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
except Exception as exc:
    redis_client = None
    print(f"Failed to initialize Redis client: {exc}")
