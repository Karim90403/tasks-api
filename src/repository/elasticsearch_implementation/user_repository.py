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

    async def add_project_to_user(self, user_id: str, project_id: str) -> None:
        script = {
            "script": {
                "source": """
                    if (ctx._source.managed_projects == null) {
                        ctx._source.managed_projects = [params.project]
                    } else if (!ctx._source.managed_projects.contains(params.project)) {
                        ctx._source.managed_projects.add(params.project)
                    }
                """,
                "lang": "painless",
                "params": {"project": project_id}
            }
        }
        await self.client.update(index=self.index, id=user_id, body=script, ignore=[404])

    async def remove_project_from_user(self, user_id: str, project_id: str) -> None:
        script = {
            "script": {
                "source": """
                    if (ctx._source.managed_projects != null) {
                        ctx._source.managed_projects.removeIf(p -> p == params.project)
                    }
                """,
                "lang": "painless",
                "params": {"project": project_id}
            }
        }
        await self.client.update(index=self.index, id=user_id, body=script, ignore=[404])

    async def update_user(self, user: UserInDB) -> None:
        await self.client.index(index=self.index, id=user.id, document=user.dict())


@lru_cache
def get_user_elastic_repository(
    client: AsyncElasticsearch = Depends(get_elastic_client),
) -> ABCUserRepository:
    return UserRepository(
        client, settings.elasticsearch.users_index, settings.elasticsearch.request_timeout
    )
