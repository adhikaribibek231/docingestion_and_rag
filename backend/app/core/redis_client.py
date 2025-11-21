"""Redis client bootstrap with graceful fallback when Redis is down."""
import logging
import redis

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
except Exception as exc:
    redis_client = None
    logger.warning("Failed to initialize Redis client: %s", exc)
