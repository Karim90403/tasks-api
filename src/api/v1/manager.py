
from fastapi import APIRouter, Depends, status

from core.dependencies import check_project_access
from schemas.request.project_change import ChangeProjectRequest
from schemas.request.project_create import ProjectCreate
from schemas.user import UserInDB
from services.manager_service import ManagerService, get_manager_service

router = APIRouter(prefix="/api/manager", tags=["manager"])


@router.get("/projects", status_code=status.HTTP_200_OK, dependencies=[Depends(check_project_access)])
async def get_projects(
        service: ManagerService = Depends(get_manager_service),
    ):
    return await service.list_projects()

@router.post(
    "/projects",
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    project: ProjectCreate,
    service: ManagerService = Depends(get_manager_service),
    current_user: UserInDB = Depends(check_project_access),
):
    return await service.create_project(project)

@router.patch(
    "/projects/{project_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(check_project_access)]
)
async def change_project(
    project_id: str,
    body: ChangeProjectRequest,
    service: ManagerService = Depends(get_manager_service),
):
    return await service.change_project(project_id, body.key, body.value)


@router.get("/tasks", status_code=status.HTTP_200_OK, dependencies=[Depends(check_project_access)])
async def get_tasks(
        service: ManagerService = Depends(get_manager_service),
    ):
    return await service.list_tasks()

@router.get("/shifts", status_code=status.HTTP_200_OK, dependencies=[Depends(check_project_access)])
async def get_all_shifts(
        service: ManagerService = Depends(get_manager_service),
):
    return await service.shift_history()

