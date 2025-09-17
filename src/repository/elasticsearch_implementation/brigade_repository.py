from functools import lru_cache
from typing import Any, Dict, List, Optional

from elasticsearch._async.client import AsyncElasticsearch
from fastapi import Depends

from core.environment_config import settings
from db.elastic.connection import get_elastic_client
from repository.abc.brigade_repository import ABCBrigadeRepository

class BrigadeRepository(ABCBrigadeRepository):
    def __init__(self, client: AsyncElasticsearch, index: str, timeout: int = 30):
        self.client = client
        self.index = index
        self.timeout = timeout

    async def create_brigade(self, brigade_data: Dict[str, Any]) -> Dict[str, Any]:
        brigade_id = brigade_data.get("brigade_id")
        resp = await self.client.index(index=self.index, id=brigade_id, document=brigade_data, refresh="wait_for")
        return resp

    async def get_brigade(self, brigade_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.client.get(index=self.index, id=brigade_id, ignore=[404])
        if not doc or not doc.get("found"):
            return None
        return doc["_source"]

    async def search_brigades(self, name: Optional[str], member: Optional[str], size: int = 20) -> List[Dict[str, Any]]:
        if name and member:
            # комбинированный nested + match
            query = {
                "bool": {
                    "must": [
                        {"match": {"brigade_name": {"query": name}}},
                        {
                            "nested": {
                                "path": "members",
                                "query": {"term": {"members.user_id": member}}
                            }
                        },
                    ]
                }
            }
        elif name:
            query = {"match": {"brigade_name": {"query": name}}}
        elif member:
            query = {
                "nested": {
                    "path": "members",
                    "query": {"term": {"members.user_id": member}}
                }
            }
        else:
            query = {"match_all": {}}

        resp = await self.client.search(index=self.index, size=size, body={"query": query})
        return [hit["_source"] for hit in resp["hits"]["hits"]]

@lru_cache
def get_brigade_repository(
    client: AsyncElasticsearch = Depends(get_elastic_client),
) -> ABCBrigadeRepository:
    return BrigadeRepository(client, settings.elasticsearch.brigades_index, settings.elasticsearch.request_timeout)
