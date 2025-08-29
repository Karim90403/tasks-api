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
            _source=["work_stages", "project_id", "project_name"]
        )
        results = []
        for hit in resp["hits"]["hits"]:
            ws = hit["_source"].get("work_stages", [])
            project_id = hit["_source"].get("project_id", "")
            project_name = hit["_source"].get("project_name", "")
            for stage in ws:
                results.append(dict(project_id=project_id, project_name=project_name,**stage))
        return results


    async def get_shift_history(self) -> List[Dict[str, Any]]:
        resp = await self.client.search(
            index=self.index,
            size=100,
            _source=[
                "project_id",
                "project_name",
                "work_stages.tasks.task_id",
                "work_stages.tasks.task_name",
                "work_stages.tasks.time_intervals",
                "work_stages.tasks.subtasks.subtask_id",
                "work_stages.tasks.subtasks.subtask_name",
                "work_stages.tasks.subtasks.time_intervals",
            ],
        )
        return self.parse_shift_history(resp["hits"]["hits"])

    async def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.client.index(
            index=self.index,
            id=project_data["project_id"],
            document=project_data,
            refresh="wait_for",
        )
        return response
@lru_cache
def get_manager_elastic_repository(
    client: AsyncElasticsearch = Depends(get_elastic_client),
) -> ABCManagerRepository:
    return ElasticManagerRepository(
        client, settings.elasticsearch.index, settings.elasticsearch.request_timeout
    )
