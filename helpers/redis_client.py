import redis.asyncio as redis

class RedisClient:
    _instances = []  # 🔹 Global list of the instances

    def __init__(self, port='6379', db=0):
        self.db = db
        self.redis = redis.from_url(f"redis://localhost:{port}")
        self._closed = False
        RedisClient._instances.append(self)  # Instance registry

    async def close(self):
        """Cerrar esta conexión Redis"""
        if not self._closed:
            try:
                await self.redis.aclose()
            except Exception as e:
                print(f"⚠️ Error cerrando Redis: {e}")
            self._closed = True

    @classmethod
    async def close_all(cls):
        """Cerrar todas las conexiones Redis creadas en este proceso"""
        for client in cls._instances:
            if not client._closed:
                await client.close()
        cls._instances.clear()

    async def select_db(self):
        await self.redis.execute_command('SELECT', self.db)

    async def set(self, key, value):
        await self.select_db()
        await self.redis.set(key, value)

    async def get(self, key):
        await self.select_db()
        return await self.redis.get(key)

    async def delete(self, key):
        await self.select_db()
        await self.redis.delete(key)

    async def exists(self, key):
        await self.select_db()
        return await self.redis.exists(key)

    async def list_keys(self, pattern='*'):
        await self.select_db()
        return await self.redis.keys(pattern)

    async def mget(self, keys):
        await self.select_db()
        return await self.redis.mget(keys)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
