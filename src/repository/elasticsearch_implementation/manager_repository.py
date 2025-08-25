from functools import lru_cache
from typing import Any, Dict, List

from elasticsearch._async.client import AsyncElasticsearch
from fastapi import Depends

from core.environment_config import settings
from db.elastic.connection import get_elastic_client
from repository.abc.manager_repository import ABCManagerRepository
from repository.base.elastic_repository import BaseElasticRepository


class ElasticManagerRepository(ABCManagerRepository, BaseElasticRepository):
    def __init__(self, client: AsyncElasticsearch, index: str, timeout: int = 30):
        self.client = client
        self.index = index
        self.timeout = timeout

    async def get_projects(self) -> List[Dict[str, Any]]:
        resp = await self.client.search(
            index=self.index,
            size=100,
            _source=["project_id", "project_name"]
        )
        return [hit["_source"] for hit in resp["hits"]["hits"]]

    async def get_tasks(self) -> List[Dict[str, Any]]:
        resp = await self.client.search(
            index=self.index,
            size=100,
            _source=["work_stages"]
        )
        results = []
        for hit in resp["hits"]["hits"]:
            ws = hit["_source"].get("work_stages", [])
            for stage in ws:
                results.append(stage)
        return results


    async def get_shift_history(self) -> List[Dict[str, Any]]:
        resp = await self.client.search(
            index=self.index,
            size=100,
            _source=[
                "project_id",
                "project_name",
                "work_stages.work_types.tasks.task_id",
                "work_stages.work_types.tasks.task_name",
                "work_stages.work_types.tasks.time_intervals",
                "work_stages.work_types.tasks.subtasks.subtask_id",
                "work_stages.work_types.tasks.subtasks.subtask_name",
                "work_stages.work_types.tasks.subtasks.time_intervals",
            ],
        )
        return self.parse_shift_history(resp["hits"]["hits"])

@lru_cache
def get_manager_elastic_repository(
    client: AsyncElasticsearch = Depends(get_elastic_client),
) -> ABCManagerRepository:
    return ElasticManagerRepository(
        client, settings.elasticsearch.index, settings.elasticsearch.request_timeout
    )
