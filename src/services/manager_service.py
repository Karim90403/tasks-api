from typing import Any, Dict, List

from fastapi import Depends

from repository.abc.manager_repository import ABCManagerRepository
from repository.elasticsearch_implementation.manager_repository import get_manager_elastic_repository
from schemas.request.project_create import ProjectCreate
from schemas.response.construction import (
    OperationResult,
    ProjectSummary,
    ShiftHistoryEntry,
    StageWithProject,
    SubtaskShiftEntry,
    TaskShiftEntry,
)


class ManagerService:
    def __init__(self, repo: ABCManagerRepository):
        self.repo = repo

    async def list_projects(self) -> List[ProjectSummary]:
        projects = await self.repo.get_projects()
        return [ProjectSummary.parse_obj(project) for project in projects]

    async def list_tasks(self, project_id: str) -> List[StageWithProject]:
        stages = await self.repo.get_tasks(project_id)
        return [StageWithProject.parse_obj(stage) for stage in stages]

    async def shift_history(self, project_id: str) -> List[ShiftHistoryEntry]:
        history = await self.repo.get_shift_history(project_id)
        parsed: List[ShiftHistoryEntry] = []
        for item in history:
            entry_type = item.get("type")
            if entry_type == "task":
                parsed.append(TaskShiftEntry.parse_obj(item))
            elif entry_type == "subtask":
                parsed.append(SubtaskShiftEntry.parse_obj(item))
            else:
                parsed.append(TaskShiftEntry.parse_obj(item))
        return parsed

    async def create_project(self, project: ProjectCreate) -> OperationResult:
        response = await self.repo.create_project(project.dict())
        result = response.get("result") or "created"
        return OperationResult(result=result, project_id=project.project_id)

    async def change_project(self, project_id: str, key: str, value: Any) -> OperationResult:
        response = await self.repo.change_project(project_id, key, value)
        result = response.get("result") or "updated"
        response_project_id = response.get("project_id") or project_id
        return OperationResult(result=result, project_id=response_project_id)


def get_manager_service(
    repo: ABCManagerRepository = Depends(get_manager_elastic_repository),
) -> ManagerService:
    return ManagerService(repo)
