"""
Redis client configuration for caching and session management.
"""

import redis
from typing import Optional
import json
from app.core.config import settings

class RedisClient:
    """Redis client wrapper with common operations."""
    
    def __init__(self):
        self.client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        return self.client.get(key)
    
    async def set(self, key: str, value: str, expire: int = None) -> bool:
        """Set key-value pair with optional expiration."""
        return self.client.set(key, value, ex=expire)
    
    async def delete(self, key: str) -> bool:
        """Delete key."""
        return self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return self.client.exists(key)
    
    async def set_json(self, key: str, value: dict, expire: int = None) -> bool:
        """Set JSON value with optional expiration."""
        json_value = json.dumps(value)
        return self.client.set(key, json_value, ex=expire)
    
    async def get_json(self, key: str) -> Optional[dict]:
        """Get JSON value by key."""
        value = self.client.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter."""
        return self.client.incr(key, amount)
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key."""
        return self.client.expire(key, seconds)

# Global Redis client instance
redis_client = RedisClient()