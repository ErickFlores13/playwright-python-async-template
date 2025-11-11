import redis.asyncio as redis
from typing import List, Optional, Any


class RedisClient:
    _instances: List['RedisClient'] = []  # 🔹 Global list of the instances

    def __init__(self, port: str = '6379', db: int = 0):
        self.db = db
        self.redis = redis.from_url(f"redis://localhost:{port}")
        self._closed = False
        RedisClient._instances.append(self)  # Instance registry

    async def close(self) -> None:
        """Close this Redis connection."""
        if not self._closed:
            try:
                await self.redis.aclose()
            except Exception as e:
                print(f"⚠️ Error closing Redis: {e}")
            self._closed = True

    @classmethod
    async def close_all(cls) -> None:
        """Close all Redis connections created in this process."""
        for client in cls._instances:
            if not client._closed:
                await client.close()
        cls._instances.clear()

    async def select_db(self) -> None:
        """Select the database for this connection."""
        await self.redis.execute_command('SELECT', self.db)

    async def set(self, key: str, value: Any) -> None:
        """Set a key-value pair in Redis."""
        await self.select_db()
        await self.redis.set(key, value)

    async def get(self, key: str) -> Optional[bytes]:
        """Get a value from Redis by key."""
        await self.select_db()
        return await self.redis.get(key)

    async def delete(self, key: str) -> int:
        """Delete a key from Redis. Returns number of keys deleted."""
        await self.select_db()
        return await self.redis.delete(key)

    async def exists(self, key: str) -> int:
        """Check if a key exists in Redis. Returns 1 if exists, 0 otherwise."""
        await self.select_db()
        return await self.redis.exists(key)

    async def list_keys(self, pattern: str = '*') -> List[str]:
        """List all keys matching the given pattern."""
        await self.select_db()
        return await self.redis.keys(pattern)

    async def mget(self, keys: List[str]) -> List[Optional[bytes]]:
        """Get multiple values from Redis by keys."""
        await self.select_db()
        return await self.redis.mget(keys)

    async def __aenter__(self) -> 'RedisClient':
        """Enter async context manager."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager and close connection."""
        await self.close()
