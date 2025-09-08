import redis.asyncio as redis
from config import config


class RedisManager:
    def __init__(self):
        self.pool = None

    async def connect(self):
        """Initialize Redis connection pool"""
        self.pool = redis.ConnectionPool.from_url(
            f"redis://:{config.redis_password}@{config.redis_host}:{config.redis_port}/0",
            decode_responses=True,
            max_connections=config.redis_pool_size
        )

    async def disconnect(self):
        """Close Redis connection pool"""
        if self.pool:
            await self.pool.disconnect()

    def get_client(self):
        """Get a Redis client from the pool"""
        return redis.Redis(connection_pool=self.pool)


# Global instance
redis_manager = RedisManager()
