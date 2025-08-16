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


def get_foreman_service(
    repo: ABCForemanRepository = Depends(get_foreman_elastic_repository),
) -> ForemanService:
    return ForemanService(repo)
