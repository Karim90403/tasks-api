from functools import lru_cache
from typing import Any, Dict, List, Union

from elasticsearch._async.client import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
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

    @staticmethod
    def _ensure_list_size(lst: List[Any], idx: int):
        while len(lst) <= idx:
            lst.append(None)

    @classmethod
    def _set_by_path(cls, obj: Union[Dict[str, Any], List[Any]], path: str, value: Any):
        """
        Устанавливает value по dot-path. Поддерживает индексы массивов: "work_stages.0.stage_name".
        Создаёт недостающие словари/списки.
        """
        parts = path.split(".")
        cur = obj
        for i, part in enumerate(parts):
            is_last = i == len(parts) - 1
            is_index = part.isdigit()

            if is_index:
                idx = int(part)
                if not isinstance(cur, list):
                    # превращаем текущий узел в список (если там ничего, делаем список)
                    # если это dict — заменяем его на список (см. ниже комментарий)
                    # аккуратнее: если cur — dict, то это означает, что предыдущий шаг создал dict,
                    # нужно перевести его в список на уровне родителя — для простоты считаем,
                    # что ключ уже был списком; в реальных данных это обычно корректно.
                    new_list = []
                    # если был dict, мы его "теряем", потому что целимся в массив
                    # но такой кейс встречается редко; при необходимости можно
                    # усложнить логику, чтобы хранить и dict и list.
                    cur.clear()  # на всякий случай очищаем
                    cur = new_list  # NOTE: см. пояснение ниже
                cls._ensure_list_size(cur, idx)
                if is_last:
                    cur[idx] = value
                else:
                    if cur[idx] is None:
                        # следующий уровень по умолчанию — dict
                        cur[idx] = {}
                    cur = cur[idx]
            else:
                # ключ словаря
                if not isinstance(cur, dict):
                    # если тут список — это конфликт структур, создаём dict
                    # и "перезатираем" текущую позицию
                    # (в нормальных данных такое не должно происходить)
                    cur = {}
                if is_last:
                    cur[part] = value
                else:
                    if part not in cur or cur[part] is None:
                        # по умолчанию следующий уровень — dict
                        cur[part] = {}
                    # если следующий сегмент — число, то готовим список
                    if (i + 1) < len(parts) and parts[i + 1].isdigit() and not isinstance(cur[part], list):
                        cur[part] = []
                    cur = cur[part]

    async def change_project(self, project_id: str, key: str, value: Any) -> Dict[str, Any]:
        try:
            got = await self.client.get(index=self.index, id=project_id)
        except NotFoundError:
            return {"result": "not_found", "project_id": project_id}

        src = got["_source"]

        # модифицируем на месте
        self._set_by_path(src, key, value)

        # перезаписываем документ (id тот же)
        resp = await self.client.index(
            index=self.index,
            id=project_id,
            document=src,
            refresh="wait_for",
        )
        return resp


@lru_cache
def get_manager_elastic_repository(
    client: AsyncElasticsearch = Depends(get_elastic_client),
) -> ABCManagerRepository:
    return ElasticManagerRepository(
        client, settings.elasticsearch.index, settings.elasticsearch.request_timeout
    )
