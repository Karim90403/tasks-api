import backoff
from aiocache import cached
from redis import Redis

from core.environment_config import settings
from db.redis.session_manager import redis_db_manager


@backoff.on_exception(backoff.expo, RuntimeError, max_time=30)
@cached(ttl=settings.redis.expire_manager, key="get_redis_client")
async def get_redis_client() -> Redis:
    async with redis_db_manager.session() as session:
        return session
