import redis
from redis.exceptions import RedisError

from app.core.config import settings


class RedisClient:
    """Singleton Redis client"""

    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,  # Auto-decode bytes to strings
            )

    @property
    def client(self) -> redis.Redis:
        """Get Redis client instance"""
        return self._client

    def ping(self) -> bool:
        """Check if Redis is ready"""
        try:
            return self._client.ping()
        except RedisError:
            return False


redis_client = RedisClient()
