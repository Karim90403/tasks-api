from functools import lru_cache
from typing import Any, Dict, List

from elasticsearch._async.client import AsyncElasticsearch
from fastapi import Depends

from core.environment_config import settings
from db.elastic.connection import get_elastic_client
from repository.abc.foreman_repository import ABCForemanRepository


class ElasticForemanRepository(ABCForemanRepository):
    def __init__(self, client: AsyncElasticsearch, index: str, timeout: int = 30):
        self.client = client
        self.index = index
        self.timeout = timeout

    async def get_projects(self, foreman_id: str) -> List[Dict[str, Any]]:
        resp = await self.client.search(
            index=self.index,
            size=100,
            query={"term": {"foreman_id": foreman_id}},
            _source=["project_id", "project_name"]
        )
        return [hit["_source"] for hit in resp["hits"]["hits"]]

    async def get_tasks(self, foreman_id: str) -> List[Dict[str, Any]]:
        resp = await self.client.search(
            index=self.index,
            size=100,
            query={"term": {"foreman_id": foreman_id}},
            _source=["work_stages.work_types.tasks"]
        )
        results = []
        for hit in resp["hits"]["hits"]:
            ws = hit["_source"].get("work_stages", [])
            for stage in ws:
                for wt in stage.get("work_types", []):
                    for task in wt.get("tasks", []):
                        results.append(task)
        return results


@lru_cache
def get_foreman_elastic_repository(
    client: AsyncElasticsearch = Depends(get_elastic_client),
) -> ABCForemanRepository:
    return ElasticForemanRepository(
        client, settings.elasticsearch.index, settings.elasticsearch.request_timeout
    )
