
from fastapi import APIRouter, Depends, status

from core.dependencies import get_current_user
from schemas.request.project_change import ChangeProjectRequest
from schemas.user import UserInDB
from services.manager_service import ManagerService, get_manager_service

router = APIRouter(prefix="/api/manager", tags=["manager"])


@router.get("/projects", status_code=status.HTTP_200_OK)
async def get_projects(
        service: ManagerService = Depends(get_manager_service),
        current_user: UserInDB = Depends(get_current_user),
    ):
    if current_user.role == "root":
        return await service.list_projects()

@router.patch(
    "/projects/{project_id}",
    status_code=status.HTTP_200_OK,
)
async def change_project(
    project_id: str,
    body: ChangeProjectRequest,
    service: ManagerService = Depends(get_manager_service),
    current_user: UserInDB = Depends(get_current_user),
):
    if current_user.role == "root":
        return await service.change_project(project_id, body.key, body.value)


@router.get("/tasks", status_code=status.HTTP_200_OK)
async def get_tasks(
        service: ManagerService = Depends(get_manager_service),
        current_user: UserInDB = Depends(get_current_user),
    ):
    if current_user.role == "root":
        return await service.list_tasks()

@router.get("/shifts", status_code=status.HTTP_200_OK)
async def get_all_shifts(
        service: ManagerService = Depends(get_manager_service),
        current_user: UserInDB = Depends(get_current_user),
    ):
    if current_user.role == "root":
        return await service.shift_history()

