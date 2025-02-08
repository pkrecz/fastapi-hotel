import os
import redis
from redis.exceptions import ConnectionError
from dotenv import load_dotenv
from typing import AsyncGenerator, Generator


load_dotenv()

host_redis = os.getenv("REDIS_HOST", default="localhost")
port_redis = os.getenv("REDIS_PORT", default=6379)


class RedisSupport:

    def __init__(self):
        try:
            redis_pool = redis.ConnectionPool(
                                                host=host_redis,
                                                port=port_redis,
                                                decode_responses=True)
            self._redis = redis.Redis(connection_pool=redis_pool)
            self._redis.ping()
        except ConnectionError:
            raise ConnectionError("Redis is not ready.")

    def init_sync(self):
        return self._redis

    async def init_async(self):
        return self._redis


instance = RedisSupport()

def get_redis_sync() -> Generator:
    session = instance.init_sync()
    yield session

async def get_redis_async() -> AsyncGenerator:
    session = await instance.init_async()
    yield session
