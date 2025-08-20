from functools import lru_cache
from http.client import HTTPException

from elasticsearch import Elasticsearch

from common.exceptions.authorisation import AuthorisationException
from core.environment_config import settings
from db.elastic.connection import get_elastic_client
from repository.abc.user_repository import ABCUserRepository
from schemas.user import UserInDB
from fastapi import Depends
from elasticsearch._async.client import AsyncElasticsearch

class UserRepository(ABCUserRepository):
    def __init__(self, client: AsyncElasticsearch, index: str, timeout: int = 30):
        self.client = client
        self.index = index
        self.timeout = timeout

    async def create_user(self, user: UserInDB) -> None:
        await self.client.index(index=self.index, id=user.id, document=user.dict())

    async def get_user_by_email(self, email: str) -> UserInDB | None:
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
        return UserInDB(**source, id=hits[0]["_id"])

    async def get_user_by_id(self, user_id: str) -> UserInDB | None:
        query = {"query": {"term": {"id": user_id}}}
        resp = await self.client.search(
            index=self.index,
            size=100,
            body=query
        )
        hits = resp.get("hits", {}).get("hits", [])
        if not hits:
            raise AuthorisationException(msg="User not found")

        source = hits[0]["_source"]
        return UserInDB(**source, id=user_id)

@lru_cache
def get_user_elastic_repository(
    client: AsyncElasticsearch = Depends(get_elastic_client),
) -> ABCUserRepository:
    return UserRepository(
        client, settings.elasticsearch.index, settings.elasticsearch.request_timeout
    )