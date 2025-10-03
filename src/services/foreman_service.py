from typing import Any, Dict, List

from fastapi import Depends

from repository.abc.foreman_repository import ABCForemanRepository
from repository.elasticsearch_implementation.foreman_repository import get_foreman_elastic_repository
from schemas.response.construction import (
    ProjectSummary,
    ShiftHistoryEntry,
    ShiftStatus,
    TaskShiftEntry,
    SubtaskShiftEntry,
    WorkStage,
)


class ForemanService:
    def __init__(self, repo: ABCForemanRepository):
        self.repo = repo

    async def list_projects(self, foreman_id: str) -> List[ProjectSummary]:
        projects = await self.repo.get_projects(foreman_id)
        return [ProjectSummary.parse_obj(project) for project in projects]

    async def list_tasks(self, foreman_id: str) -> List[WorkStage]:
        tasks = await self.repo.get_tasks(foreman_id)
        return [WorkStage.parse_obj(stage) for stage in tasks]

    async def start_shift(self, foreman_id: str, task_ids: List[str], subtask_ids: List[str]) -> None:
        return await self.repo.start_shift(foreman_id, task_ids, subtask_ids)

    async def stop_shift(self, foreman_id: str, task_ids: List[str], subtask_ids: List[str]) -> None:
        return await self.repo.stop_shift(foreman_id, task_ids, subtask_ids)

    async def shift_history(self, foreman_id: str) -> List[ShiftHistoryEntry]:
        history = await self.repo.get_shift_history(foreman_id)
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

    async def shift_status(self, foreman_id: str) -> ShiftStatus:
        status = await self.repo.get_shift_status(foreman_id)
        return ShiftStatus(status=status)

    async def add_report_links(
            self,
            project_id: str,
            stage_id: str,
            work_type_id: str,
            task_id: str,
            subtask_id: str,
            links: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        return await self.repo.add_report_links(
            project_id=project_id,
            stage_id=stage_id,
            work_type_id=work_type_id,
            task_id=task_id,
            subtask_id=subtask_id,
            links=links,
        )


def get_foreman_service(
    repo: ABCForemanRepository = Depends(get_foreman_elastic_repository),
) -> ForemanService:
    return ForemanService(repo)
