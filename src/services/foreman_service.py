from typing import Any, Dict, List

from fastapi import Depends

from repository.abc.foreman_repository import ABCForemanRepository
from repository.elasticsearch_implementation.foreman_repository import get_foreman_elastic_repository


class ForemanService:
    def __init__(self, repo: ABCForemanRepository):
        self.repo = repo

    async def list_projects(self, foreman_id: str) -> List[Dict[str, Any]]:
        return await self.repo.get_projects(foreman_id)

    async def list_tasks(self, foreman_id: str) -> List[Dict[str, Any]]:
        return await self.repo.get_tasks(foreman_id)

    async def start_shift(self, foreman_id: str, task_ids: List[str], subtask_ids: List[str]) -> None:
        return await self.repo.start_shift(foreman_id, task_ids, subtask_ids)

    async def stop_shift(self, foreman_id: str, task_ids: List[str], subtask_ids: List[str]) -> None:
        return await self.repo.stop_shift(foreman_id, task_ids, subtask_ids)

    async def shift_history(self, foreman_id: str) -> List[Dict[str, Any]]:
        return await self.repo.get_shift_history(foreman_id)

    async def shift_status(self, foreman_id: str) -> Dict[str, str]:
        status = await self.repo.get_shift_status(foreman_id)
        return {"status": status}


def get_foreman_service(
    repo: ABCForemanRepository = Depends(get_foreman_elastic_repository),
) -> ForemanService:
    return ForemanService(repo)
