from typing import Any, Dict, List

from fastapi import Depends

from repository.abc.manager_repository import ABCManagerRepository
from repository.elasticsearch_implementation.manager_repository import get_manager_elastic_repository
from schemas.request.project_create import ProjectCreate


class ManagerService:
    def __init__(self, repo: ABCManagerRepository):
        self.repo = repo

    async def list_projects(self) -> List[Dict[str, Any]]:
        return await self.repo.get_projects()

    async def list_tasks(self) -> List[Dict[str, Any]]:
        return await self.repo.get_tasks()

    async def shift_history(self) -> List[Dict[str, Any]]:
        return await self.repo.get_shift_history()

    async def create_project(self, project: ProjectCreate) -> Dict[str, Any]:
        return await self.repo.create_project(project.dict())

    async def change_project(self, project_id: str, key: str, value: Any) -> Dict[str, Any]:
        return await self.repo.change_project(project_id, key, value)


def get_manager_service(
    repo: ABCManagerRepository = Depends(get_manager_elastic_repository),
) -> ManagerService:
    return ManagerService(repo)
