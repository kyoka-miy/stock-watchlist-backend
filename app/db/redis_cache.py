import json
import logging
import redis
from app.config import settings


logger = logging.getLogger("uvicorn.error")


class RedisCache:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        self.ttl = settings.REDIS_TTL

    def check_connection(self) -> bool:
        try:
            pong = self.client.ping()
            logger.info(
                "Redis connection succeeded: host=%s port=%s db=%s ping=%s",
                settings.REDIS_HOST,
                settings.REDIS_PORT,
                settings.REDIS_DB,
                pong,
            )
            return True
        except Exception:
            logger.exception(
                "Redis connection failed: host=%s port=%s db=%s",
                settings.REDIS_HOST,
                settings.REDIS_PORT,
                settings.REDIS_DB,
            )
            return False

    def get(self, key: str):
        value = self.client.get(key)

        if value is None:
            return None
        if not isinstance(value, str):
            return None

        return json.loads(value)

    def set(self, key: str, value):
        self.client.setex(key, self.ttl, json.dumps(value))

    def clear(self):
        self.client.flushdb()


redis_cache = RedisCache()
