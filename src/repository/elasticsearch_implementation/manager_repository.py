from functools import lru_cache
from typing import Any, Dict, List

from elasticsearch._async.client import AsyncElasticsearch
from fastapi import Depends

from core.environment_config import settings
from db.elastic.connection import get_elastic_client
from repository.abc.manager_repository import ABCManagerRepository


class ElasticManagerRepository(ABCManagerRepository):
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

    async def get_shift_history(self) -> List[Dict[str, Any]]:
        resp = await self.client.search(
            index=self.index,
            size=100,
            _source=["foreman_id", "foreman_email", "work_stages.work_types.tasks.subtasks.time_intervals"]
        )
        results = []
        for hit in resp["hits"]["hits"]:
            foreman = {
                "foreman_id": hit["_source"]["foreman_id"],
                "foreman_email": hit["_source"]["foreman_email"],
                "shifts": []
            }
            ws = hit["_source"].get("work_stages", [])
            for stage in ws:
                for wt in stage.get("work_types", []):
                    for task in wt.get("tasks", []):
                        foreman["shifts"].extend(task.get("time_intervals", []))
                        for sub in task.get("subtasks", []):
                            foreman["shifts"].extend(sub.get("time_intervals", []))
            results.append(foreman)

        return results

@lru_cache
def get_manager_elastic_repository(
    client: AsyncElasticsearch = Depends(get_elastic_client),
) -> ABCManagerRepository:
    return ElasticManagerRepository(
        client, settings.elasticsearch.index, settings.elasticsearch.request_timeout
    )
