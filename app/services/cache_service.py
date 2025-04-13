import json
import redis.asyncio as aioredis
from app.config import settings
import logging

class RedisCache:
    def __init__(self):
        self.redis = None
        self.ttl = settings.REDIS_TTL
        
    async def init_redis(self):
        """Initialize Redis connection"""
        if not self.redis:
            try:
                self.redis = await aioredis.from_url(
                    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                    password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                    decode_responses=True
                )
                logging.info("Redis connection established")
            except Exception as e:
                logging.error(f"Redis connection error: {e}")
                raise
    
    async def get(self, key: str) -> dict:
        """Get item from cache"""
        if not self.redis:
            await self.init_redis()
        result = await self.redis.get(key)
        if result:
            return json.loads(result)
        return None
    
    async def set(self, key: str, value: dict) -> bool:
        """Set item in cache with TTL"""
        if not self.redis:
            await self.init_redis()
        try:
            await self.redis.set(
                key,
                json.dumps(value),
                ex=self.ttl
            )
            return True
        except Exception as e:
            logging.error(f"Error setting cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete item from cache"""
        if not self.redis:
            await self.init_redis()
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logging.error(f"Error deleting cache: {e}")
            return False
    
    def get_dividend_key(self, netuid: int, hotkey: str) -> str:
        """Get cache key for TAO dividend data"""
        return f"tao_dividend:{netuid}:{hotkey}"

# Create cache instance
cache = RedisCache()


