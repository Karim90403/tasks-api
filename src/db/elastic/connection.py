import backoff
import elasticsearch
from aiocache import cached
from elasticsearch._async.client import AsyncElasticsearch

from core.environment_config import settings
from db.elastic.session_manager import elastic_db_manager


@backoff.on_exception(backoff.expo, elasticsearch.exceptions.ConnectionError, max_time=30)
@cached(ttl=settings.redis.expire_manager, key="get_elastic_client")
async def get_elastic_client() -> AsyncElasticsearch:
    async with elastic_db_manager.session() as session:
        return session
