import contextlib
from typing import AsyncIterator

from fastapi import FastAPI

from core.environment_config import settings
from db.elastic.session_manager import elastic_db_manager
from db.redis.session_manager import redis_db_manager


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    elastic_db_manager.init(settings.elasticsearch.url, settings.elasticsearch.login, settings.elasticsearch.password)
    redis_db_manager.init(settings.redis.host, settings.redis.port)
    yield
    await elastic_db_manager.close()
    await redis_db_manager.close()
