from typing import Any, Dict, List

from fastapi import Depends

from repository.abc.manager_repository import ABCManagerRepository
from repository.elasticsearch_implementation.manager_repository import get_manager_elastic_repository


class ManagerService:
    def __init__(self, repo: ABCManagerRepository):
        self.repo = repo

    async def list_projects(self) -> List[Dict[str, Any]]:
        return await self.repo.get_projects()

    async def list_tasks(self) -> List[Dict[str, Any]]:
        return await self.repo.get_tasks()

    async def shift_history(self) -> List[Dict[str, Any]]:
        return await self.repo.get_shift_history()


def get_manager_service(
    repo: ABCManagerRepository = Depends(get_manager_elastic_repository),
) -> ManagerService:
    return ManagerService(repo)
