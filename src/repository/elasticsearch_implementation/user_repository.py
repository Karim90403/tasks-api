from functools import lru_cache
from typing import Any, Optional

from elasticsearch._async.client import AsyncElasticsearch
from fastapi import Depends
from loguru import logger

from core.environment_config import settings
from db.elastic.connection import get_elastic_client
from repository.abc.user_repository import ABCUserRepository
from schemas.user import UserInDB


class UserRepository(ABCUserRepository):
    def __init__(self, client: AsyncElasticsearch, index: str, timeout: int = 30):
        self.client = client
        self.index = index
        self.timeout = timeout

    async def create_user(self, user: UserInDB) -> None:
        response = await self.client.index(index=self.index, id=user.id, document=user.dict())
        logger.info(f"Document created: {response['result']}")
        logger.info(f"Document ID: {response['_id']}")

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        query = {"query": {"term": {"email": email}}}
        resp = await self.client.search(
            index=self.index,
            size=100,
            body=query
        )
        hits = resp.get("hits", {}).get("hits", [])
        if not hits:
            return None
        source = hits[0]["_source"]
        return UserInDB(**source)

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        doc = await self.client.get(
            index=self.index,
            ignore=[404],
            id=user_id
        )
        if not doc or not doc.get("found"):
            return None
        return UserInDB(**doc["_source"])

    async def get_all_users(self) -> list[dict[str, Any]]:
        result = await self.client.search(
            index=self.index,
            body={"query": {"match_all": {}}},
            size=1000
        )
        return [hit["_source"] for hit in result["hits"]["hits"]]

@lru_cache
def get_user_elastic_repository(
    client: AsyncElasticsearch = Depends(get_elastic_client),
) -> ABCUserRepository:
    return UserRepository(
        client, settings.elasticsearch.users_index, settings.elasticsearch.request_timeout
    )
