import json
import logging
from typing import Any, Optional
# Assuming redis is installed or fallback to in-memory dict for now if not available
try:
    import redis.asyncio as redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.enabled = HAS_REDIS
        if self.enabled:
            self.redis = redis.from_url(redis_url, decode_responses=True)
        else:
            logger.warning("Redis is not installed. Using fallback in-memory cache.")
            self._fallback_cache = {}
            self._fallback_ttls = {}
            
    async def get(self, key: str) -> Optional[Any]:
        if self.enabled:
            val = await self.redis.get(key)
            return json.loads(val) if val else None
        else:
            import time
            if key in self._fallback_cache:
                if self._fallback_ttls.get(key, float('inf')) > time.time():
                    return self._fallback_cache[key]
                else:
                    del self._fallback_cache[key]
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600):
        if self.enabled:
            await self.redis.setex(key, ttl, json.dumps(value))
        else:
            import time
            self._fallback_cache[key] = value
            self._fallback_ttls[key] = time.time() + ttl
            
    async def invalidate(self, prefix: str):
        if self.enabled:
            keys = await self.redis.keys(f"{prefix}*")
            if keys:
                await self.redis.delete(*keys)
        else:
            keys_to_delete = [k for k in self._fallback_cache.keys() if str(k).startswith(prefix)]
            for k in keys_to_delete:
                del self._fallback_cache[k]
