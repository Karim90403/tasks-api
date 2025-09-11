import elasticsearch

from datetime import datetime, timezone
from functools import lru_cache
from typing import Any, Dict, List, Optional

from elasticsearch._async.client import AsyncElasticsearch
from fastapi import Depends

from core.environment_config import settings
from db.elastic.connection import get_elastic_client
from repository.abc.foreman_repository import ABCForemanRepository
from repository.base.elastic_repository import BaseElasticRepository


class ElasticForemanRepository(ABCForemanRepository, BaseElasticRepository):
    def __init__(self, client: AsyncElasticsearch, index: str, timeout: int = 30):
        self.client = client
        self.index = index
        self.timeout = timeout

    async def get_projects(self, foreman_id: str) -> List[Dict[str, Any]]:
        resp = await self.client.search(
            index=self.index,
            size=100,
            query={"term": {"foreman_id": foreman_id}},
            _source=["project_id", "project_name"],
            request_timeout=self.timeout,
        )
        return [hit["_source"] for hit in resp["hits"]["hits"]]

    async def get_tasks(self, foreman_id: str) -> List[Dict[str, Any]]:
        resp = await self.client.search(
            index=self.index,
            size=100,
            query={"term": {"foreman_id": foreman_id}},
            _source=["work_stages"],
            request_timeout=self.timeout,
        )
        results = []
        for hit in resp["hits"]["hits"]:
            ws = hit["_source"].get("work_stages", [])
            for stage in ws:
                results.append(stage)
        return results

    async def start_shift(self, foreman_id: str, task_ids: List[str], subtask_ids: List[str]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        body = {
            "query": {
                "match": {"foreman_id": foreman_id}
            },
            "script": {
                "source": """
                    boolean updated = false;

                    if (ctx._source.work_stages != null) {
                        for (stage in ctx._source.work_stages) {
                            if (stage.tasks != null) {
                                for (task in stage.tasks) {
                                    // Обработка задач
                                    if (params.task_ids.contains(task.task_id)) {
                                        if (task.time_intervals == null) {
                                            task.time_intervals = [];
                                        }
                                        // Проверяем, есть ли активный интервал
                                        boolean hasActiveInterval = false;
                                        if (!task.time_intervals.isEmpty()) {
                                            def lastInterval = task.time_intervals.get(task.time_intervals.size() - 1);
                                            if (lastInterval.end_time == null) {
                                                hasActiveInterval = true;
                                            }
                                        }
                                        if (!hasActiveInterval) {
                                            def newInterval = [
                                                'start_time': params.now,
                                                'end_time': null,
                                                'status': 'active'
                                            ];
                                            task.time_intervals.add(newInterval);
                                            updated = true;
                                        }
                                    }

                                    // Обработка подзадач
                                    if (task.subtasks != null && !task.subtasks.isEmpty()) {
                                        for (sub in task.subtasks) {
                                            if (params.subtask_ids.contains(sub.subtask_id)) {
                                                if (sub.time_intervals == null) {
                                                    sub.time_intervals = [];
                                                }
                                                // Проверяем, есть ли активный интервал
                                                boolean hasActiveSubInterval = false;
                                                if (!sub.time_intervals.isEmpty()) {
                                                    def lastSubInterval = sub.time_intervals.get(sub.time_intervals.size() - 1);
                                                    if (lastSubInterval.end_time == null) {
                                                        hasActiveSubInterval = true;
                                                    }
                                                }
                                                if (!hasActiveSubInterval) {
                                                    def newSubInterval = [
                                                        'start_time': params.now,
                                                        'end_time': null,
                                                        'status': 'active'
                                                    ];
                                                    sub.time_intervals.add(newSubInterval);
                                                    updated = true;
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    if (!updated) {
                        ctx.op = 'noop';
                    }
                """,
                "params": {"task_ids": task_ids, "subtask_ids": subtask_ids, "now": now},
                "lang": "painless"
            }
        }

        try:
            await self.client.update_by_query(
                index=self.index,
                body=body,
                refresh=True
            )
        except Exception as e:
            print(f"Elasticsearch error: {e}")
            raise

    async def stop_shift(self, foreman_id: str, task_ids: List[str], subtask_ids: List[str]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        body = {
            "query": {
                "match": {"foreman_id": foreman_id}
            },
            "script": {
                "source": """
                    boolean updated = false;

                    if (ctx._source.work_stages != null) {
                        for (stage in ctx._source.work_stages) {
                            if (stage.tasks != null) {
                                for (task in stage.tasks) {
                                    // Обработка задач
                                    if (params.task_ids.contains(task.task_id)) {
                                        if (task.time_intervals != null && !task.time_intervals.isEmpty()) {
                                            def lastTaskInterval = task.time_intervals.get(task.time_intervals.size() - 1);
                                            if (lastTaskInterval.end_time == null) {
                                                lastTaskInterval.end_time = params.now;
                                                lastTaskInterval.status = 'closed';
                                                updated = true;
                                            }
                                        }
                                    }

                                    // Обработка подзадач
                                    if (task.subtasks != null && !task.subtasks.isEmpty()) {
                                        for (sub in task.subtasks) {
                                            if (params.subtask_ids.contains(sub.subtask_id)) {
                                                if (sub.time_intervals != null && !sub.time_intervals.isEmpty()) {
                                                    def lastSubInterval = sub.time_intervals.get(sub.time_intervals.size() - 1);
                                                    if (lastSubInterval.end_time == null) {
                                                        lastSubInterval.end_time = params.now;
                                                        lastSubInterval.status = 'closed';
                                                        updated = true;
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    if (!updated) {
                        ctx.op = 'noop';
                    }
                """,
                "params": {"task_ids": task_ids, "subtask_ids": subtask_ids, "now": now},
                "lang": "painless"
            }
        }

        try:
            await self.client.update_by_query(
                index=self.index,
                body=body,
                refresh=True
            )
        except Exception as e:
            print(f"Elasticsearch error: {e}")
            raise

    async def get_shift_history(self, foreman_id: str) -> List[Dict[str, Any]]:
        resp = await self.client.search(
            index=self.index,
            size=50,
            query={"match": {"foreman_id": foreman_id}},
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

    async def get_shift_status(self, foreman_id: str) -> str:
        resp = await self.client.search(
            index=self.index,
            size=1,
            query={"match": {"foreman_id": foreman_id}},
            _source=[
                "work_stages.tasks.time_intervals",
                "work_stages.tasks.subtasks.time_intervals",
            ],
        )

        for hit in resp["hits"]["hits"]:
            ws = hit["_source"].get("work_stages", [])
            for stage in ws:
                for task in stage.get("tasks", []):
                    for ti in task.get("time_intervals", []):
                        if ti.get("end_time") in (None, "") or ti.get("status") == "active":
                            return "working"
                    for sub in task.get("subtasks", []):
                        for ti in sub.get("time_intervals", []):
                            if ti.get("end_time") in (None, "") or ti.get("status") == "active":
                                return "working"
        return "not_working"

    async def add_report_links(
            self,
            project_id: str,
            stage_id: str,
            task_id: str,
            subtask_id: str,
            links: List[Dict[str, str]],
            uploaded_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Добавляет элементы в work_stages[].tasks[].subtasks[].reportLinks для одного проекта.
        links: [{ "title": "...", "href": "..."}, ...]
        """
        try:
            got = await self.client.get(index=self.index, id=project_id)
        except elasticsearch.exceptions.NotFoundError:
            return {"result": "not_found", "project_id": project_id}

        src = got["_source"]

        ws = src.get("work_stages", [])
        stage = next((s for s in ws if s.get("stage_id") == stage_id), None)
        if not stage:
            return {"result": "stage_not_found", "stage_id": stage_id}

        tasks = stage.get("tasks", [])
        task = next((t for t in tasks if t.get("task_id") == task_id), None)
        if not task:
            return {"result": "task_not_found", "task_id": task_id}

        subtasks = task.get("subtasks", [])
        subtask = next((st for st in subtasks if st.get("subtask_id") == subtask_id), None)
        if not subtask:
            return {"result": "subtask_not_found", "subtask_id": subtask_id}

        rlinks = subtask.get("reportLinks")
        if rlinks is None or not isinstance(rlinks, list):
            rlinks = []
            subtask["reportLinks"] = rlinks

        from datetime import datetime, timezone
        uploaded_at = datetime.now(timezone.utc).isoformat()

        for link in links:
            enriched = {
                "title": link.get("title") or "Файл",
                "href": link.get("href"),
            }
            rlinks.append(enriched)

        resp = await self.client.index(
            index=self.index,
            id=project_id,
            document=src,
            refresh="wait_for",
            if_seq_no=got.get("_seq_no"),
            if_primary_term=got.get("_primary_term"),
        )
        return resp


@lru_cache
def get_foreman_elastic_repository(
    client: AsyncElasticsearch = Depends(get_elastic_client),
) -> ABCForemanRepository:
    return ElasticForemanRepository(
        client, settings.elasticsearch.index, settings.elasticsearch.request_timeout
    )
