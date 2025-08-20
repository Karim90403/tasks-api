from fastapi import APIRouter, Depends, status

from core.dependencies import get_current_user
from schemas.user import UserInDB
from services.foreman_service import ForemanService, get_foreman_service

router = APIRouter(prefix="/api/foreman", tags=["foreman"])


@router.get("/projects", status_code=status.HTTP_200_OK)
async def get_projects(
    foreman_id: str,
    service: ForemanService = Depends(get_foreman_service),
    current_user: UserInDB = Depends(get_current_user),
):
    return await service.list_projects(foreman_id)


@router.get("/tasks", status_code=status.HTTP_200_OK)
async def get_tasks(
    foreman_id: str,
    service: ForemanService = Depends(get_foreman_service),
    current_user: UserInDB = Depends(get_current_user),
):
    return await service.list_tasks(foreman_id)
