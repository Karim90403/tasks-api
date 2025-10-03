from typing import List

from fastapi import APIRouter, Depends, status

from core.dependencies import check_project_access, get_current_user
from schemas.request.project_change import ChangeProjectRequest
from schemas.request.project_create import ProjectCreate
from schemas.response.construction import (
    OperationResult,
    ProjectSummary,
    ShiftHistoryEntry,
    StageWithProject,
)
from schemas.user import UserInDB
from services.manager_service import ManagerService, get_manager_service

router = APIRouter(prefix="/api/manager", tags=["manager"])


@router.get(
    "/projects",
    status_code=status.HTTP_200_OK,
    response_model=List[ProjectSummary],
)
async def get_projects(
        service: ManagerService = Depends(get_manager_service),
        current_user: UserInDB = Depends(get_current_user),
):
    if current_user.role == "root":
        return await service.list_projects()
    elif current_user.role == "project_manager":
        return current_user.managed_projects

@router.post(
    "/projects",
    status_code=status.HTTP_201_CREATED,
    response_model=OperationResult,
)
async def create_project(
    project: ProjectCreate,
    service: ManagerService = Depends(get_manager_service),
    current_user: UserInDB = Depends(get_current_user),
):
    if current_user.role in ["root", "project_manager"]:
        return await service.create_project(project)

@router.patch(
    "/projects/{project_id}",
    status_code=status.HTTP_200_OK,
    response_model=OperationResult,
    dependencies=[Depends(check_project_access)]
)
async def change_project(
    project_id: str,
    body: ChangeProjectRequest,
    service: ManagerService = Depends(get_manager_service),
):
    return await service.change_project(project_id, body.key, body.value)


@router.get(
    "/tasks",
    status_code=status.HTTP_200_OK,
    response_model=List[StageWithProject],
    dependencies=[Depends(check_project_access)],
)
async def get_tasks(
        service: ManagerService = Depends(get_manager_service),
    ):
    return await service.list_tasks()

@router.get(
    "/shifts",
    status_code=status.HTTP_200_OK,
    response_model=List[ShiftHistoryEntry],
    dependencies=[Depends(check_project_access)],
)
async def get_all_shifts(
        service: ManagerService = Depends(get_manager_service),
):
    return await service.shift_history()
