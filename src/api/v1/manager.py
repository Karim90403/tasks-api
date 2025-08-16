from fastapi import APIRouter, Depends, status

from services.manager_service import ManagerService, get_manager_service

router = APIRouter(prefix="/api/manager", tags=["manager"])


@router.get("/projects", status_code=status.HTTP_200_OK)
async def get_projects(service: ManagerService = Depends(get_manager_service)):
    return await service.list_projects()


@router.get("/tasks", status_code=status.HTTP_200_OK)
async def get_tasks(service: ManagerService = Depends(get_manager_service)):
    return await service.list_tasks()
